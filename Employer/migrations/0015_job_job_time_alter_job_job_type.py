# Generated by Django 4.2.2 on 2023-07-23 08:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Employer', '0014_applicant_about'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='job_time',
            field=models.CharField(choices=[('Full-time', 'Full-time'), ('Part-time', 'Part-time'), ('Contract', 'Contract'), ('Internship', 'Internship')], default='Full-time', max_length=100),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='job',
            name='job_type',
            field=models.CharField(choices=[('On-site', 'On-Site'), ('Remote', 'Remote'), ('Hybrid', 'Hybrid')], max_length=100),
        ),
    ]
