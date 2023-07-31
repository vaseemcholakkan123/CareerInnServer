# Generated by Django 4.2.2 on 2023-07-05 11:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('User', '0006_user_info_post_comment_report'),
    ]

    operations = [
        migrations.RenameField(
            model_name='report',
            old_name='Post',
            new_name='post',
        ),
        migrations.AlterUniqueTogether(
            name='report',
            unique_together={('user', 'post')},
        ),
        migrations.CreateModel(
            name='Like',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('liked', models.BooleanField(default=False)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='User.post')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'post')},
            },
        ),
    ]
