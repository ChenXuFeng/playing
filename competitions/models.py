'''
Time       :   2023-02
Author     :   ChenXuFeng <xu.sz@outlook.com> 
Describe   :   
'''

import uuid

from django.db import models
from django.utils import timezone

from accounts.models import Group, User
from questions.models import Questions


def upload_path(instance, filename):
    return f'competitionWriteup/{instance.respondent.id}/{filename}'

class Competitions(models.Model):
    """赛事"""
    name = models.CharField('名称', max_length=512, unique=True)
    groups = models.ManyToManyField(Group, verbose_name='队伍', blank=True, related_name='cometitions')
    questions = models.ManyToManyField(Questions, verbose_name='题库', blank=True, related_name='cometitions')
    notes = models.TextField('备注', max_length=1024, blank=True, null=True)
    starttime = models.DateTimeField('开始时间')
    endtime = models.DateTimeField('结束时间')
    create_at = models.DateTimeField('创建时间', auto_now_add=True)

    @property
    def status(self)->bool:
        """赛事状态"""
        now = timezone.localtime(timezone.now())
        if now < self.starttime:
            return 0    # 未开始
        elif now > self.endtime:
            return 1    # 已结束
        elif now >= self.starttime and now <= self.endtime:
            return 2    # 进行中

    @property    
    def group_names(self)->list[str]:
        """参数队伍名称"""
        return self.groups.values_list('name',flat=True)
    
    @property
    def qs_count(self)->int:
        """试题总数"""
        return self.questions.count()
    
    @property
    def gs_count(self)->int:
        """队伍总数"""
        return self.groups.count()
    
    class Meta:
        ordering = ['-create_at']
    

class AnswerRecords(models.Model):
    """赛事答题记录"""
    competition = models.ForeignKey(Competitions, on_delete=models.PROTECT)
    question = models.ForeignKey(Questions, verbose_name='题库', on_delete=models.PROTECT)
    respondent = models.ForeignKey(User, verbose_name='答题人', on_delete=models.PROTECT)
    gid = models.IntegerField('队伍id', null=True, blank=True)
    answer = models.JSONField('答案', default=list)
    result = models.BooleanField(blank=True, null=True)
    score = models.SmallIntegerField('分数', blank=True, null=True)
    notes = models.TextField('备注', max_length=10000, blank=True, null=True)
    handed = models.BooleanField('交卷', default=False)
    create_at = models.DateTimeField('创建时间', auto_now_add=True)
    modify_time = models.DateTimeField('修改时间', auto_now=True)

    class Meta:
        ordering = ['-create_at']


def get_active_competition():
    """获取已开始的赛事"""
    competi =  [c for c in Competitions.objects.all() if c.status ==2]
    if competi:
        return competi[0]
    return None


class WriteUP(models.Model):
    competition = models.ForeignKey(Competitions, on_delete=models.PROTECT)
    respondent = models.ForeignKey(User, verbose_name='答题人', on_delete=models.PROTECT)
    gid = models.IntegerField('队伍id', null=True, blank=True)
    notes = models.TextField('备注', max_length=10000, default='')
    files = models.FileField(upload_to=upload_path)
    name = models.CharField(max_length=255, default='')
    uuid = models.UUIDField(default=uuid.uuid4)
    create_at = models.DateTimeField('创建时间', auto_now_add=True)
    modify_time = models.DateTimeField('修改时间', auto_now=True)

    @property
    def size(self):
        try:
            size = self.files.size
            return size
        except FileNotFoundError:
            return 0
        
    class Meta:
        unique_together = [['competition', 'respondent']]