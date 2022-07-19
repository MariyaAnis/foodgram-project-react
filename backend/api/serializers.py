from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator
from djoser.serializers import UserSerializer, UserCreateSerializer
from drf_extra_fields.fields import Base64ImageField
from drf_extra_fields.relations import PresentablePrimaryKeyRelatedField
from recipes.models import Recipe, Tag, IngredientWeight
from users.models import Follow, ShoppingList, Favorite, User
from ingredients.models import Ingredient


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'measurement_unit')
        read_only_fields = ('id',)
        model = Ingredient


class IngredientWeightSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    measurement_unit = serializers.SerializerMethodField()

    def get_name(self, obj):
        return obj.ingredient.name

    def get_measurement_unit(self, obj):
        return obj.ingredient.measurement_unit

    class Meta:
        model = IngredientWeight
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        default=serializers.CurrentUserDefault(),
        queryset=User.objects.all(),
    )
    image = Base64ImageField()
    ingredients = PresentablePrimaryKeyRelatedField(
        queryset=IngredientWeight.objects.all(),
        presentation_serializer=IngredientWeightSerializer,
        read_source=None
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        fields = ('id',
                  'tags',
                  'author',
                  'ingredients',
                  'is_favorited',
                  'is_in_shopping_cart',
                  'name',
                  'image',
                  'text',
                  'cooking_time')
        model = Recipe
        read_only_fields = ('id',)

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user is None or user.is_anonymous:
            return False
        recipe = obj
        return Favorite.objects.filter(user=user, recipe=recipe).exist()

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user is None or user.is_anonymous:
            return False
        recipe = obj
        return ShoppingList.objects.filter(user=user, recipe=recipe).exist()


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'color', 'slug')
        read_only_fields = ('id',)
        model = Tag


class RecipeSmallSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = [
            'id',
            'name',
            'image',
            'cooking_time'
        ]


class SubscriptionSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )
        read_only_fields = ('id', 'email', 'username', 'first_name', 'last_name',)

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return Follow.objects.filter(user=user).filter(author=obj).exists()
        return False

    def get_recipes_count(self, obj):
        return obj.recipes.all().count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit is not None:
            queryset = Recipe.objects.filter(author=obj.following)[:int(recipes_limit)]
        else:
            queryset = Recipe.objects.filter(author=obj.following)
        return RecipeSmallSerializer(queryset, many=True).data


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        ]

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user is None or user.is_anonymous:
            return False
        return Follow.objects.filter(author=obj, user=user).exists()


class CustomUserCreateSerializer(UserCreateSerializer):

    class Meta:
        model = User
        fields = [
            'email',
            'username',
            'first_name',
            'last_name',
            'password'
        ]
