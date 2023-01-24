from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(
        'Email',
        max_length=254,
        unique=True,)
    first_name = models.CharField(
        'Имя',
        max_length=150)
    last_name = models.CharField(
        'Фамилия',
        max_length=150)
    # is_subscribed = models.BooleanField(
    #     help_text='Подписан ли текущий пользователь на этого',
    #     default=False
    # )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = (
        'username',
        'first_name',
        'last_name',
        # 'is_subscribed',
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)

    def __str__(self):
        return self.email


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        related_name='follower',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        related_name='following',
        verbose_name='Автор'
    )

    class Meta:
        constraints = (models.UniqueConstraint(
            fields=['user', 'author'],
            name='user_to_author_follow',
        ),)
