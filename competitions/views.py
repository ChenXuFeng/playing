'''
Date       :   2023-02
Author     :   ChenXuFeng <xu.sz@outlook.com> 
Describe   :   
'''
import random
from typing import OrderedDict

from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.views import APIView

from accounts.api.permissions import AdminPermission
from accounts.api.serializers import GroupSerializer
from common.calculator import curve, get_increment_point
from common.file_service import generate_response
from practices.models import DockerContainers
from questions.api.filters import QuestionFiltersV2
from questions.api.serializers import (EntryQuestionsSerializers,
                                       QuestionListSerializers)

from .api.filters import AnswerRecordFilters, CompetitionFilters
from .api.serializers import (AnserRecordListSerializers,
                              AnserRecordSerizlizers,
                              CompetitionGroupSerizlizers,
                              CompetitionQuestionSerizlizers,
                              CompetitionSerizlizers, WUReadOnlySerializers,
                              WUSerializers)
from .models import (AnswerRecords, Competitions, WriteUP,
                     get_active_competition)


class CompetitionLC(generics.ListCreateAPIView):
    queryset = Competitions.objects.all()
    serializer_class = CompetitionSerizlizers
    filterset_class = CompetitionFilters
    permission_classes = [AdminPermission]


class CompetitionRUD(generics.RetrieveUpdateDestroyAPIView):
    queryset = Competitions.objects.all()
    serializer_class = CompetitionSerizlizers
    permission_classes = [AdminPermission]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class CompetitionQuestions(generics.ListAPIView):
    queryset = Competitions.objects.all()
    serializer_class = QuestionListSerializers
    filterset_class = QuestionFiltersV2
    permission_classes = [AdminPermission]

    def list(self, request, *args, **kwargs):
        cid = request.query_params.get('cid', None)
        if not cid:
            raise ValueError('无效参数')
        instance = Competitions.objects.get(
            pk=int(request.query_params['cid']))
        queryset = instance.questions.all()
        queryset = self.filter_queryset(queryset)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = QuestionListSerializers(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = QuestionListSerializers(queryset, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = CompetitionQuestionSerizlizers(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.validated_data['cid']
        qs = serializer.validated_data['qs']
        instance.questions.add(*qs)
        return Response()

    def delete(self, request, *args, **kwargs):
        serializer = CompetitionQuestionSerizlizers(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.validated_data['cid']
        qs = serializer.validated_data['qs']
        instance.questions.remove(*qs)
        return Response()


class CompetitionGroups(generics.ListAPIView):
    queryset = Competitions.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [AdminPermission]

    def list(self, request, *args, **kwargs):
        cid = request.query_params.get('cid', None)
        if not cid:
            raise ValueError('无效参数')
        instance = Competitions.objects.get(
            pk=int(request.query_params['cid']))
        queryset = instance.groups.all()
        queryset = self.filter_queryset(queryset)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = GroupSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = GroupSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = CompetitionGroupSerizlizers(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.validated_data['cid']
        gs = serializer.validated_data['gs']
        instance.groups.add(*gs)
        return Response()

    def delete(self, request, *args, **kwargs):
        serializer = CompetitionGroupSerizlizers(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.validated_data['cid']
        gs = serializer.validated_data['gs']
        instance.groups.remove(*gs)
        return Response()


class AnswerRecordLC(generics.ListCreateAPIView):
    queryset = AnswerRecords.objects.all()
    serializer_class = AnserRecordSerizlizers
    filterset_calss = AnswerRecordFilters

    @staticmethod
    def base_scoring(ctx) -> int:
        qs = ctx['question']
        user = ctx['respondent']
        match qs.types:
            case 1:  # 多选
                answer_set = set(qs.answer.values_list('value', flat=True))
                if set(ctx['answer']) == answer_set:
                    return qs.score
            case 0 | 2 | 4:  # 单选、静态flag、动态、是非题
                answer = qs.answer.first()
                if str(ctx['answer'][0]) == answer.value:
                    return qs.score
            case 3:
                dc = DockerContainers.objects.filter(qid=qs.id, name__startswith=user.username).last()
                if str(ctx['answer'][0]) == dc.flag:
                    return qs.score
        return 0

    @staticmethod
    def _calculator(score: int, count: int) -> int:
        """动态分数、额外奖励"""
        if count <= 3:
            # 额外奖励
            return get_increment_point(score, count)
        else:
            # 动态分数
            return curve(score, count)

    def create(self, request, *args, **kwargs):
        """答题提交"""
        # request.data.update(gid=request.user.group.id) #  QueryDict instance is immutable
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # 当前用户和“答题人”绑定，防止恶意提交数据
        if self.request.user != serializer.validated_data['respondent']:
            return Response(data='未知错误', status=status.HTTP_400_BAD_REQUEST)
        # 存库前插入自定义数据
        serializer.validated_data.update(gid=request.user.group.id)
        cpt = serializer.validated_data['competition']
        qs = serializer.validated_data['question']
        score = self.base_scoring(serializer.validated_data)
        if score and qs.types in [2, 3]:
            # 额外加成或动态分数
            count = AnswerRecords.objects.filter(
                competition=cpt, question=qs, score__gt=0).count()
            score = self._calculator(score, count)
        serializer.validated_data.update(score=score)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class Entry(APIView):
    """参赛"""

    def get(self, request, *args, **kwargs):
        """赛事基本信息"""
        if not request.user.group:
            raise ValueError('非法访问')
        group = request.user.group
        competi = get_active_competition()
        if not competi:
            return Response('无活动赛事')
        if group not in competi.groups.all():
            raise ValueError('非法访问')
        serializer = CompetitionSerizlizers(instance=competi)
        return Response(data=serializer.data)


class EntryResource(generics.ListAPIView):
    """参赛资源：赛题、答题记录"""
    filterset_class = QuestionFiltersV2
    RS = ['qs', 'records']

    def get(self, request, *args, **kwargs):
        """赛题资源、已答记录"""
        t = kwargs['types']
        if t in self.RS:
            method = getattr(self, t, None)
            if not method:
                raise ValueError('服务器错误')
            return method(request)
        raise ValueError('未找到')

    @staticmethod
    def random_answers(data: list[OrderedDict]):
        for d in data:
            d['answers'] = random.sample(
                d['answers'], k=len(d['answers']))

    def qs(self, request):
        """赛题"""
        competi = get_active_competition()
        if not compile:
            raise ValueError('无活动赛事')
        group = request.user.group
        if group not in competi.groups.all():
            raise ValueError('非法访问')
        records = AnswerRecords.objects.filter(
            gid=group.id, competition=competi)
        rid = [r.question.id for r in records]
        qs = competi.questions.exclude(pk__in=rid).all()
        qs = self.filter_queryset(qs)
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = EntryQuestionsSerializers(page, many=True)
            self.random_answers(serializer.data)
            return self.get_paginated_response(serializer.data)
        serializer = EntryQuestionsSerializers(qs, many=True)
        return Response(serializer.data)

    def records(self, request):
        """答题记录"""
        competi = get_active_competition()
        if not compile:
            raise ValueError('无活动赛事')
        group = request.user.group
        if group not in competi.groups.all():
            raise ValueError('非法访问')
        records = AnswerRecords.objects.filter(
            respondent=request.user, competition=competi)
        page = self.paginate_queryset(records)
        if page is not None:
            serializer = AnserRecordListSerializers(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = AnserRecordListSerializers(records, many=True)
        return Response(serializer.data)


class WriteUpLC(generics.ListCreateAPIView):
    """ 新增、列表 """
    serializer_class = WUSerializers
    queryset = WriteUP.objects.all()

    def list(self, request, *args, **kwargs):
        cid = request.query_params.get('cid', 0)
        c = None
        if cid != 0:
            if not Competitions.objects.filter(pk=cid).exists():
                raise ValueError('cid未找到')
            else:
                c = Competitions.objects.get(pk=cid)
        queryset = self.filter_queryset(self.get_queryset())
        competi = get_active_competition()
        if not request.user.is_superuser:
            if request.user.r_names[0] == '参赛队伍':
                queryset = queryset.filter(
                    competition=competi, respondent=request.user)
            if request.user.r_names[0] == '平台管理员':
                queryset = queryset.filter(competition=c)
        else:
            queryset = queryset.filter(competition=c or competi)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = WUReadOnlySerializers(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = WUReadOnlySerializers(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            if e.detail.get('non_field_errors', None):
                raise ValueError('重复提交')
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class WPDownload(APIView):
    queryset = WriteUP.objects.all()

    def get(self, request, fid, document_root=None):
        obj = get_object_or_404(self.queryset.all(), uuid=fid)
        return generate_response(obj.files.path, obj.name)
