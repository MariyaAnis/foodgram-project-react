from django.contrib import admin

from recipes.models import Recipe, Tag


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id',
                    # 'tags',
                    'author',
                    # 'ingredients',
                    'name',
                    'image',
                    'text',
                    'cooking_time')
    # list_editable = ('tags',)
    search_fields = ('name',)
    # list_filter = '-id',
    empty_value_display = '-пусто-'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass
