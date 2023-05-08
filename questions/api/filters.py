'''
Date       :   2023-03
Author     :   ChenXuFeng <xu.sz@outlook.com> 
Describe   :    过滤器   
'''

import django_filters

from ..models import Clasf, Questions


class QuestionFilters(django_filters.rest_framework.FilterSet):
    topic = django_filters.CharFilter(lookup_expr='icontains')
    clasf = django_filters.ModelChoiceFilter(queryset=Clasf.objects.all())
    cid = django_filters.CharFilter(method='_exclude_cid')

    def _exclude_cid(self, qs, name, value):
        return qs.exclude(cometitions__pk=value)

    class Meta:
        model = Questions
        fields = ('types',)


class QuestionFiltersV2(django_filters.rest_framework.FilterSet):
    topic = django_filters.CharFilter(lookup_expr='icontains')
    clasf = django_filters.ModelChoiceFilter(queryset=Clasf.objects.all())

    class Meta:
        model = Questions
        fields = ('types',)