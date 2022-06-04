from rest_framework import permissions


class IsOwner(permissions.DjangoModelPermissions):
    def has_object_permission(self, request, view, obj):
        if request.method not in permissions.SAFE_METHODS:
            return request.user == obj.user
        return True


'''class IsMod(permissions.DjangoObjectPermissions):
    def has_object_permission(self, request, view, obj):
        print("fuffhs", dir(obj))
        return True
'''
