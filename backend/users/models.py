from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models

from foodgram_backend.constants import MAX_LENGTH


class User(AbstractUser):
    """Кастомная модель пользователя."""
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    username = models.CharField(
        'Имя пользователя',
        unique=True,
        max_length=MAX_LENGTH,
        validators=[UnicodeUsernameValidator()]
    )
    email = models.EmailField(unique=True,
                              verbose_name='Почта')
    first_name = models.CharField(
        'Имя', max_length=MAX_LENGTH,
    )
    last_name = models.CharField(
        'Фамилия', max_length=MAX_LENGTH,
    )
    bio = models.TextField(
        'Биография', blank=True
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscribe(models.Model):
    """Возвращает пользователей, на которых подписан текущий пользователь."""
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='subscriber',
                             verbose_name='Подписчик')
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='subscribing',
                               verbose_name='Автор подписки')

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'], name='unique_name'
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='prevent_self_follow'
            )
        ]

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
