# Generated by Django 4.2.2 on 2023-07-21 06:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Employer', '0012_applicant_is_selected'),
    ]

    operations = [
        migrations.AddField(
            model_name='applicant',
            name='interview_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
