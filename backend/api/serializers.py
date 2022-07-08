from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import Recipe, Tag
from users.models import Follow, ShoppingList, Favorite
from django.contrib.auth.models import User


class RecipeSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        default=serializers.CurrentUserDefault(),
        queryset=User.objects.all(),
    )

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


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'color', 'slug')
        read_only_fields = ('id',)
        model = Tag


class FollowSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        read_only=True, slug_field='username',
        default=serializers.CurrentUserDefault()
    )
    following = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all()
    )

    def validate(self, data):
        if self.context['request'].user == data['following']:
            raise serializers.ValidationError(
                'Нальзя подписываться на самого себя'
            )
        return data

    class Meta:
        fields = '__all__'
        model = Follow
        read_only_fields = ('id', 'user')
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'following')
            )
        ]


class ShoppingListSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        read_only=True, slug_field='username',
        default=serializers.CurrentUserDefault()
    )
    shopping_lists = serializers.SlugRelatedField(
        slug_field='id',
        queryset=ShoppingList.objects.all()
    )

    class Meta:
        fields = '__all__'
        model = ShoppingList
        read_only_fields = ('id', 'user')
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'shopping_lists')
            )
        ]


class FavoriteSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        read_only=True, slug_field='username',
        default=serializers.CurrentUserDefault()
    )
    favorites = serializers.SlugRelatedField(
        slug_field='id',
        queryset=ShoppingList.objects.all()
    )

    class Meta:
        fields = '__all__'
        model = ShoppingList
        read_only_fields = ('id', 'user')
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'favorites')
            )
        ]
