# Generated by Django 4.2.2 on 2023-07-14 12:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Employer', '0006_remove_company_related_users_company_related_users'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='company',
            name='related_users',
        ),
    ]
