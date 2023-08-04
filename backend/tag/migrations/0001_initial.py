# Generated by Django 4.2.3 on 2023-08-02 08:41

import autoslug.fields
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True, verbose_name='Тэг')),
                ('color', models.CharField(max_length=7, unique=True, validators=[django.core.validators.RegexValidator(regex='^#([A-Fa-f0-9]{6})$')], verbose_name='Цвет')),
                ('slug', autoslug.fields.AutoSlugField(editable=False, populate_from='name')),
            ],
            options={
                'verbose_name': 'Тэг',
                'verbose_name_plural': 'Тэги',
            },
        ),
        migrations.AddConstraint(
            model_name='tag',
            constraint=models.UniqueConstraint(fields=('name', 'color'), name='unique_for_tag'),
        ),
    ]