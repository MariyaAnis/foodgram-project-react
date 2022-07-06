from django.db import models


class Ingredient(models.Model):
    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'ингредиенты'

    name = models.CharField('название', max_length=200)
    measurement_unit = models.CharField('единицы измерения', max_length=200)

    def __str__(self):
        return self.name


class IngredientWeight(models.Model):
    class Meta:
        verbose_name = 'вес ингредиента'
        verbose_name_plural = 'вес ингредиентов'

    ingredient = models.ForeignKey('ingredients.Ingredient', on_delete=models.PROTECT, verbose_name='ингридиент')
    weight = models.PositiveIntegerField('количество')

    def __str__(self):
        return f'{self.ingredient} - {self.weight}'
