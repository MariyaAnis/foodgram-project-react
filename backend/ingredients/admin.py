from django.contrib import admin

from ingredients.models import Ingredient, IngredientWeight

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('name',)
    empty_value_display = '-пусто-'


@admin.register(IngredientWeight)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'ingredient', 'amount')
    search_fields = ('ingredient',)
    empty_value_display = '-пусто-'