from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator
from djoser.serializers import UserSerializer, UserCreateSerializer
from drf_extra_fields.fields import Base64ImageField
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

    @staticmethod
    def get_name(obj):
        return obj.ingredient.name

    @staticmethod
    def get_measurement_unit(obj):
        return obj.ingredient.measurement_unit

    class Meta:
        model = IngredientWeight
        fields = ('id', 'name', 'measurement_unit', 'amount')
        read_only_fields = ('id', )


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'color', )
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

    @staticmethod
    def get_recipes_count(obj):
        return obj.recipes.all().count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit is not None:
            queryset = Recipe.objects.filter(author=obj.following)[:int(recipes_limit)]
        else:
            queryset = Recipe.objects.filter(author=obj.following)
        return RecipeSmallSerializer(queryset, many=True).data


class SubscribCreateDeleteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Follow
        fields = [
            'user',
            'author'
        ]
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'author'),
                message='Подписка уже есть'
            )
        ]


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


class RecipeSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField()
    ingredients = IngredientWeightSerializer(many=True, source='weight')
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    tags = TagSerializer(many=True)

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
        return ShoppingList.objects.filter(shopping_list_users=user, recipe=recipe).exist()


class IngredientWeightCreateSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(min_value=1, )

    class Meta:
        fields = ['id', 'amount']
        model = IngredientWeight


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):

    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )
    ingredients = IngredientWeightCreateSerializer(many=True, source='weight')
    image = Base64ImageField()
    name = serializers.CharField(max_length=200)
    cooking_time = serializers.IntegerField(min_value=1)
    author = CustomUserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'ingredients',
            'author',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time'
        )
        read_only_field = ('id', 'author')

    # def validators(self):
#дописать валидатор

    @staticmethod
    def create_ingredients(ingredients, recipe):
        for ingredient in ingredients:
            IngredientWeight.objects.create(
                recipe=recipe, ingredient=ingredient['id'],
                amount=ingredient['amount']
            )

    @staticmethod
    def create_tags(tags, recipe):
        for tag in tags:
            recipe.tags.add(tag)

    def create(self, validated_data):
        author = self.context.get('request').user
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('weight')
        recipe = Recipe.objects.create(author=author, **validated_data)
        self.create_tags(tags, recipe)
        self.create_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        instance.tags.clear()
        IngredientWeight.objects.filter(recipe=instance).delete()
        self.create_tags(validated_data.pop('tags'), instance)
        self.create_ingredients(validated_data.pop('weight'), instance)
        return super().update(instance, validated_data)
