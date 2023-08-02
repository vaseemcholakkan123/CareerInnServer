from django.db.models.signals import post_save
from django.dispatch import receiver
from django.dispatch import Signal
from .models import Applicant,Job,RejectedApplicant
from User.models import Notification

progress_signal  = Signal()


@receiver(progress_signal, sender = Applicant, dispatch_uid="progress_signal")
def send_application_progress(sender,instance,created,**kwargs):
    job_name = kwargs['job_name']
    usr = instance.user
    interview_starting = kwargs.get('starting_interview',None)
    if created:
        Notification.objects.create(user=usr,rel_img=kwargs['thread_img'],content=f'Application submitted for the job {job_name}',link_thread=kwargs['job_id'],type='Job')
    else:
        if instance.is_shortlisted and not instance.is_informed:
            Notification.objects.create(user=usr,rel_img=kwargs['thread_img'],content=f'Application shortlisted for the job {job_name}',link_thread=kwargs['job_id'],type='Job')
        elif instance.is_selected:
            Notification.objects.create(user=usr,rel_img=kwargs['thread_img'],content=f"Congratulations you're selected for the job {job_name}",link_thread=kwargs['job_id'],type='Job')
        elif instance.is_interviewed:
            Notification.objects.create(user=usr,rel_img=kwargs['thread_img'],content=f'Interview  results pending for the job {job_name}',link_thread=kwargs['job_id'],type='Job')
        elif instance.is_informed and not interview_starting:
            Notification.objects.create(user=usr,rel_img=kwargs['thread_img'],content=f'Interview sheduled on {instance.interview_date} at {instance.interview_time} for the job {job_name}, Be available at that time',link_thread=kwargs['job_id'],type='Job')
        elif instance.is_informed and interview_starting:
            Notification.objects.create(user=usr,rel_img=kwargs['thread_img'],content=f'Interview  has started for the job {job_name}, Click to join interview',link_thread='redirect',type='Job')


        
            
@receiver(post_save , sender = RejectedApplicant)
def application_rejected_notification(sender,created,instance,**kwargs):
    if created:
        Notification.objects.create(user=instance.user,rel_img=instance.job.company.logo.url,content=f'Application rejected for the job {instance.job.name}',link_thread=instance.job.id,type='Job')


