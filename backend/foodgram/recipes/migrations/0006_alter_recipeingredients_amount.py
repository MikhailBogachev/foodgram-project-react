# Generated by Django 3.2 on 2023-08-14 09:57

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0005_auto_20230814_1418'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipeingredients',
            name='amount',
            field=models.IntegerField(validators=[django.core.validators.MinValueValidator(1, 'Оценка должна быть не меньше 1!')]),
        ),
    ]
