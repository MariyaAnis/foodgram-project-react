from django_filters.rest_framework import FilterSet, filters
from recipes.models import Recipe


class RecipeFilter(FilterSet):

    tags = filters.AllValuesMultipleFilter(field_name='tags__slug', label='Тег')
    is_favorited = filters.BooleanFilter(method='filter_is_favorited', label='Показать любимые рецепты')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart',
        label='Показать рецепты в шоплисте',
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')

    def filter_is_favorited(self, queryset, name, value):
        if value:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value:
            return queryset.filter(shopping_list_users__user=self.request.user)
        return queryset
