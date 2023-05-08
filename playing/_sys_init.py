'''
Date       :   2023-03
Author     :   ChenXuFeng <xu.sz@outlook.com> 
Describe   :   平台初始化工具，内置角色和权限数据
'''

__all__ = ('up',)

from accounts.models import Roles


def up():
    roles()

def permissions():
    """内置权限"""
    ps = [
        {'label':'账号管理', 'value':'can_accounts'},
        {'label':'账号列表', 'value':'list_account'},
        {'label':'新增账号', 'value':'post_account'},
        {'label':'修改账号', 'value':'patch_account'},
        {'label':'删除账号', 'value':'del_account'},
        {'label':'组列表', 'value':'list_group'},
        {'label':'新增组', 'value':'post_group'},
        {'label':'修改组', 'value':'patch_group'},
        {'label':'删除组', 'value':'del_group'},
        {'label':'新增组', 'value':'post_group'},
        # TODO: 待完善
    ]


def roles():
    """内置角色"""
    rs = [
        {'name':'平台管理员', 'is_internal':True},
        {'name':'参赛队伍', 'is_internal':True},
        {'name':'题库管理员', 'is_internal':True}
    ]
    Roles.objects.bulk_create(
        [Roles(**r) for r in rs],
        ignore_conflicts=True
    )

