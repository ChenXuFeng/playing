'''
Date       :   2023-02
Author     :   ChenXuFeng <xu.sz@outlook.com> 
Describe   :   
'''

from django.urls import path
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView)

from ..views import (GroupAll, GroupCL, GroupRUD, PermisAll, PermisCL,
                     PermisRUD, PWValidateView, RolesAll, RolesCL, RolesRUD,
                     UserAll, UserCL, UsernameAccountView, UserRUD)

urlpatterns = [
    path('token', TokenObtainPairView.as_view()),
    path('token/refresh', TokenRefreshView.as_view()),
    path('permis', PermisCL.as_view()),
    path('permis/<int:pk>', PermisRUD.as_view()),
    path('permis/all', PermisAll.as_view()),
    path('roles', RolesCL.as_view()),
    path('role/<int:pk>', RolesRUD.as_view()),
    path('roles/all', RolesAll.as_view()),
    path('groups', GroupCL.as_view()),
    path('group/<int:pk>', GroupRUD.as_view()),
    path('group/all', GroupAll.as_view()),
    path('users', UserCL.as_view()),
    path('user/<str:pk>', UserRUD.as_view()),
    path('user/all', UserAll.as_view()),
    path('checkAccount', UsernameAccountView.as_view()),
    path('checkpw', PWValidateView.as_view())
]
