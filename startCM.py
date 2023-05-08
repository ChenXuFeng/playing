import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE','playing.settings')
django.setup()


from dockerd.container_manage import ContainerManage

if __name__ == '__main__':
    cm = ContainerManage()
    try:
        cm.start()
    except KeyboardInterrupt:
        cm.stoped()
    except Exception as e:
        print(f'CM 未知错误：{e}')