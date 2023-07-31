from django.db import models
from User.models import User,Skill
from django.core.exceptions import ValidationError

# Create your models here.

class Department(models.Model):
    title = models.CharField(max_length=200)
    
class Company(models.Model):
    name = models.CharField(max_length=100)
    ceo = models.OneToOneField(User,on_delete=models.CASCADE,related_name='company_ceo')
    banner = models.ImageField(upload_to='company_banners',blank=True)
    logo = models.ImageField(upload_to='company_logos',blank=True)
    excerpt = models.CharField(max_length=300)
    about = models.TextField()
    department = models.ForeignKey(Department,on_delete=models.CASCADE)
    location = models.CharField(max_length=250)
    employees_start = models.IntegerField()
    employees_end = models.IntegerField()

    def save(self, *args, **kwargs):
        if self.employees_start >= self.employees_end:
            raise ValidationError("Employees start must be less than employees end.")
        super().save(*args, **kwargs)

class JobResponsibilities(models.Model):
    name = models.CharField(max_length=200)

class JobRequirements(models.Model):
    name = models.CharField(max_length=200)

class JobQuestions(models.Model):
    name = models.CharField(max_length=300)
    answer_is_yes = models.BooleanField()

class Applicant(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    resume = models.FileField(upload_to='resumes')
    is_shortlisted = models.BooleanField(default=False)
    is_interviewed = models.BooleanField(default=False)
    is_informed = models.BooleanField(default=False)
    applied_on = models.DateTimeField(auto_now_add=True)
    is_selected = models.BooleanField(default=False)
    interview_date = models.CharField(max_length=100)
    interview_time = models.CharField(max_length=100)
    about = models.TextField()


class Job(models.Model):
    name = models.CharField(max_length=200)
    company = models.ForeignKey(Company,on_delete=models.CASCADE)
    description = models.TextField()
    job_type = models.CharField(choices=(('On-Site','On-Site'),('Remote','Remote'),('Hybrid','Hybrid')),max_length=100)
    job_time = models.CharField(choices=(('Full-time','Full-time'),('Part-time','Part-time'),('Contract','Contract'),('Internship','Internship')),max_length=100)
    responsibilities = models.ManyToManyField(JobResponsibilities)
    requirements = models.ManyToManyField(JobRequirements)
    is_closed = models.BooleanField(default=False)
    posted_on = models.DateTimeField(auto_now_add=True)
    expected_salary = models.PositiveBigIntegerField()
    skills_required = models.ManyToManyField(Skill)
    questions = models.ManyToManyField(JobQuestions)
    applicants = models.ManyToManyField(Applicant,blank=True)

    
class RejectedApplicant(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    job = models.ForeignKey(Job,on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user','job')

