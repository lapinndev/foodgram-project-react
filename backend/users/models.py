from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import F, Q, UniqueConstraint

MAX_LENGHT = 150
MAX_EMAIL_LENGHT = 254


class CustomUser(AbstractUser):
    username = models.CharField(
        verbose_name='Логин',
        max_length=MAX_LENGHT,
        unique=True,
    )
    email = models.EmailField(
        verbose_name='Email',
        max_length=MAX_EMAIL_LENGHT,
        unique=True,
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=MAX_LENGHT,
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=MAX_LENGHT,
    )
    password = models.CharField(
        verbose_name='Пароль',
        max_length=MAX_LENGHT,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class FollowUser(models.Model):
    """ Модель подписки на автора. """
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='follower',
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name='Подписчик',
        related_name='following'
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=('user', 'author'),
                name='unique_follow'
            ),
            models.CheckConstraint(
                check=~Q(user=F('author')),
                name='no_self_follow'
            )
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f"{self.user} подписан на {self.author}"
