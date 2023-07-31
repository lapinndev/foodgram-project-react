from django.contrib import admin
from .models import Ingredient


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement')
    search_fields = ('name', 'measurement')
    list_filter = ('name', 'measurement')
    ordering = ('name',)
    empty_value_display = '-пусто-'


admin.site.register(Ingredient, IngredientAdmin)
