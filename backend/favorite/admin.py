from django.contrib import admin
from .models import Favorite


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    search_fields = ('user__username', 'recipe__name')
    list_filter = ('user__username', 'recipe__name')
    empty_value_display = 'пусто'

    def user(self, obj):
        return obj.user.username

    def recipe(self, obj):
        return obj.recipe.name


admin.site.register(Favorite, FavoriteAdmin)
