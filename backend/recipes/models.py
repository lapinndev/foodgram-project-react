from django.db import models
from django.core.validators import MinValueValidator
from users.models import CustomUser
from tag.models import Tag
from ingredients.models import Ingredient


MAX_RECIPENAME_LENGHT = 200
MIN_COOKING_AMOUNT = 1


class Recipe(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=MAX_RECIPENAME_LENGHT
    )
    author = models.ForeignKey(
        CustomUser,
        verbose_name='Автор',
        related_name='recipes',
        on_delete=models.CASCADE
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
        related_name='recipes',
        blank=False
    )
    text = models.TextField(
        verbose_name='Описание'
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='recipes/',
        blank=True
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты',
        related_name='recipes',
        through='RecipeIngredients'
    )
    cooking_time = models.IntegerField(
        verbose_name='Время',
        validators=[MinValueValidator(MIN_COOKING_AMOUNT)]
    )
    is_favorited = models.BooleanField(default=False)
    in_shopping_cart = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'author'), name='unique_recipe'
            ),
        )

    def __str__(self):
        return self.name


class RecipeIngredients(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        related_name='recipeingredients',
        on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингедиент',
        related_name='recipeingredients',
        on_delete=models.CASCADE
    )
    amount = models.IntegerField(
        verbose_name='Количество',
        validators=[MinValueValidator(MIN_COOKING_AMOUNT)]
    )

    class Meta:
        verbose_name = 'Ингрдиент в рецепте'
        verbose_name_plural = 'Ингрдиенты в рецепте'
        constraints = (
            models.UniqueConstraint(
                fields=('ingredient',
                        'recipe'), name='unique_ingredient_recipe',
            ),
        )

    def __str__(self):
        return f'{self.recipe.name} - {self.ingredient.name}'
