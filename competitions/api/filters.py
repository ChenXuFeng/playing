'''
Date       :   2023-02
Author     :   ChenXuFeng <xu.sz@outlook.com> 
Describe   :    过滤器   
'''

import django_filters

from ..models import AnswerRecords, Competitions


class CompetitionFilters(django_filters.rest_framework.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    date = django_filters.DateFromToRangeFilter(method='_date_range')

    def _date_range(self, qs, name, value):
        return qs.filter(starttime__range=(value.start,value.stop)).all()
    class Meta:
        model = Competitions
        fields = ()


class AnswerRecordFilters(django_filters.rest_framework.FilterSet):

    def filter_queryset(self, queryset):
        user = self.queryset.user
        queryset = queryset[0]
        return super().filter_queryset(queryset)

    class Meta:
        model = AnswerRecords
        fields = ()