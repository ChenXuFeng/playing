'''
Date       :   2023-03
Author     :   ChenXuFeng <xu.sz@outlook.com> 
Describe   :   文件服务    
'''


import mimetypes
import os
import stat

from django.http import FileResponse, Http404
from django.utils.http import http_date


def generate_response(filepath, filename):
    # 是一个目录抛出异常
    if os.path.isdir(filepath):
        raise Http404("Directory indexes are not allowed here.")
    # 不存在，抛出异常
    if not os.path.exists(filepath):
        raise Http404('"%(path)s" does not exist' % {'path': filepath})
    # stat（）系统调用，获取文件信息
    stat_obj = os.stat(filepath)
    content_type, encoding = mimetypes.guess_type(filepath)
    content_type = content_type or 'application/octet-stream'
    response = FileResponse(open(filepath, 'rb'), content_type=content_type, as_attachment=True,
                            filename=filename)
    response["Last-Modified"] = http_date(stat_obj.st_mtime)
    if stat.S_ISREG(stat_obj.st_mode):
        response["Content-Length"] = stat_obj.st_size
    if encoding:
        response["Content-Encoding"] = encoding
    return response



