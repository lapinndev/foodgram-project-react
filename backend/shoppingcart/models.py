from django.db import models
from users.models import CustomUser
from recipes.models import Recipe


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        CustomUser,
        verbose_name='Пользователь',
        related_name='shoppingcart',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        related_name='shoppingcart',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'), name='unique_shopping_cart'
            ),
        )

    def __str__(self):
        return f'{self.user} - {self.recipe}'
