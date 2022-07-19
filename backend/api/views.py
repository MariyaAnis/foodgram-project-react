from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination
from rest_framework import filters, permissions, viewsets, status
from djoser.views import UserViewSet as DjoserUserViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404


from recipes.models import Recipe, Tag, IngredientWeight
from users.models import Follow, ShoppingList, Favorite, User
from ingredients.models import Ingredient

from .permissions import IsAuthorOrReadOnlyPermission
from .serializers import (RecipeSerializer,
                          SubscriptionSerializer,
                          TagSerializer,
                          RecipeSmallSerializer,
                          IngredientSerializer,
                          IngredientWeightSerializer,
                          CustomUserSerializer,
                          CustomUserCreateSerializer)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthorOrReadOnlyPermission,)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_fields = ('name',)
    search_fields = ('name', )
    pagination_class = LimitOffsetPagination

    @action(
        detail=True,
        methods=('post', 'delete'),
        url_path='shopping_cart',
        permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, pk=self.kwargs.get('pk'))
        serializer = RecipeSmallSerializer(recipe)
        return self.validator_create_delete(request, ShoppingList, serializer, recipe)

    @action(
        detail=True,
        methods=('post', 'delete'),
        url_path='favorite',
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, pk=self.kwargs.get('pk'))
        serializer = RecipeSmallSerializer(recipe)
        return self.validator_create_delete(request, Favorite, serializer, recipe)

    def validator_create_delete(self, request, model, serializer, recipe):
        if request.method == 'POST':
            if model.objects.filter(recipe=recipe, user=self.request.user).exists():
                return Response(
                    'Нельзя повторно добавить рецепт',
                    status=status.HTTP_400_BAD_REQUEST
                )
            model.objects.create(recipe=recipe, user=self.request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if not model.objects.filter(recipe=recipe, user=self.request.user).exists():
            return Response(
                'Вы не добавляли этот рецепт',
                status=status.HTTP_400_BAD_REQUEST
            )
        record = model.objects.filter(recipe=recipe, user=self.request.user)
        record.delete()
        return Response(
            'Рецепт удален из вашего списка',
            status=status.HTTP_204_NO_CONTENT
        )


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAuthorOrReadOnlyPermission,)
    # filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name',)


class IngredientWeightViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = IngredientWeight.objects.all()
    serializer_class = IngredientWeightSerializer
    permission_classes = (IsAuthorOrReadOnlyPermission,)
    # filter_backends = (IngredientSearchFilter,)
    # search_fields = ('^name',)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class SubscriptionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SubscriptionSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('=following__username',)

    def get_queryset(self):
        return Follow.objects.filter(user=self.request.user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update(
            {'recipes_limit': self.request.query_params.get('recipes_limit')}
        )
        return context


class UserViewSet(DjoserUserViewSet):
    pagination_class = LimitOffsetPagination
