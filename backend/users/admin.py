from django.contrib import admin

from users.models import User, Subscribe


class UserAdmin(admin.ModelAdmin):

    list_display = ('email', 'username')
    list_filter = ('email', 'username')


admin.site.register(User, UserAdmin)
admin.site.register(Subscribe)
