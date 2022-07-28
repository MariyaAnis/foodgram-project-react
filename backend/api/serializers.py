from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from ingredients.models import Ingredient
from recipes.models import IngredientWeight, Recipe, Tag
from users.models import Favorite, Follow, ShoppingList, User


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
    id = serializers.ReadOnlyField(source='author.id')
    email = serializers.ReadOnlyField(source='author.email')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    @staticmethod
    def get_is_subscribed(obj):
        return Follow.objects.filter(
            user=obj.user, author=obj.author
        ).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        queryset = Recipe.objects.filter(author=obj.author)
        if limit:
            queryset = queryset[:int(limit)]
        return RecipeSmallSerializer(queryset, many=True).data

    @staticmethod
    def get_recipes_count(obj):
        return Recipe.objects.filter(author=obj.author).count()


class SubscribeCreateDeleteSerializer(serializers.ModelSerializer):

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
        return Favorite.objects.filter(user=user, recipe=recipe).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user is None or user.is_anonymous:
            return False
        recipe = obj
        return ShoppingList.objects.filter(user=user, recipe=recipe).exists()


class IngredientWeightCreateSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(min_value=1)

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
            'author',
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time'
        )
        read_only_fields = ('author',)

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        tags = self.initial_data.get('tags')
        self.ingredients_validate(ingredients)
        self.tags_validate(tags)

        if ingredients:
            self.ingredients_validate(ingredients)
            data['ingredients'] = ingredients
        if tags:
            self.tags_validate(tags)
            data['tags'] = tags
        return data

    @staticmethod
    def ingredients_validate(ingredients):
        ingredients_set = set()
        if not ingredients:
            raise serializers.ValidationError(
                'Добавьте ингридиенты'
            )
        for ingredient in ingredients:
            amount = ingredient.get('amount')
            ingredient_id = ingredient.get('id')
            if ingredient_id in ingredients_set:
                raise serializers.ValidationError(
                    'Ингредиенты в рецепте не должены повторяться.'
                )
            try:
                int(ingredient_id)
            except ValueError:
                raise serializers.ValidationError(
                    'Id ингридиента должно быть числом'
                )
            try:
                int(amount)
            except ValueError:
                raise serializers.ValidationError(
                    'Количество ингридиента должно быть числом'
                )
            ingredients_set.add(ingredient_id)

    @staticmethod
    def tags_validate(tags):
        if not tags:
            raise serializers.ValidationError(
                'Необходимо добавить хотя бы один тэг'
            )
        if len(tags) > len(set(tags)):
            raise serializers.ValidationError(
                'Тэги не должны повторяться'
            )

    @staticmethod
    def create_ingredients(ingredients, recipe):
        for ingredient in ingredients:
            IngredientWeight.objects.create(
                recipe=recipe, ingredient_id=ingredient['id'],
                amount=ingredient['amount']
            )

    @staticmethod
    def create_tags(tags, recipe):
        for tag in tags:
            recipe.tags.add(tag)

    def create(self, validated_data):
        author = self.context.get('request').user
        tags = validated_data.pop('tags')
        validated_data.pop('weight')
        ingr = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=author, **validated_data)
        self.create_tags(tags, recipe)
        self.create_ingredients(ingr, recipe)
        return recipe

    def update(self, instance, validated_data):
        instance.tags.clear()
        IngredientWeight.objects.filter(recipe=instance).delete()
        self.create_tags(validated_data.pop('tags'), instance)
        validated_data.pop('weight')
        self.create_ingredients(validated_data.pop('ingredients'), instance)
        return super().update(instance, validated_data)
