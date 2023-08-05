from django.db.models.signals import post_save
from django.dispatch import receiver,Signal
from .models import Post,Notification,connections
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


followNotification = Signal()
post_banned = Signal()
app_channel_layer = get_channel_layer()

@receiver(post_save, sender=Post)
def send_post_notification_to_followers(sender,instance,created,**kwargs):
   if created:
        threads = connections.objects.filter(following__in=[instance.posted_user.id])
        url = instance.content_image.url if instance.content_image else instance.posted_user.profile.url if instance.posted_user.profile else None
        if threads.exists():
            for thread in threads:
                Notification.objects.create(user=thread.user,rel_img=url,content=f'Your friend {instance.posted_user.username} has posted something',link_thread=str(instance.id),type='Post')

                socket_name = f'user_notification_{thread.user.id}'
                event = {
                    'type' : 'notification_message',
                }

                async_to_sync(app_channel_layer.group_send)(socket_name, event)
        


@receiver(followNotification,sender= connections , dispatch_uid="followNotification")
def send_follow_notification(sender,created,instance,**kwargs):
    target = kwargs['target']
    if created:
        Notification.objects.create(user=target,rel_img=instance.user.profile.url if instance.user.profile else '',content=f'{instance.user}  has started following you',link_thread=str(instance.user.id),type='Connection')

        socket_name = f'user_notification_{target.id}'
        event = {
            'type' : 'notification_message',
        }
        async_to_sync(app_channel_layer.group_send)(socket_name, event)



@receiver(post_banned,sender= Post , dispatch_uid="followNotification")
def send_post_ban_notification(sender,deleted,instance,**kwargs):

    if deleted:
        Notification.objects.create(user=instance.posted_user,rel_img=instance.content_image if instance.content_image else '',content='your post is deleted by admin due to reports',link_thread='l',type='Post')
        socket_name = f'user_notification_{instance.posted_user.id}'
        event = {
            'type' : 'notification_message',
        }

        async_to_sync(app_channel_layer.group_send)(socket_name, event)
