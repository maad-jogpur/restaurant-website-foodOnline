from django.db.models.signals import post_save,pre_save
from django.dispatch import receiver

from . models import User,UserProfile


@receiver(post_save,sender=User)
def post_save_creating_userprofile_receiver(sender,instance,created,**kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        try:
            UserProfile.objects.get(user=instance)
        except:
            UserProfile.objects.create(user=instance)
    

@receiver(pre_save,sender=User)
def pre_save_receiver(sender,instance,**kwargs):
    pass
