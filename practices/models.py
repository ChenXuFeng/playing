'''
Time       :   2023-03
Author     :   ChenXuFeng <xu.sz@outlook.com> 
Describe   :   
'''

from django.db import models


class DockerImages(models.Model):
    """docker镜像"""
    imageid = models.CharField('镜像ID', max_length=64, unique=True)
    name = models.CharField('镜像名称', max_length=64)
    cport = models.IntegerField('容器端口')
    notes = models.CharField('说明', max_length=2048)
    create_at = models.DateTimeField('创建时间', auto_now_add=True)
    modify_time = models.DateTimeField('修改时间', auto_now=True)


class DockerContainers(models.Model):
    """docker容器"""
    image = models.ForeignKey(DockerImages, on_delete=models.PROTECT)
    name = models.CharField('名称', max_length=256)
    uname = models.CharField('账号', max_length=32)
    cid = models.CharField('容器ID', max_length=32)
    qid = models.IntegerField('题库ID')
    # status：0 运行中 1 正常关闭 2 超时关闭
    status = models.SmallIntegerField('状态')
    hostport = models.IntegerField('主机端口')
    port = models.IntegerField('容器端口')
    flag = models.CharField(max_length=128, default='', blank=True, null=True)
    create_at = models.DateTimeField('创建时间', auto_now_add=True)
