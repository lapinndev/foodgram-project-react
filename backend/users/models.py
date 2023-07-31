from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError

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
        constraints = (
            models.UniqueConstraint(
                fields=('email', 'username'), name='unique_custom_user'
            ),
        )

    def __str__(self):
        return self.username


class FollowUser(models.Model):
    author = models.ForeignKey(
        CustomUser,
        verbose_name='Пользователь',
        related_name='subscriber',
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        CustomUser,
        verbose_name='Подписчик',
        related_name='subscribe',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'author'), name='unique_follow'
            ),
        )

    def __str__(self):
        return f'Пользователь {self.user} подписан на {self.author}'

    def clean(self):
        if self.user == self.author:
            raise ValidationError('Самоподписка запрещена!')
