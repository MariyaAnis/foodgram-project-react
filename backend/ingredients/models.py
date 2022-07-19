from django.db import models


class Ingredient(models.Model):
    name = models.CharField('название', max_length=200)
    measurement_unit = models.CharField('единицы измерения', max_length=200)

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'ингредиенты'

    def __str__(self):
        return f'{self.name} - {self.measurement_unit}'
