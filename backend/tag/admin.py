from django.contrib import admin
from .models import Tag


class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color', 'slug')
    search_fields = ('name', 'color')
    list_filter = ('name', 'color')
    ordering = ('name',)
    empty_value_display = '-пусто-'


admin.site.register(Tag, TagAdmin)
