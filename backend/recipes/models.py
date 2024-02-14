from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.core.validators import MinValueValidator


MAX_LENGTH = 150
MAX_NAME_LENGTH = 200
MAX_COLOR_LENGTH = 7
MAX_MEASUREMENT_LENGTH = 10
MAX_ROLE_LENGTH = 25
MIN_MARK = 1
USER = 'user'
ADMIN = 'admin'


class User(AbstractUser):
    """Кастомная модель пользователя."""

    ROLES = [
        (USER, 'user'),
        (ADMIN, 'admin')
    ]
    username = models.CharField(
        'Имя пользователя',
        unique=True,
        max_length=MAX_LENGTH,
        validators=[UnicodeUsernameValidator()]
    )

    email = models.EmailField(unique=True,
                              verbose_name='Почта')
    first_name = models.CharField(
        'Имя', max_length=MAX_LENGTH, blank=True
    )
    last_name = models.CharField(
        'Фамилия', max_length=MAX_LENGTH, blank=True
    )
    bio = models.TextField(
        'Биография', blank=True
    )
    role = models.CharField(
        'Роль',
        choices=ROLES,
        default=USER,
        max_length=MAX_ROLE_LENGTH,
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    @property
    def is_admin(self):
        """Проверяем является ли пользователь админом или суперюзером."""
        return self.role == ADMIN or self.is_superuser

    def __str__(self):
        return self.username


class Tag(models.Model):
    """Модель тэгов."""

    name = models.CharField(max_length=MAX_NAME_LENGTH,
                            unique=True,
                            verbose_name='Название тэга')
    color_code = models.CharField(max_length=MAX_COLOR_LENGTH,
                                  unique=True,
                                  verbose_name='Цветовой код')
    slug = models.SlugField(unique=True, verbose_name='Уникальный слаг')

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингридиентов."""

    name = models.CharField(max_length=MAX_NAME_LENGTH,
                            verbose_name='Название ингридиента')
    measurement_unit = models.CharField(max_length=MAX_MEASUREMENT_LENGTH,
                                        verbose_name='Единицы измерения')

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
    description = models.TextField(verbose_name='Описание')
    ingredients = models.ManyToManyField(Ingredient,
                                         through='RecipeIngredients',
                                         verbose_name='Ингредиенты')
    tag = models.ManyToManyField(Tag,
                                 related_name='recipes',
                                 verbose_name='Тэг')
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
    """Модель ингридиентов рецепта."""

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


class Favourites(models.Model):
    """Добавляет рецепт в избранное."""

    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name='favourites',
                               verbose_name='Рецепт')
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='favourites',
                             verbose_name='Пользователь')

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'

    def __str__(self):
        return f'{self.user} добавил {self.recipe} в избранное'


class ShoppingList(models.Model):
    """Добавляет рецепт в список покупок."""

    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name='shopping_list',
                               verbose_name='Рецепт')
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='shopping_list',
                             verbose_name='Пользователь')

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'

    def __str__(self):
        return f'{self.user} добавил {self.recipe} в список покупок'


class Following(models.Model):
    """Возвращает пользователей, на которых подписан текущий пользователь."""

    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='follower',
                             verbose_name='Подписчик')
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='following',
                               verbose_name='Автор')

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'], name='unique_following'
            )
        ]

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
