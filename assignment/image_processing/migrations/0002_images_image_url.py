# Generated by Django 5.1 on 2024-08-31 15:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('image_processing', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='images',
            name='image_url',
            field=models.URLField(null=True),
        ),
    ]
