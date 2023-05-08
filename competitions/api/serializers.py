'''
Date       :   2023-02
Author     :   ChenXuFeng <xu.sz@outlook.com> 
Describe   :    序列化器   
'''

from django.utils import timezone
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from accounts.api.serializers import GroupSerializer
from accounts.models import Group
from questions.api.serializers import QuestionSerializers
from questions.models import Questions

from ..models import AnswerRecords, Competitions, WriteUP


class CompetitionSerizlizers(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    gnames = serializers.SerializerMethodField()
    qs_count = serializers.SerializerMethodField()
    gs_count = serializers.SerializerMethodField()

    def get_gnames(self, obj: Competitions):
        return obj.group_names

    def get_status(self, obj: Competitions):
        return obj.status

    def get_qs_count(self, obj: Competitions):
        return obj.qs_count

    def get_gs_count(self, obj: Competitions):
        return obj.gs_count

    def validate(self, data):
        now = timezone.localtime(timezone.now())
        s = data['starttime']
        if not self.partial:
            if s.date() < now.date():
                raise ValueError('不能为过去的时间安排赛事')
        e = data['endtime']
        if e <= s:
            raise ValueError('结束时间必须大于开始时间')
        if not self.partial:
            qs = Competitions.objects.all()
        else:
            qs = Competitions.objects.exclude(pk=self.instance.id)
        for q in qs:
            if all(
                [s >= q.starttime, s <= q.endtime]
            ) or all(
                [e >= q.starttime, e <= q.endtime]
            ):
                raise ValueError('赛事时间重叠，请检查')
        return data

    class Meta:
        model = Competitions
        exclude = ()
        extra_kwargs = {
            'groups': {'write_only': True},
            'questions': {'write_only': True}
        }


class CompetitionSimepleSerizlizers(serializers.ModelSerializer):

    class Meta:
        model = Competitions
        exclude = ('groups', 'questions')


class CompetitionQuestionSerizlizers(serializers.Serializer):
    # 序列化模型字段，需要加上read_only字段
    cid = CompetitionSimepleSerizlizers(read_only=True, many=False)
    qs = QuestionSerializers(read_only=True, many=True)

    def to_internal_value(self, data):
        r = {
            'cid': None,
            'qs': []
        }
        if Competitions.objects.filter(pk=data['cid']).exists():
            c = Competitions.objects.get(pk=data['cid'])
            r['cid'] = c
        else:
            raise ValueError(f'cid: {data["cid"][0]} 未找到')
        # request.data 默认为JSON格式
        # fromdata请使用： qs = data.getlist('qs')
        qs = data['qs']
        r['qs'] = Questions.objects.filter(pk__in=qs)
        return r


class CompetitionGroupSerizlizers(serializers.Serializer):
    # 序列化模型字段，需要加上read_only字段
    cid = CompetitionSimepleSerizlizers(read_only=True, many=False)
    gs = GroupSerializer(read_only=True, many=True)

    def to_internal_value(self, data):
        r = {
            'cid': None,
            'gs': []
        }
        if Competitions.objects.filter(pk=data['cid']).exists():
            c = Competitions.objects.get(pk=data['cid'])
            r['cid'] = c
        else:
            raise ValueError(f'cid: {data["cid"][0]} 未找到')
        # request.data 默认为JSON格式
        # fromdata请使用： qs = data.getlist('qs')
        qs = data['gs']
        r['gs'] = Group.objects.filter(pk__in=qs)
        return r


class AnserRecordSerizlizers(serializers.ModelSerializer):

    def validate_competition(self, value: Competitions):
        """验证赛事状态"""
        if value.status != 2:
            raise serializers.ValidationError('赛事未开始或已结束')
        return value

    def validate(self, data):
        # 验证试题是否和赛事绑定
        if data['question'] not in data['competition'].questions.all():
            raise serializers.ValidationError('试题未找到')
        # 验证答题人是否参与赛事
        if data['respondent'].group not in data['competition'].groups.all():
            raise serializers.ValidationError('赛事未找到')
        return data

    class Meta:
        model = AnswerRecords
        exclude = ()
        validators = [
            UniqueTogetherValidator(
                queryset=AnswerRecords.objects.all(),
                fields=['competition', 'question', 'gid'],
                message='重复答题'
            )
        ]


class AnserRecordListSerializers(serializers.ModelSerializer):
    question = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field='topic'
    )
    respondent = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field='username'
    )
    competition = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field='name'
    )

    class Meta:
        model = AnswerRecords
        exclude = ()


class WUSerializers(serializers.ModelSerializer):
    file = serializers.SerializerMethodField()
    size = serializers.SerializerMethodField()

    def get_file(self, obj) -> str:
        return obj.uuid.hex

    def get_size(self, obj) -> int:
        return obj.size

    def validate(self, data):
        data = super().validate(data)
        if data.get('respondent') != self.root.context['request'].user:
            raise ValueError('无权限')
        return data

    def create(self, validated_data):
        validated_data.update(name=validated_data['files'].name)
        validated_data.update(gid=validated_data['respondent'].group.id)
        return super().create(validated_data)

    class Meta:
        model = WriteUP
        exclude = ('uuid',)
        extra_kwargs = {
            'files': {'write_only': True},
        }


class WUReadOnlySerializers(serializers.ModelSerializer):
    file = serializers.SerializerMethodField()
    size = serializers.SerializerMethodField()
    respondent = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field='username'
    )
    competition = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field='name'
    )

    def get_file(self, obj) -> str:
        return obj.uuid.hex

    def get_size(self, obj) -> int:
        return obj.size

    class Meta:
        model = WriteUP
        exclude = ('uuid',)
        extra_kwargs = {
            'files': {'write_only': True},
        }
