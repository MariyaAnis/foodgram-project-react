from rest_framework.response import Response
from django.http import FileResponse
from rest_framework.pagination import LimitOffsetPagination
from rest_framework import filters, permissions, viewsets, status
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from .filters import RecipeFilter
from django.db.models import Sum


import io

from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

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
                          RecipeCreateUpdateSerializer,
                          SubscribCreateDeleteSerializer)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthorOrReadOnlyPermission,)
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter
    pagination_class = LimitOffsetPagination

    def get_serializer_class(self):
        if self.request.method == 'POST' or self.request.method == 'PATCH':
            return RecipeCreateUpdateSerializer
        return RecipeSerializer

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
        recipe = model.objects.filter(recipe=recipe, user=self.request.user)
        recipe.delete()
        return Response(
            'Рецепт удален из вашего списка',
            status=status.HTTP_204_NO_CONTENT
        )

    @staticmethod
    def create_pdf(ingredients, title):

        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)

        pdfmetrics.registerFont(
            TTFont('FreeSans', 'FreeSans.ttf'))

        p.setFont('FreeSans', 20)
        y = 810
        p.drawString(55, y, f'{title}')
        y -= 30

        p.setFont('FreeSans', 14)
        string_number = 1
        for ingredient in ingredients:
            p.drawString(
                15, y,
                f'{string_number}. {ingredient.name.capitalize()} ({ingredient.measurement_unit}) - {ingredient.amount}'
            )
            y -= 20
            string_number += 1

        p.showPage()
        p.save()
        buffer.seek(0)

        return buffer

    @action(
        detail=False,
        methods=('get', ),
        url_path='download_shopping_cart',
        permission_classes=(IsAuthenticated,),
    )
    def download_shopping_cart(self, request):
        recipe_list = Recipe.objects.filter(shopping_list_users__user=request.user)
        ingredient_list = Ingredient.objects.filter(
            ingredient_recipes__recipe__in=recipe_list
        ).annotate(amount=Sum('ingredient_recipes__amount'))

        file = self.create_pdf(ingredient_list, 'Список покупок')

        return FileResponse(
            file,
            as_attachment=True,
            filename='shopping_list.pdf',
            status=status.HTTP_200_OK
        )


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)


class IngredientWeightViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = IngredientWeight.objects.all()
    serializer_class = IngredientWeightSerializer


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class SubscriptionViewSet(viewsets.ModelViewSet):
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


class SubscriptionCreateDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    @staticmethod
    def post(request, id):
        data = {'user': request.user.id, 'author': id}
        serializer = SubscribCreateDeleteSerializer(
            data=data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @staticmethod
    def delete(request, id):
        user = request.user
        author = get_object_or_404(User, id=id)
        instance = get_object_or_404(
            Follow, user=user,  author=author
        )
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)