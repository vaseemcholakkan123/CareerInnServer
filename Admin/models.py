from django.db import models

# Create your models here.


class News(models.Model):
    title = models.CharField(max_length=100)
    posted_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-posted_time']


class Order(models.Model):
    type = models.CharField(choices=(("monthly","monthly"),("yearly","yearly")))
    payment_id = models.CharField(max_length=259)
    user = models.ForeignKey("User.User",on_delete=models.SET_DEFAULT,default="User deleted")
    payment_date = models.DateField(auto_now_add=True)
    price = models.PositiveIntegerField(null=True)

    def __str__(self) -> str:
        return self.user.username + '_' + self.type