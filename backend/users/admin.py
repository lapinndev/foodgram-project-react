from django.contrib import admin

from users.models import FollowUser, CustomUser


class UsersAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'username',
        'last_name',
        'first_name',
        'email',
    )
    search_fields = ('username', 'first_name', 'last_name', 'email')
    list_filter = ('username', 'email',)
    empty_value_display = '-пусто-'


class FolowAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'author')
    search_fields = ('user', 'author')


admin.site.register(CustomUser, UsersAdmin)
admin.site.register(FollowUser, FolowAdmin)
