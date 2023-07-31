from django.db import models
from users.models import CustomUser
from recipes.models import Recipe


class Favorite(models.Model):
    user = models.ForeignKey(
        CustomUser,
        verbose_name='Пользователь',
        related_name='favorite',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        related_name='favorite',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Избранное',
        verbose_name_plural = 'Избранные',
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'), name='unique_favorite'
            ),
        )

    def __str__(self):
        return f'{self.user} - {self.recipe}'
