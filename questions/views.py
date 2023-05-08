'''
Time       :   2023-03
Author     :   ChenXuFeng <xu.sz@outlook.com> 
Describe   :   
'''


import logging
import random
from itertools import chain

from django import forms
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.api.permissions import AdminPermission
from common.file_service import generate_response
from practices.models import DockerContainers

from .api.filters import QuestionFilters
from .api.permissions import QuestionsPermission
from .api.serializers import (AnswerSerializer, AnswersUpdataSerializer,
                              AnswerUpdataSerializer, ClasfSerializer,
                              QsAttachmentSerializers, QuestionListSerializers,
                              QuestionSerializers, QuestionUpdateSerializers,
                              StartContainerSerializers)
from .models import Answer, Answers, Attachments, Clasf, Questions

logger = logging.getLogger("django.server")


class ClasfLC(generics.ListCreateAPIView):
    queryset = Clasf.objects.all()
    serializer_class = ClasfSerializer


class ClasRUD(generics.RetrieveUpdateDestroyAPIView):
    queryset = Clasf.objects.all()
    serializer_class = ClasfSerializer
    permission_classes = [QuestionsPermission]


class AnswersUpdate(generics.UpdateAPIView):
    queryset = Answers.objects.all()
    serializer_class = AnswersUpdataSerializer
    permission_classes = [QuestionsPermission]


class AnswerUpdate(generics.UpdateAPIView):
    queryset = Answer.objects.all()
    serializer_class = AnswerUpdataSerializer
    permission_classes = [QuestionsPermission]


class AnswerCreate(generics.CreateAPIView):

    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer
    permission_classes = [QuestionsPermission]

    def perform_create(self, serializer):
        qs = serializer.validated_data['qs']
        if qs.types != 1:
            raise ValueError('非多选题不能增加答案')
        if qs.answer.count() == 4:
            raise ValueError('答案数量 超出限制')
        answers = qs.answers.values_list('value', flat=True)
        if serializer.validated_data['value'] not in answers:
            raise ValueError('非法 答案')
        serializer.save()


class AnswerDel(generics.DestroyAPIView):
    queryset = Answer.objects.all()
    serializer_class = AnswerUpdataSerializer
    permission_classes = [QuestionsPermission]

    def perform_destroy(self, instance):
        if instance.qs.types != 1:
            return
        if instance.qs.answer.count() == 1:
            return
        instance.delete()


class QuestionLC(generics.ListCreateAPIView):
    serializer_class = QuestionSerializers
    queryset = Questions.objects.filter(is_delete=False)
    filterset_class = QuestionFilters
    list_serializer_class = QuestionListSerializers
    permission_classes = [AdminPermission | QuestionsPermission]

    def get(self, request, *args, **kwargs):
        self.serializer_class = self.list_serializer_class
        return self.list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        serializer = self.list_serializer_class(
            serializer.instance)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=200, headers=headers)


