from django.db.models import Count, Sum
from django.utils import timezone
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from accounts.models import Group
from competitions.api.serializers import CompetitionSerizlizers
from competitions.models import (AnswerRecords, Competitions,
                                 get_active_competition)


class Stats(GenericAPIView):
    """大屏统计"""

    # base: 基本信息
    # gs:   队伍排行
    # qs:   答题动态
    # rate：队伍答题进度
    # trend: 答题趋势(态势)
    TYPE = ['base', 'gs', 'qs', 'rate', 'trend']

    def get(self, request, *args, **kwargs):
        t = kwargs['types']
        if t in self.TYPE:
            method = getattr(self, t, None)
            if not method:
                raise ValueError('服务器错误')
            competi = get_active_competition()
            if not competi:
                raise ValueError('无活动赛事')
            return method(request, competi)
        raise ValueError('未找到')

    def base(self, request, competi: Competitions):
        serializer = CompetitionSerizlizers(instance=competi)
        gs = competi.groups.all()
        hc = sum([g.users.count() for g in gs])
        data = dict(serializer.data)
        data.update(people_number=hc)
        return Response(data=data)

    def gs(self, request, competi: Competitions):
        records = AnswerRecords.objects.filter(competition=competi)
        gid_sum = records.values('gid').annotate(Sum('score'))[:10]
        # records.values('gid').annotate(Sum('score')).order_by('-score__sum')[:10]
        data = []
        for gs in gid_sum:
            g = Group.objects.get(pk=gs['gid'])
            data.append({'group': g.name, 'score_sum': gs['score__sum']})
        return Response(data=data)

    def qs(self, request, competi: Competitions):
        qs = AnswerRecords.objects.filter(competition=competi)[:10]
        data = []
        for q in qs:
            data.append(f'{q.respondent.name} 提交了 {q.question.topic}')
        return Response(data=data)

    def rate(self, request, competi: Competitions):
        recoreds = AnswerRecords.objects.filter(competition=competi)
        gid_count = recoreds.values('gid').annotate(Count('question'))
        data = []
        for gc in gid_count:
            g = Group.objects.get(pk=gc['gid'])
            data.append({'group': g.name, 'rate': (gc['question__count']/competi.questions.count())*100})
        return Response(data=data)

    def trend(self, request, competi: Competitions, duration=24):
        befor = timezone.localtime(timezone.now()) - timezone.timedelta(hours=duration)
        befor_records = AnswerRecords.objects.filter(competition=competi, create_at__lt=befor)
        records = AnswerRecords.objects.filter(competition=competi, create_at__gte=befor)
        gid_sum = AnswerRecords.objects.filter(competition=competi, score__gt=0).values('gid').annotate(Sum('score'))[:10]
        data = {}
        for gs in gid_sum:
            name = Group.objects.get(pk=gs['gid']).name
            packet_data = []
            p = befor_records.filter(gid=gs['gid']).aggregate(Sum('score'))['score__sum'] or 0
            for h in range(duration):
                this_time = records.filter(gid=gs['gid'], create_at__range=(
                    befor+timezone.timedelta(hours=h), befor + timezone.timedelta(hours=h+1)
                )
                )
                if not this_time:
                    packet_data.append(p)
                    continue
                this_sum = this_time.aggregate(Sum('score'))['score__sum']
                p += this_sum
                packet_data.append(p)
            data.update({name: packet_data})
        return Response(data=data)
