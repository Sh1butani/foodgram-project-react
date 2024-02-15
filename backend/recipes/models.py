from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

from foodgram_backend.settings import (
    MAX_COLOR_LENGTH,
    MAX_NAME_LENGTH,
    MIN_MARK,
)
from users.models import User


class Tag(models.Model):
    """Модель тэгов."""
    name = models.CharField(max_length=MAX_NAME_LENGTH,
                            unique=True,
                            verbose_name='Название тэга')
    color = models.CharField(max_length=MAX_COLOR_LENGTH,
                             unique=True,
                             verbose_name='Цвет в HEX')
    slug = models.SlugField(
        max_length=MAX_NAME_LENGTH,
        unique=True,
        verbose_name='Уникальный слаг',
        validators=[RegexValidator(
            r'^[-a-zA-Z0-9_]+$',
            message='Пожалуйста, введите корректный формат слага.'
                    'Он должен содержать только буквы, цифры, "_" и "-".',
        )]
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингридиентов."""
    name = models.CharField(max_length=MAX_NAME_LENGTH,
                            verbose_name='Название ингридиента')
    measurement_unit = models.CharField(max_length=MAX_NAME_LENGTH,
                                        verbose_name='Единицы измерения')

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецепта."""
    name = models.CharField(max_length=MAX_NAME_LENGTH,
                            verbose_name='Название рецепта')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор публикации'
    )
    image = models.ImageField(
        upload_to='recipes/images/', verbose_name='Картинка'
    )
    text = models.TextField(verbose_name='Описание')
    ingredients = models.ManyToManyField(Ingredient,
                                         through='RecipeIngredients',
                                         verbose_name='Ингредиенты')
    tags = models.ManyToManyField(Tag,
                                  related_name='recipes',
                                  verbose_name='Тэги')
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=(
            MinValueValidator(
                MIN_MARK,
                message='Время приготовления не может быть'
                        f'меньше {MIN_MARK}.'
            ),
        )
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации', auto_now_add=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeIngredients(models.Model):
    """Модель ингредиентов рецепта."""
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name='recipe_ingredients',
                               verbose_name='Рецепт')
    ingredient = models.ForeignKey(Ingredient,
                                   on_delete=models.CASCADE,
                                   related_name='recipe_ingredients',
                                   verbose_name='Ингредиент')
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество ингредиентов',
        validators=(
            MinValueValidator(
                MIN_MARK,
                message='Количество ингредиентов  не может быть'
                        f'меньше {MIN_MARK}.',
            ),
        )
    )

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'

    def __str__(self):
        return f'{self.recipe} - {self.ingredient}'


class Favorites(models.Model):
    """Модель для добавления рецепта в избранное."""
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name='favorites',
                               verbose_name='Рецепт')
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='favorites',
                             verbose_name='Пользователь')

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'

    def __str__(self):
        return f'{self.user} добавил {self.recipe} в избранное'


class ShoppingCart(models.Model):
    """Модель для добавления рецепта в список покупок."""
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name='shopping_cart',
                               verbose_name='Рецепт')
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='shopping_cart',
                             verbose_name='Пользователь')

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'

    def __str__(self):
        return f'{self.user} добавил {self.recipe} в список покупок'
