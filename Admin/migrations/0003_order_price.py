# Generated by Django 4.2.2 on 2023-08-11 07:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Admin', '0002_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='price',
            field=models.PositiveIntegerField(null=True),
        ),
    ]
