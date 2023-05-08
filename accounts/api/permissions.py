from playing.permissions import Permission


class AdminPermission(Permission):

    def has_permission(self, request, view):
        if super().has_permission(request, view):
            return True
        rs = request.user.r_names
        return '平台管理员' in rs
    

class TeamPermission(Permission):

    def has_permission(self, request, view):
        if super().has_permission(request, view):
            return True
        if request.user.roles.exists():
            return request.user.r_names[0] == '参赛队伍'
        return False
