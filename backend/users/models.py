from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import UniqueConstraint

from users.validators import validate_username


class User(AbstractUser):
    """Пользовательская модель - Пользователь."""

    email = models.EmailField(
        'Почта',
        max_length=254,
        unique=True)
    first_name = models.CharField(
        'Имя',
        max_length=150,
        blank=False
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=150,
        blank=False)
    username = models.CharField(
        'Юзернейм',
        max_length=150,
        validators=[validate_username])

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = (
        'username',
        'first_name',
        'last_name',
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('-id',)

    def __str__(self):
        return self.username


class Follow(models.Model):
    """Модель - Подписка."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='author',
        verbose_name='Автор'
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['user', 'author'],
                name='user_author_unique',
            )
        ]

    def __str__(self):
        return f'{self.user} подписался на {self.author}'
