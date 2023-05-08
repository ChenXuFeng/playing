'''
Time       :   2023-02
Author     :   ChenXuFeng <xu.sz@outlook.com> 
Describe   :   
'''

import uuid

from django.db import models

from practices.models import DockerImages


def upload_path(instance, filename):
    return f'questionAttachments/{instance.question.id}/{uuid.uuid4().hex}/{filename}'

class Clasf(models.Model):
    """题库分类"""
    name = models.CharField('名称',max_length=32, unique=True)
    parent = models.ForeignKey('self', on_delete=models.PROTECT, blank=True, null=True, related_name='children',
                               verbose_name='上级', default=None)
    notes = models.TextField('备注', max_length=1024, blank=True, null=True)
    create_at = models.DateTimeField('创建时间', auto_now_add=True)
    modify_time = models.DateTimeField('修改时间', auto_now=True)



class Questions(models.Model):
    """题库"""
    topic = models.CharField('题目',max_length=512, unique=True)
    clasf = models.ForeignKey(Clasf, verbose_name='分类', blank=True, null=True, related_name='questions', on_delete=models.SET_NULL)
    # types: 0 单选，1 多选，2 静态flag 3 动态flag 4 是非
    types = models.SmallIntegerField('类型')
    notes = models.TextField('备注', max_length=1024, default='',null=True)
    en = models.BooleanField('启用', default=True)
    is_delete = models.BooleanField('删除', default=False)
    score = models.SmallIntegerField('分数')
    docker_images = models.ForeignKey(DockerImages, verbose_name='docker镜像', null=True, related_name='qs', on_delete=models.SET_NULL)
    create_at = models.DateTimeField('创建时间', auto_now_add=True)
    modify_time = models.DateTimeField('修改时间', auto_now=True)

    class Meta:
        ordering = ['-create_at']

class Answers(models.Model):
    """题目答项"""
    qs = models.ForeignKey(
        Questions, 
        blank=True,
        verbose_name='题库', 
        related_name='answers', 
        on_delete=models.CASCADE
        )
    value = models.CharField('值', max_length=512)

    class Meta:
        unique_together = [['qs', 'value']]


class Answer(models.Model):
    """题目答案"""
    qs = models.ForeignKey(
        Questions, 
        blank=True,
        verbose_name='题库', 
        related_name='answer', 
        on_delete=models.CASCADE
        )
    value = models.CharField('值', max_length=512)

    class Meta:
        unique_together = [['qs', 'value']]



class Attachments(models.Model):
    """附件"""
    question = models.ForeignKey(
        Questions, verbose_name='题库', on_delete=models.CASCADE, related_name='attaches')
    files = models.FileField(upload_to=upload_path)
    name = models.CharField(max_length=255)
    uuid = models.UUIDField(default=uuid.uuid4)
    notes = models.TextField('备注', max_length=1024, blank=True, null=True)
    create_at = models.DateTimeField('创建时间', auto_now_add=True)
    modify_time = models.DateTimeField('修改时间', auto_now=True)

    @property
    def size(self):
        try:
            size = self.files.size
            return size
        except FileNotFoundError:
            return 0