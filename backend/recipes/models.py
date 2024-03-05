from colorfield.fields import ColorField
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from foodgram_backend.constants import (
    MAX_COLOR_LENGTH,
    MAX_NAME_LENGTH,
    MIN_COOKING_TIME,
    MAX_COOKING_TIME,
    MIN_INGREDIENTS,
    MAX_INGREDIENTS,
)
from users.models import User


class Tag(models.Model):
    """Модель тэгов."""
    name = models.CharField(max_length=MAX_NAME_LENGTH,
                            unique=True,
                            verbose_name='Название тэга')
    color = ColorField(max_length=MAX_COLOR_LENGTH,
                       unique=True,
                       verbose_name='Цвет в HEX')
    slug = models.SlugField(
        max_length=MAX_NAME_LENGTH,
        unique=True,
        verbose_name='Уникальный слаг',
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
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_name_measurement_unit'
            ),
        ]

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
                MIN_COOKING_TIME,
                message='Время приготовления не может быть'
                        f'меньше {MIN_COOKING_TIME}.'
            ),
            MaxValueValidator(
                MAX_COOKING_TIME,
                message='Время приготовления не может'
                        f'превышать {MAX_COOKING_TIME}.'
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
                MIN_INGREDIENTS,
                message='Количество ингредиентов  не может быть'
                        f'меньше {MIN_INGREDIENTS}.',
            ),
            MaxValueValidator(
                MAX_INGREDIENTS,
                message='Количество ингредиентов не может'
                        f'превышать {MAX_INGREDIENTS}.'
            ),
        )
    )

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'

    def __str__(self):
        return f'{self.recipe} - {self.ingredient}'


class BaseFavoritesShoppingCart(models.Model):
    """Базовая модель для избранного и списка покупок."""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )

    class Meta:
        abstract = True

    def __str__(self):
        return f'{self.user} добавил {self.recipe} в {self._meta.verbose_name}'


class Favorites(BaseFavoritesShoppingCart):
    """Модель для добавления рецепта в избранное."""

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        default_related_name = 'favorites'


class ShoppingCart(BaseFavoritesShoppingCart):
    """Модель для добавления рецепта в список покупок."""

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        default_related_name = 'shopping_cart'
