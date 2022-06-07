from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm

from .models import Room, Message, Topic, User


class MyUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User


class MyUserAdmin(UserAdmin):
    form = MyUserChangeForm

    fieldsets = UserAdmin.fieldsets + ((None, {"fields": ("bio", "avatar")}),)


admin.site.register(Room)
admin.site.register(Message)
admin.site.register(Topic)
admin.site.register(User, MyUserAdmin)
