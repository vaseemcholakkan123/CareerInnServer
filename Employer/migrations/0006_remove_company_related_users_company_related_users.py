# Generated by Django 4.2.2 on 2023-07-14 11:11

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Employer', '0005_company_related_users_alter_company_ceo'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='company',
            name='related_users',
        ),
        migrations.AddField(
            model_name='company',
            name='related_users',
            field=models.ManyToManyField(blank=True, null=True, to=settings.AUTH_USER_MODEL),
        ),
    ]
