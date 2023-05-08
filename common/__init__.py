import logging

from django.http.response import Http404
from rest_framework import exceptions
from rest_framework.response import Response
from rest_framework.views import exception_handler
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

logger = logging.getLogger("django.server")

__all__ = ('TokenSerializer', 'custom_exception_handler', 'CustomRenderer')


class TokenSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['name'] = user.name
        token['role'] = ['777'] if user.is_superuser else user.r_names
        token['permis'] = user.ps
        token['group'] = user.group.name if user.group else ''
        token['gid'] = user.group.id if user.group else ''
        return token


def custom_exception_handler(exc, context):
    body = {
        'code': 1,
        'msg': '',
        'data': ''
    }
    if exc is exceptions.NotFound or isinstance(exc, exceptions.NotFound):
        body.update(msg=exc.args[0])
        return Response(data=body, status=200)
    elif exc is Http404 or isinstance(exc, Http404):
        body.update(msg='未找到')
        return Response(data=body, status=200)
    elif isinstance(exc, ValueError):
        body.update(msg=str(exc))
        return Response(data=body, status=200)
    # 上面为view异常，下面为校验错误
    r = exception_handler(exc, context)
    if r == None:
        logger.error(exc)
        return Response(data={'code': 1, 'msg': '服务器错误'}, status=200)
    r.status_code = 200
    match r.data:
        case list():
            body.update(msg=','.join(r.data))
        case dict():
            msgs = []
            for k, v in r.data.items():
                if isinstance(v, list):
                    msgs.append(f'{k}:{str(v[0])}')
                else:
                    msgs.append(f'{k}:{v}')
            body.update(msg=''.join(msgs))
    r.data = body
    return r
