from django.contrib import admin
from .models import Recipe


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author', 'text', 'image', 'cooking_time')
    search_fields = ('name', 'tags__name')
    list_filter = ('name', 'tags__name')
    ordering = ('name',)
    empty_value_display = '-пусто-'

    def tag_count(self, obj):
        return obj.tags.count()

    def ingredient_count(self, obj):
        return obj.ingredients.count()


admin.site.register(Recipe, RecipeAdmin)
