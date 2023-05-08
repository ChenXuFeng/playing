from playing.permissions import Permission


class QuestionsPermission(Permission):

    def has_permission(self, request, view):
        if super().has_permission(request, view):
            return True
        if request.user.roles.exists():
            return request.user.r_names[0] == '题库管理员'
        return False
