'''
Date       :   2023-02
Author     :   ChenXuFeng <xu.sz@outlook.com> 
Describe   :   
'''


from typing import List

from django.contrib.auth.password_validation import \
    validate_password as django_validate_password
from django.core.exceptions import PermissionDenied, ValidationError
from rest_framework import serializers
from rest_framework.exceptions import ValidationError as RESTValidationError

from ..models import Group, Permissions, Roles, User


class PermisSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permissions
        exclude = ()


class RoleListSerializer(serializers.ModelSerializer):
    ps = PermisSerializer(many=True, read_only=True)

    class Meta:
        model = Roles
        exclude = ('is_internal','level')

class RolesSerializer(serializers.ModelSerializer):

    class Meta:
        model = Roles
        exclude = ('is_internal','level')

class RolesAllSerializer(serializers.ModelSerializer):

    class Meta:
        model = Roles
        fields = ('id','name')


class GroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = Group
        exclude = ('level',)

class GroupAllSerizlizer(GroupSerializer):

    class Meta:
        model = Group
        fields = ('id','name')

class UserListSerializer(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField()
    permiss = serializers.SerializerMethodField()
    group = serializers.SlugRelatedField(
        many = False,
        read_only = True,
        slug_field= 'pk'
    )
    group_name = serializers.SerializerMethodField()
    roles_name = serializers.SerializerMethodField()
    icon = serializers.SerializerMethodField()

    def get_group_name(self, obj):
        return obj.group.name if obj.group else ''
    
    def get_roles_name(self,obj):
        return obj.roles.first().name if obj.roles.first() else ''

    def get_icon(self, obj):
        return obj.icons

    def get_roles(self, obj: User) -> List[str]:
        return obj.roles.first().id if obj.roles.first() else None
    
    def get_permiss(self, obj)->list[str]:
        return obj.p_labels

    class Meta:
        model = User
        exclude = ('is_staff', 'is_superuser', 'last_login', 'is_active', 'password')


class UserSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        max_length=35,
        min_length=2,
        error_messages = {
        'invalid': '值无效',
        'blank': '不能为空',
        'max_length': '最多 {max_length} 字符',
        'min_length': '至少 {min_length} 字符',
    }
        )
    username = serializers.CharField(max_length=32,min_length=2,error_messages = {
        'invalid': '值无效',
        'blank': '不能为空',
        'max_length': '最多 {max_length} 字符',
        'min_length': '至少 {min_length} 字符',
    })
    password = serializers.CharField(max_length=32,min_length=8, write_only=True,error_messages = {
        'invalid': '值无效',
        'blank': '不能为空',
        'max_length': '最多 {max_length} 字符',
        'min_length': '至少 {min_length} 字符',
    })
    allow_change_field = ('name', 'phone', 'roles', 'group', 'email', 'icon', 'notes')
    

    def create(self, validated_data):
        try:
            django_validate_password(validated_data.get('password', ''))
        except ValidationError as e:
            raise RESTValidationError(e)
        if User.objects.filter(username=validated_data['username']).exists():
            raise RESTValidationError('账号已存在')
        instance = super().create(validated_data)
        instance.set_password(validated_data.get('password'))
        instance.save()
        return instance

    def update(self, instance, validated_data):
        """
        表单字段包含oldPW、newPW认为是修改密码，其它字段将被忽略。
        反之认为是修改其它允许修改的信息，self.allow_change_field。
        """
        new_pw = self.initial_data.get('new_pw', '')
        old_pw = self.initial_data.get('old_pw', '')
        current_login_user = self.context.get('request').user
        if new_pw and old_pw:
            # 修改密码
            self._patch_pw(instance, current_login_user, new_pw, old_pw)
        else:
            # 修改其它信息
            self._patch_other(instance, current_login_user, validated_data)
        return instance

    def _patch_pw(self, instance, current_user, new_pw: str, old_pw: str):
        try:
            django_validate_password(new_pw)
        except ValidationError as e:
            raise RESTValidationError(e)

        if not current_user.is_superuser:
            if current_user != instance:
                raise PermissionDenied()
        if not instance.check_password(old_pw):
            raise RESTValidationError(['密码错误'])
        instance.set_password(new_pw)
        instance.save()
    
    def _patch_other(self, instance, current_user, validated_data):
        allow_fields = set(self.allow_change_field) & set(
            validated_data.keys())
        data = {key: validated_data[key] for key in allow_fields}
        super().update(instance, data)

    def validate_roles(self, value):
        if not isinstance(value, list):
            value = [value]
        return value
    class Meta:
        model = User
        extra_kwargs = {
            'roles': {'write_only':True}
        }
        exclude = ['is_staff', 'is_superuser', 'last_login', 'is_active']


class AllUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'name')


class UsernameAccountSerializer(serializers.Serializer):
    """账号校验"""
    username = serializers.CharField(write_only=True,label='账号', max_length=32,min_length=2,error_messages = {
        'invalid': '值无效',
        'blank': '不能为空',
        'max_length': '最多 {max_length} 字符',
        'min_length': '至少 {min_length} 字符',
    })


class PWValidateSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)

    def validate_password(self, v):
        try:
            django_validate_password(v)
            return v
        except ValidationError as e:
            raise RESTValidationError(e)
