'''
Time       :   2023-02
Author     :   ChenXuFeng <xu.sz@outlook.com> 
Describe   :   
'''

from django.db.models import ProtectedError
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .api.filters import GroupFilters, UserFilters
from .api.permissions import AdminPermission
from .api.serializers import (AllUserSerializer, GroupAllSerizlizer,
                              GroupSerializer, PermisSerializer,
                              PWValidateSerializer, RoleListSerializer,
                              RolesAllSerializer, RolesSerializer,
                              UserListSerializer, UsernameAccountSerializer,
                              UserSerializer)
from .models import Group, Permissions, Roles, User


class PermisCL(generics.ListCreateAPIView):
    serializer_class = PermisSerializer
    queryset = Permissions.objects.all()
    filter_backends = (DjangoFilterBackend,)
    permission_classes = [AdminPermission]



class PermisRUD(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PermisSerializer
    queryset = Permissions.objects.all()
    permission_classes = [AdminPermission]


class PermisAll(generics.ListAPIView):
    _paginator = None
    serializer_class = PermisSerializer
    queryset = Permissions.objects.all()
    permission_classes = [AdminPermission]


class RolesAll(generics.ListAPIView):
    _paginator = None
    serializer_class = RolesAllSerializer
    queryset = Roles.objects.all()
    permission_classes = [AdminPermission]


class RolesCL(generics.ListCreateAPIView):
    serializer_class = RolesSerializer
    list_serializer_class = RoleListSerializer
    queryset = Roles.objects.all()
    filter_backends = (DjangoFilterBackend,)
    permission_classes = [AdminPermission]
    # filterset_class = RoleFilter

    def get(self, request, *args, **kwargs):
        self.serializer_class = self.list_serializer_class
        return self.list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        serializer = self.list_serializer_class(
            serializer.instance)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class RolesRUD(generics.RetrieveUpdateDestroyAPIView):
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']
    serializer_class = RolesSerializer
    queryset = Roles.objects.all()
    permission_classes = [AdminPermission]


class GroupAll(generics.ListAPIView):
    _paginator = None
    serializer_class =GroupAllSerizlizer
    queryset = Group.objects.all()
    permission_classes = [AdminPermission]


class GroupCL(generics.ListCreateAPIView):
    filter_backends = (DjangoFilterBackend,)
    serializer_class = GroupSerializer
    queryset = Group.objects.all()
    filterset_class = GroupFilters
    permission_classes = [AdminPermission]


class GroupRUD(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = GroupSerializer
    queryset = Group.objects.all()
    permission_classes = [AdminPermission]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ProtectedError:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'detail': '有关联数据，不能删除'})


class UserAll(generics.ListAPIView):
    _paginator = None
    serializer_class = AllUserSerializer
    queryset = User.objects.all()
    permission_classes = [AdminPermission]


class UserCL(generics.ListCreateAPIView):
    serializer_class = UserSerializer
    list_serializer_class = UserListSerializer
    queryset = User.objects.filter(is_superuser=False)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = UserFilters
    permission_classes = [AdminPermission]

    def get(self, request, *args, **kwargs):
        self.serializer_class = self.list_serializer_class
        return self.list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        serializer = self.list_serializer_class(
            serializer.instance)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class UserRUD(generics.RetrieveUpdateDestroyAPIView):
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']
    serializer_class = UserSerializer
    list_serializer_class = UserListSerializer
    queryset = User.objects.all()
    permission_classes = [AdminPermission]

    def get(self, request, *args, **kwargs):
        self.serializer_class = self.list_serializer_class
        return self.retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}
        serializer = self.list_serializer_class(instance)
        return Response(serializer.data)


class UsernameAccountView(generics.GenericAPIView):
    serializer_class = UsernameAccountSerializer
    queryset = User.objects

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result= User.objects.filter(username=serializer.validated_data.get('username')).exists()
        return Response(result, status=200)


class PWValidateView(APIView):
    """"""

    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = PWValidateSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return Response(None, status=status.HTTP_200_OK)