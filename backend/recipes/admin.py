from django.contrib import admin
from recipes.models import IngredientWeight, Recipe, Tag


class IngredientWeightInline(admin.TabularInline):
    model = IngredientWeight
    min_num = 1
    extra = 1


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
    readonly_fields = ('in_favorite',)
    inlines = (IngredientWeightInline,)

    def in_favorite(self, obj):
        return obj.in_favorite.all().count()

    in_favorite.short_description = 'Количество добавлений в избранное'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass


@admin.register(IngredientWeight)
class IngredientWeightAdmin(admin.ModelAdmin):
    list_display = ('id', 'ingredient', 'amount')
    search_fields = ('ingredient',)
    empty_value_display = '-пусто-'




