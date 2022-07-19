from django.contrib import admin

from recipes.models import Recipe, Tag, IngredientWeight


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id',
                    'author',
                    'name',
                    'image',
                    'text',
                    'cooking_time')
    search_fields = ('name',)
    list_filter = ('name', 'author', 'tags')
    empty_value_display = '-пусто-'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass


@admin.register(IngredientWeight)
class IngredientWeightAdmin(admin.ModelAdmin):
    list_display = ('id', 'ingredient', 'amount')
    search_fields = ('ingredient',)
    empty_value_display = '-пусто-'