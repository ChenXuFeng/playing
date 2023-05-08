'''
Date       :   2023-02
Author     :   ChenXuFeng <xu.sz@outlook.com> 
Describe   :   
'''

from rest_framework import generics

from questions.api.permissions import QuestionsPermission

from .api.serializers import DockerImageListSerializers, DockerImageSerializers
from .models import DockerImages


class DockerImagesLC(generics.ListCreateAPIView):
    queryset = DockerImages.objects.all()
    serializer_class = DockerImageSerializers
    permission_classes = [QuestionsPermission]


class DockerImagesRUD(generics.RetrieveUpdateDestroyAPIView):
    queryset = DockerImages.objects.all()
    serializer_class = DockerImageSerializers
    permission_classes = [QuestionsPermission]


class DockerImagesList(generics.ListAPIView):
    _paginator = None
    queryset = DockerImages.objects.all()
    serializer_class = DockerImageListSerializers
    permission_classes = [QuestionsPermission]