class QuestionRUD(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = QuestionSerializers
    queryset = Questions.objects.filter(is_delete=False)
    permission_classes = [QuestionsPermission]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = QuestionListSerializers(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = QuestionUpdateSerializers(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        serializer = QuestionListSerializers(
            serializer.instance)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def perform_destroy(self, instance):
        instance.is_delete = True
        instance.save()


class QsAttrCreateView(generics.CreateAPIView):
    serializer_class = QsAttachmentSerializers
    queryset = Attachments.objects.all()
    permission_classes = [QuestionsPermission]

    def perform_create(self, serializer):
        qs = serializer.validated_data['question']
        # 仅flag题可以添加附件
        if qs.types not in [2, 3]:
            raise ValueError('非法操作')
        serializer.save()


class QsAttrDelView(generics.DestroyAPIView):
    serializer_class = QsAttachmentSerializers
    permission_classes = [QuestionsPermission]
    queryset = Attachments.objects.all()
    lookup_field = 'uuid'

    def perform_destroy(self, instance):
        if instance.question.types not in [2, 3]:
            raise ValueError('非法操作')
        instance.delete()


class QsAttrRetrieveView(generics.RetrieveAPIView):
    serializer_class = QsAttachmentSerializers
    queryset = Questions.objects.all()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance.attaches.all(), many=True)
        return Response(serializer.data)


class StartContainer(generics.GenericAPIView):
    """启动容器"""
    CONTAINER_STATUS = {
        'created': 0,
        'exited': 1,
        'timeout': 2
    }
    serializer_class = StartContainerSerializers

    @staticmethod
    def _match_competition(user, competition) -> bool:
        """检查赛事状态及用户是否参与该赛事"""
        if competition.status != 2:
            logger.error(f'赛事状态 {competition.status}')
            return False
        group_users = list(chain(*[g.users.all() for g in competition.groups.all()]))
        if user not in group_users:
            logger.error('用户和赛事不匹配')
            return False
        return True

    @staticmethod
    def _match_qs(qs, competition) -> bool:
        """检查赛题是否分配到赛事"""
        return qs in competition.questions.all() and qs.docker_images

    @staticmethod
    def is_running(name: str) -> bool:
        if DockerContainers.objects.filter(name=name, status=0).exists():
            return True
        return False

    @staticmethod
    def start_container(dockerd, name: str, port: str, imageid: str):
        _flag = ''.join(random.choices(['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'], k=6))
        container = dockerd.containers.run(
            imageid,
            name=name,
            detach=True,
            remove=True,
            ports={f'{port}/tcp': None},
            environment=[f"FLAG={_flag}"]
        )
        if container.status != 'created':
            container.reload()
        return container, _flag

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        if not all(
                [
                    self._match_competition(request.user, data['cid']),
                    self._match_qs(data['qid'], data['cid'])
                ]):
            logger.error(f'{self.__class__.__name__}：表单数据校验失败')
            return Response({'detail': '数据错误'}, status=200)
        try:
            from dockerd import dockerd
        except Exception as e:
            logger.error(e)
            raise Exception('服务器错误')
        docker_iamge = data['qid'].docker_images
        container_name = request.user.username + '_' + docker_iamge.name.replace('/', '_')
        if self.is_running(container_name):
            dc = DockerContainers.objects.get(name=container_name, cid=data['cid'].id, qid=data['qid'].id, status=0)
            data = {
                'dec': dc.image.notes,
                'uri': f"{settings.DOCKERD_HOST}:{dc.hostport}",
                'qid': dc.qid,
                'id': dc.id
            }
            return Response(data, status=200)
        container, flag = self.start_container(dockerd, container_name, str(docker_iamge.cport), docker_iamge.imageid)
        container_ports = dockerd.api.port(container.id, docker_iamge.cport)
        container_record = DockerContainers(
            image=docker_iamge,
            name=container_name,
            uname=request.user.username,
            cid=data['cid'].id,
            qid=data['qid'].id,
            status=self.CONTAINER_STATUS[container.status],
            hostport=int(container_ports[0]['HostPort']),
            port=docker_iamge.cport,
            flag=flag
        )
        container_record.save()
        return Response(
            {
                'dec': docker_iamge.notes,
                'uri': f"{settings.DOCKERD_HOST}:{container_record.hostport}",
                'qid': container_record.qid,
                'id': container_record.id
            },
            status=200
        )


class StopContainer(StartContainer):

    @staticmethod
    def stop_container(dockerd, name):
        c = dockerd.containers.get(name)
        c.stop()
        return c

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        if not all(
                [
                    self._match_competition(request.user, data['cid']),
                    self._match_qs(data['qid'], data['cid'])
                ]):
            logger.error(f'{self.__class__.__name__}：表单数据校验失败')
            return Response({'detail': '数据错误'}, status=200)
        try:
            from dockerd import dockerd
        except Exception as e:
            logger.error(e)
            raise Exception('服务器错误')
        container = DockerContainers.objects.filter(qid=data['qid'].id, status=0).exists()
        if not container:
            return Response({'detail': '操作成功'}, status=200)
        container = DockerContainers.objects.get(qid=data['qid'].id, status=0)
        if self.is_running(container.name):
            self.stop_container(dockerd, container.name)
            container.status = 1
            container.save()
            return Response({'detail': '操作成功'}, status=200)
        return Response({'detail': '操作成功'}, status=200)


class QuestionAttaches(APIView):
    queryset = Attachments.objects

    def get(self, request, fid, document_root=None):
        obj = get_object_or_404(self.queryset.all(), uuid=fid)
        return generate_response(obj.files.path, obj.name)


class QsForm(forms.ModelForm):

    class Meta:
        model = Questions
        exclude = []
