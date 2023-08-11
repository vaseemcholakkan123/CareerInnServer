from django.db import models

from django.contrib.auth.models import AbstractUser

# Create your models here.


class Skill(models.Model):
    title = models.CharField(max_length=200,unique=True)



class User(AbstractUser):
    banner = models.ImageField(upload_to='banners',blank=True,null=True)
    profile = models.ImageField(upload_to="profiles", null=True)
    email = models.EmailField(null=False,unique=True)  
    otp = models.BigIntegerField(null=True)
    otp_delay = models.TimeField(auto_now=True)
    otp_limit = models.IntegerField(default=1)
    is_blocked = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    info  = models.CharField(max_length=100,null=True,blank=True)
    mobile = models.BigIntegerField(null=True,blank=True)
    location = models.CharField(null=True,blank=True)
    skills = models.ManyToManyField(Skill,blank=True)
    company = models.ForeignKey('Employer.Company', on_delete=models.SET_NULL, null=True, blank=True)
    is_premium_user = models.BooleanField(default=False)
    resume = models.FileField(upload_to='resume',null=True)
    premium_end_date = models.DateTimeField(null=True,blank=True)

class Education(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    institute = models.CharField(max_length=250)
    subject = models.CharField(max_length=200)
    graduated_year = models.PositiveIntegerField() 

class Experience(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    company = models.OneToOneField('Employer.company',on_delete=models.CASCADE,related_name='working_company')
    position = models.CharField(max_length=200)
    year_from = models.IntegerField()
    year_to = models.IntegerField()
    still_working = models.BooleanField(default=False)

class Post(models.Model):
    posted_user = models.ForeignKey(User,on_delete=models.CASCADE,null=False)
    content_image = models.ImageField(upload_to='post_images',null=False,blank=True)
    content_text = models.TextField(null=False)
    likes = models.IntegerField(default = 0) 
    posted_on = models.DateTimeField(auto_now_add=True)


class CommentManager(models.Manager):
    def by_post(self,**kwargs):
        post = kwargs.get('post_id')
        return self.get_queryset().filter(post = Post.objects.get(id=post))

class comment(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    post = models.ForeignKey(Post,on_delete=models.CASCADE,related_name='post_comments')
    comment_text = models.TextField(null=False)
    commented_on = models.DateTimeField(auto_now_add=True)

    objects = CommentManager()

class Like(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    post = models.ForeignKey(Post,on_delete=models.CASCADE)
    liked = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'post')

class Report(models.Model):
    post = models.ForeignKey(Post,on_delete=models.CASCADE,related_name='post_reports')
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    content = models.CharField(max_length=500)

    class Meta:
        unique_together = ('user', 'post')

class SavedPosts(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    post = models.ManyToManyField(Post)

class connections(models.Model):
    user= models.ForeignKey(User,on_delete=models.CASCADE,related_name='user')
    following = models.ManyToManyField(User,related_name='following')

    # class Meta:
    #     unique_together = ('user' , 'follower')

class Project(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    name = models.CharField(max_length=100,null=False,blank=False)
    description = models.CharField(max_length=250,null=False,blank=False)
    link = models.CharField(max_length=200,null=False,blank=False)

    class Meta:
        unique_together = ('user','name')

class Notification(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    content = models.CharField(max_length=200)
    link_thread = models.CharField(max_length=100)
    type = models.CharField(choices=(("Post","Post"),("Job","Job"),("Connection","Connection")))
    created = models.DateTimeField(auto_now_add=True)
    rel_img = models.CharField(max_length=500)
    is_read=models.BooleanField(default=False)