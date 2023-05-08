'''
Date       :   2023-03
Author     :   ChenXuFeng <xu.sz@outlook.com> 
Describe   :   
'''

import django_filters

from ..models import Group, Roles, User


class UserFilters(django_filters.rest_framework.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    group = django_filters.ModelChoiceFilter(queryset=Group.objects.all())
    roles = django_filters.ModelChoiceFilter(queryset=Roles.objects.all())

    class Meta:
        model = User
        fields = ()


class GroupFilters(django_filters.rest_framework.FilterSet):
    cid = django_filters.CharFilter(method='_exclude_cid')

    def _exclude_cid(self, qs, name, value):
        return qs.exclude(cometitions__pk=value)