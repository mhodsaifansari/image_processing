# Generated by Django 5.1 on 2024-09-01 08:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('image_processing', '0003_processingrequest_completed_at_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='processingrequest',
            name='image_count',
            field=models.PositiveIntegerField(null=True),
        ),
    ]
