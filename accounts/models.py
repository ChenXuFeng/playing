'''
Time       :   2023-02
Author     :   ChenXuFeng <xu.sz@outlook.com> 
Describe   :   
'''

import base64
from functools import reduce
from typing import List
from uuid import uuid4

from django.contrib.auth.models import AbstractBaseUser, UserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.mail import send_mail
from django.db import models
from django.utils.translation import gettext_lazy as _


class Permissions(models.Model):
    label = models.CharField('名称', max_length=35, unique=True)
    value = models.CharField(max_length=35, unique=True)

    def __str__(self):
        return self.label


class Roles(models.Model):
    name = models.CharField('名称', max_length=15, unique=True)
    notes = models.CharField('备注', max_length=250, null=True, blank=True)
    ps = models.ManyToManyField(
        Permissions, verbose_name='权限', related_name='role', blank=True)
    level = models.SmallIntegerField('级别', default=0)
    is_internal = models.BooleanField(
        '内置角色', default=False, blank=True, null=True)
    create_at = models.DateTimeField('创建时间', auto_now_add=True)
    modify_time = models.DateTimeField('修改时间', auto_now=True)

    @property
    def ps_names(self) -> List[str]:
        return self.ps.values_list('label', flat=True)

    def __str__(self):
        return self.name


class Group(models.Model):
    name = models.CharField('名称', max_length=255, unique=True)
    icon = models.ImageField('图标', upload_to='accountIcons/', max_length=256, blank=True, null=True)
    level = models.SmallIntegerField('级别', default=0)
    notes = models.CharField('备注', max_length=1024, blank=True, null=True)
    create_at = models.DateTimeField('创建时间', auto_now_add=True)
    modify_time = models.DateTimeField('修改时间', auto_now=True)

class User(AbstractBaseUser):
    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        _("username"),
        max_length=32,
        unique=True,
        help_text=_(
            "必填，32个字符。 字母和数字混合，可以包含：@/./+/-/_ "
        ),
        validators=[username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )
    icon = models.ImageField('图标', upload_to='accountIcons/', max_length=256, blank=True,null=True, default='')
    email = models.EmailField(_("email address"), blank=True)
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    create_at = models.DateTimeField('创建时间', auto_now_add=True)
    is_superuser = models.BooleanField(
        _("superuser status"),
        default=False,
        help_text=_(
            "Designates that this user has all permissions without "
            "explicitly assigning them."
        ),
    )
    notes = models.CharField('备注', max_length=1024, default='')
    group = models.ForeignKey(Group, verbose_name='组', related_name='users', on_delete=models.PROTECT, blank=True, null=True)
    objects = UserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        swappable = "AUTH_USER_MODEL"

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)
    id = models.UUIDField('用户ID', primary_key=True,
                          default=uuid4, editable=False)
    name = models.CharField('昵称', max_length=35)
    phone = models.CharField('电话', max_length=35, unique=True)
    notes = models.TextField('备注', max_length=512, blank=True, null=True)
    roles = models.ManyToManyField(
        Roles, verbose_name='角色', related_name='user', blank=True)

    @property
    def r_names(self) -> List[str]:
        return list(self.roles.values_list('name', flat=True))

    @property
    def ps(self) -> List[str]:
        ps = [{p.value for p in r.ps.all()} for r in self.roles.all()]
        if ps:
            return list(reduce(lambda v, e: v | e, ps))
        return ps
    
    @property
    def p_labels(self)->list[str]:
        labels = [{p.label for p in r.ps.all()} for r in self.roles.all()]
        if labels:
            return list(reduce(lambda v, e: v | e, labels))
        return labels
    
    @property
    def icons(self) -> str:
        try:
            # with open(self.icon.file.name, 'rb') as f:
            #     encode = base64.b64encode(f.read())
            #     data = str(encode, 'utf8')
            
            encode = base64.b64encode(self.icon.read())
            data = str(encode, 'utf8')
            return 'data:image/jpeg;base64,'+data
        except Exception as e:
            return ''

    def __str__(self):
        return self.name
