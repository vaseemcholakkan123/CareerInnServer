from django.db import models

# Create your models here.


class News(models.Model):
    title = models.CharField(max_length=100)
    posted_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-posted_time']
