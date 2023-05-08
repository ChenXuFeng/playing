'''
Time       :   2023-03
Author     :   ChenXuFeng <xu.sz@outlook.com> 
Describe   :   
'''

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from competitions.models import Competitions
from practices.api.serializers import DockerImageSerializers

from ..models import Answer, Answers, Attachments, Clasf, Questions


class ClasfSerializer(serializers.ModelSerializer):

    class Meta:
        model = Clasf
        exclude = ('')

class ClasfListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Clasf
        exclude = ('parent', 'create_at', 'modify_time') 


class QsAttachmentSerializers(serializers.ModelSerializer):
    file = serializers.SerializerMethodField()
    size = serializers.SerializerMethodField()

    def get_file(self, obj: Attachments) -> str:
        return obj.uuid.hex

    def get_size(self, obj: Attachments) -> int:
        return obj.size
    class Meta:
        model = Attachments
        exclude = ('uuid',)
        extra_kwargs = {
            'files': {'write_only': True},
        }

class AnswersUpdataSerializer(serializers.ModelSerializer):

    class Meta:
        model = Answers
        fields = ('value',)


class AnswerUpdataSerializer(serializers.ModelSerializer):

    class Meta:
        model = Answer
        fields = ('value',)

class AnswersSerializers(serializers.ModelSerializer):

    class Meta:
        model = Answers
        exclude = ()


class AnswerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Answer
        exclude = ()



class QuestionSerializers(serializers.ModelSerializer):
    notes = serializers.CharField(max_length=1024, default='')
    en = serializers.BooleanField(default=True)
    answers = serializers.ListField(
        write_only=True,
        allow_empty=True,
        required = False,
        child = serializers.CharField(max_length=512),
        error_messages= {
        'not_a_list': '应该是一个列表，不是 "{input_type}"',
        'empty': '列表不能为空',
        'min_length': '最小长度 {min_length} ',
        'max_length': '最大长度 {max_length} '
        }
    ) 
    answer = serializers.ListField(
        write_only=True,
        allow_empty=True,
        required = False,
        child= serializers.CharField(max_length=512),
        error_messages= {
        'not_a_list': '应该是一个列表，不是 "{input_type}"',
        'empty': '列表不能为空',
        'min_length': '最小长度 {min_length} ',
        'max_length': '最大长度 {max_length} '
        }
    )

    attaches = serializers.ListField(
        required=False,
        allow_empty=True,
        max_length=3,
        child= serializers.FileField(),
        error_messages= {
        'not_a_list': '应该是一个列表，不是 "{input_type}"',
        'empty': '列表不能为空',
        'min_length': '最小长度 {min_length} ',
        'max_length': '最大长度 {max_length} '
        }
    )

    @staticmethod
    def _needs(attrs):
        if not attrs.get('answers', False):
            raise ValueError('单选题，必须有4个答项和1个答案')
        if not attrs.get('answer', False):
            raise ValueError('单选题，必须有4个答项和1个答案')

    def validate(self, attrs):
        super().validate(attrs)
        types = attrs.get('types')
        match types:
            case 0: # 单选
                self._needs(attrs)
                if not all(
                    [
                        len(set(attrs.get('answers'))) == 4,
                        len(attrs.get('answer')) == 1
                    ]
                ):
                    raise ValueError('单选题，必须有4个答项(不能重复),1个答案')
            case 1: # 多选
                self._needs(attrs)
                if not all(
                    [
                        len(set(attrs.get('answers'))) == 4,
                        len(set(attrs.get('answer'))) > 1
                    ]
                ):
                    raise ValueError('多选题，必须有4个答项(不能重复),2～4个答案')
            case 2: # 静态flag
                attrs.pop('answers', None)
                answer = attrs.get('answer', [])
                if len(answer) != 1:
                    raise ValueError('答案是必填项')
            case 3: # 动态flag
                attrs.pop('answers', None)
            case 4: # 是非题
                self._needs(attrs)
                if not all(
                    [
                        len(set(attrs.get('answers'))) == 2,
                        len(set(attrs.get('answer'))) == 1
                    ]
                ):
                    raise ValueError('是非题，必须有2个答项(不能重复),1个答案')
        # raise ValueError('debug, PASS')
        return attrs

    def create(self, validated_data):
        answers = validated_data.pop('answers', None)
        answer = validated_data.pop('answer', None)
        attrs = validated_data.pop('attaches', [])
        instance = super().create(validated_data)
        if answers:
            Answers.objects.bulk_create(
                [Answers(qs=instance, value = ans) for ans in answers]
            )
        if answer:
            Answer.objects.bulk_create(
                [Answer(qs=instance, value=an) for an in answer]
            )
        for atr in attrs:
            ats = Attachments(question=instance,files=atr,name=atr.name)
            ats.save()
        return instance
    class Meta:
        model = Questions
        exclude = ('is_delete',)

class QuestionListSerializers(serializers.ModelSerializer):
    clasf = ClasfListSerializer(read_only=True)
    attaches = QsAttachmentSerializers(many=True, read_only=True)
    answers = AnswersSerializers(many=True, read_only=True)
    answer = AnswerSerializer(many=True, read_only=True)
    docker_images = DockerImageSerializers(read_only=True)
    class Meta:
        model = Questions
        exclude = ()


class EntryQuestionsSerializers(serializers.ModelSerializer):
    clasf = ClasfListSerializer(read_only=True)
    attaches = QsAttachmentSerializers(many=True, read_only=True)
    answers = AnswersSerializers(many=True, read_only=True)
    docker_images = DockerImageSerializers(read_only=True)
    class Meta:
        model = Questions
        exclude = ()

class _CustomAnswersRelatedField(serializers.RelatedField):
    queryset = Answers.objects.all()

    def to_internal_value(self, data):
        if self.queryset.filter(pk=data['id']).exists():
            obj = self.queryset.get(pk=data['id'])
            if self.root.instance.answers.contains(obj):
                obj.value = data['value']
                obj.save()
                return obj
        raise ValidationError(f'{data["id"]} 未找到')


class _CustomAnswerRelatedField(serializers.RelatedField):
    queryset = Answer.objects.all()

    def to_internal_value(self, data):
        if self.queryset.filter(pk=data['id']).exists():
            obj = self.queryset.get(pk=data['id'])
            if self.root.instance.answer.contains(obj):
                obj.value = data['value']
                obj.save()
                return obj
        raise ValidationError(f'{data["id"]} 未找到')
        
class QuestionUpdateSerializers(serializers.ModelSerializer):
    answers = _CustomAnswersRelatedField(many=True)
    answer = _CustomAnswerRelatedField(many=True)
    class Meta:
        model = Questions
        fields = ('topic', 'clasf', 'notes','en', 'score', 'answers', 'answer', 'docker_images')


class StartContainerSerializers(serializers.Serializer):
    cid = serializers.IntegerField()
    qid = serializers.IntegerField()

    def validate_cid(self, v):
        try:
            c = Competitions.objects.get(pk=v)
            return c
        except Exception as e:
            raise ValidationError('cid未找到')
        
    def validate_qid(self, v):
        try:
            q = Questions.objects.get(pk=v)
            return q
        except Exception as e:
            raise ValidationError('qid未找到')
