from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models

from foodgram_backend.settings import ADMIN, MAX_LENGTH, MAX_ROLE_LENGTH, USER


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
