from django.core.validators import RegexValidator
from django.db import models
from autoslug import AutoSlugField

MAX_LENGHT_TAG = 200
MAX_LENGTH_COLOR = 7

class Tag(models.Model):

    name = models.CharField(
        verbose_name='Тег',
        max_length=MAX_LENGHT_TAG,
        unique=True
    )
    color = models.CharField(
        verbose_name = 'Цвет',
        max_length=MAX_LENGTH_COLOR,
        unique = True,
        validators = (
            RegexValidator(
                regex=r'^#([A-Fa-f0-9]{6})$',
            ),
        ),
    )
    slug = AutoSlugField(populate_from='name')

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'color'), name='unique_for_tag'
            ),
        )

    def __str__(self):
        return self.name
