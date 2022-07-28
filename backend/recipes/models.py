from django.db import models

from ingredients.models import Ingredient
from users.models import User


class Recipe(models.Model):
    name = models.CharField('название', max_length=200)
    text = models.TextField('описание')
    image = models.ImageField('картинка', upload_to='media/recipes/images/')
    author = models.ForeignKey(
        User,
        verbose_name='автор',
        on_delete=models.CASCADE,
        related_name='author_recipes'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name='recipes_ingredients',
        through='IngredientWeight',
        through_fields=('recipe', 'ingredient'),
    )
    tags = models.ManyToManyField('recipes.Tag', related_name='recipes_tag')
    cooking_time = models.PositiveSmallIntegerField(
        'время приготовления (в минутах)'
    )

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'рецепты'

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField('название', max_length=200, unique=True)
    color = models.CharField('цветовой HEX-код', max_length=7)
    slug = models.SlugField('слаг', max_length=100, unique=True)

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'теги'

    def __str__(self):
        return self.name


class IngredientWeight(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='weight',
        verbose_name='рецепт',
        db_index=True
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.PROTECT,
        verbose_name='ингридиент',
        related_name='ingredient_recipes',
    )
    amount = models.PositiveIntegerField('количество')

    class Meta:
        verbose_name = 'вес ингредиента'
        verbose_name_plural = 'вес ингредиентов'

    def __str__(self):
        return f'{self.ingredient} - {self.amount}'
