from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Recipe(models.Model):
    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'рецепты'

    name = models.CharField('название', max_length=200)
    text = models.TextField('описание')
    image = models.ImageField('Картинка', upload_to='media/recipes/images/')
    author = models.ForeignKey(User,
                               verbose_name='автор',
                               on_delete=models.CASCADE,
                               related_name='recipes'
                               )
    ingredients = models.ManyToManyField('ingredients.IngredientWeight',
                                         on_delete=models.PROTECT,
                                         related_name='recipes'
                                         )
    tags = models.ManyToManyField('recipe.Tag')
    cooking_time = models.PositiveSmallIntegerField('Время приготовления (в минутах)')

    def __str__(self):
        return self.name


class Tag(models.Model):
    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'теги'

    name = models.CharField('название', max_length=200, unique=True)
    color = models.CharField('цветовой HEX-код', max_length=7)
    slug = models.SlugField('слаг', max_length=100, unique=True)

    def __str__(self):
        return self.name
