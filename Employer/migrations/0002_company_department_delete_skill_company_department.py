# Generated by Django 4.2.2 on 2023-07-13 11:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('User', '0021_skill_alter_user_skills'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Employer', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('banner', models.ImageField(upload_to='company_banners')),
                ('logo', models.ImageField(upload_to='company_logos')),
                ('excerpt', models.CharField(max_length=300)),
                ('about', models.TextField()),
                ('location', models.CharField(max_length=250)),
                ('employees_start', models.IntegerField()),
                ('employees_end', models.IntegerField()),
                ('ceo', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
            ],
        ),
        migrations.DeleteModel(
            name='Skill',
        ),
        migrations.AddField(
            model_name='company',
            name='department',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='Employer.department'),
        ),
    ]
