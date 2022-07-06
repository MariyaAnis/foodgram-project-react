from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Кто подписался',
        on_delete=models.CASCADE,
        related_name='follower'
    )
    author = models.ForeignKey(
        User,
        verbose_name='На кого подписался',
        on_delete=models.CASCADE,
        related_name='following',
    )


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Кто подписался',
        on_delete=models.CASCADE,
        related_name='favorite_recipes'
    )
    recipe = models.ForeignKey(
        'recipes.Recipe',
        verbose_name='На какой рецепт',
        on_delete=models.CASCADE,
        related_name='favorites',
    )
