# Generated by Django 4.2.2 on 2023-07-14 10:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Employer', '0003_alter_company_banner'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='department',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Employer.department'),
        ),
    ]
