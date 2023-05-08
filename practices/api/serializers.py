'''
Date       :   2023-03
Author     :   ChenXuFeng <xu.sz@outlook.com> 
Describe   :   
'''

import logging

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from ..models import DockerContainers, DockerImages

logger = logging.getLogger('django.server')

class DockerContainerSerializers(serializers.Serializer):

    image_id = serializers.UUIDField()
    image_name = serializers.CharField(max_length=35)


class DockerImageSerializers(serializers.ModelSerializer):

    def validate_imageid(self, v):
        try:
            from dockerd import dockerd
            dockerd.images.get(v)
            return v
        except:
            logger.error('docker服务器连接失败')
            raise ValidationError(detail='服务器或值错误')
        
    
    class Meta:
        model = DockerImages
        exclude = ()


class DockerImageListSerializers(serializers.ModelSerializer):

    class Meta:
        model = DockerImages
        fields = ('id','name')