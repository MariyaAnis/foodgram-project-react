from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='кто подписался',
        on_delete=models.CASCADE,
        related_name='follower'
    )
    author = models.ForeignKey(
        User,
        verbose_name='на кого подписался',
        on_delete=models.CASCADE,
        related_name='following',
    )

    class Meta:
        verbose_name = 'подписка'
        verbose_name_plural = 'подписки на пользовотелей'

    def __str__(self):
        return self.author


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='кто подписался',
        on_delete=models.CASCADE,
        related_name='favorite_recipes'
    )
    recipe = models.ForeignKey(
        'recipes.Recipe',
        verbose_name='на какой рецепт',
        on_delete=models.CASCADE,
        related_name='favorites',
    )

    class Meta:
        verbose_name = 'любимый рецепт'
        verbose_name_plural = 'любимые рецепты'

    def __str__(self):
        return self.recipe.name


class ShoppingList(models.Model):

    user = models.ForeignKey(
        User,
        verbose_name='кто подписался',
        on_delete=models.CASCADE,
        related_name='shopping_list_recipes'
    )
    recipe = models.ForeignKey(
        'recipes.Recipe',
        verbose_name='на какой рецепт',
        on_delete=models.CASCADE,
        related_name='shopping_list_users',
    )

    class Meta:
        verbose_name = 'список покупок'
        verbose_name_plural = 'списки покупок'

    def __str__(self):
        return self.recipe.name
