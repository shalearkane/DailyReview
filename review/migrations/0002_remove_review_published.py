# Generated by Django 4.1.3 on 2022-12-07 16:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("review", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="review",
            name="published",
        ),
    ]
