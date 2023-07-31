from django.db import models

MAX_INGREDIENT_LENGHT = 200


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=MAX_INGREDIENT_LENGHT,
    )
    measurement = models.CharField(
        verbose_name='Измерение',
        max_length=MAX_INGREDIENT_LENGHT,
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'measurement'), name='unique_ingredient',
            ),
        )

    def __str__(self):
        return self.name
