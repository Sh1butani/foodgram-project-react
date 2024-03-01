from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from rest_framework.authtoken.models import TokenProxy

from users.models import Subscribe, User


class UserAdmin(BaseUserAdmin):

    list_display = ('email', 'username')
    list_filter = ('email', 'username')


admin.site.register(User, UserAdmin)
admin.site.register(Subscribe)
admin.site.unregister(Group)
admin.site.unregister(TokenProxy)
