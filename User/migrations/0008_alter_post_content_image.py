# Generated by Django 4.2.2 on 2023-07-05 12:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('User', '0007_rename_post_report_post_alter_report_unique_together_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='content_image',
            field=models.ImageField(upload_to='post_images'),
        ),
    ]
