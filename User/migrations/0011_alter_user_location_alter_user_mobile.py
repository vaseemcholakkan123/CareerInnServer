# Generated by Django 4.2.2 on 2023-07-10 05:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('User', '0010_user_location_user_mobile_savedposts'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='location',
            field=models.CharField(null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='mobile',
            field=models.IntegerField(null=True),
        ),
    ]
