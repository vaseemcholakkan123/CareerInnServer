# Generated by Django 4.2.2 on 2023-07-14 11:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Employer', '0004_alter_company_department'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='related_users',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='company',
            name='ceo',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='company_ceo', to=settings.AUTH_USER_MODEL),
        ),
    ]
