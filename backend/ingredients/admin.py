from django.contrib import admin
from .models import Ingredient


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('name', 'measurement_unit')
    list_filter = ('name', 'measurement_unit')
    ordering = ('name',)
    empty_value_display = '-пусто-'


admin.site.register(Ingredient, IngredientAdmin)
