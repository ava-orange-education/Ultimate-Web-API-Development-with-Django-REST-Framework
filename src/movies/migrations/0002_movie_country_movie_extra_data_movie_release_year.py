# Generated by Django 5.0.3 on 2024-04-01 18:39

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("movies", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="movie",
            name="country",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="movie",
            name="extra_data",
            field=models.JSONField(default=dict),
        ),
        migrations.AddField(
            model_name="movie",
            name="release_year",
            field=models.IntegerField(
                blank=True,
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(1888),
                    django.core.validators.MaxValueValidator(2024),
                ],
            ),
        ),
    ]
