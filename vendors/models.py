from django.db import models
from datetime import time,date,datetime

from accounts.models import User,UserProfile
from accounts.utils import send_notification
# Create your models here.

class Vendor(models.Model):
    user = models.OneToOneField(User,related_name='user',on_delete=models.CASCADE)
    user_profile = models.OneToOneField(UserProfile,related_name='userprofile',on_delete=models.CASCADE)
    vendor_name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=100,unique=True)
    vendor_license = models.ImageField(upload_to='vendor/license')
    is_approved = models.BooleanField(default=False)

    created_at =models.DateField(auto_now_add=True)
    updated_at =models.DateField(auto_now=True)


    def __str__(self):
        return self.vendor_name
    
    def is_open(self):
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")

        today_date = date.today()
        today = today_date.isoweekday()
        current_day_hours = OpeningHour.objects.filter(vendor=self,day = today)

        is_open = None
        for i in current_day_hours:
            start = str(datetime.strptime(i.from_hour, "%I:%M %p").time())
            end = str(datetime.strptime(i.to_hour, "%I:%M %p").time())

            if current_time > start and current_time < end:
                is_open = True
                break
            else:
                is_open = False

        return is_open

    def save(self,*args, **kwargs):
        if self.pk is not None:
            original_data = Vendor.objects.get(pk = self.pk)
            
            if original_data.is_approved != self.is_approved:
                email_template = 'accounts/email/admin_approval_email.html'
                context = {
                    'user':self.user,
                    'is_approved': self.is_approved,
                }
                if self.is_approved == True:
                    mail_subject = "Congratulations! Your restaurant has been approved."
                    send_notification(mail_subject, email_template, context)
                    
                else:
                    mail_subject = "We're sorry! You are not eligible for publishing your food menu on our marketplace."
                    send_notification(mail_subject, email_template, context)
        return super().save(*args, **kwargs)

DAYS = [
    (1, ("Monday")),
    (2, ("Tuesday")),
    (3, ("Wednesday")),
    (4, ("Thursday")),
    (5, ("Friday")),
    (6, ("Saturday")),
    (7, ("Sunday")),
]

FROM_TO_HOURS_24 = [(time(h,m).strftime('%I:%M %p'), time(h,m).strftime('%I:%M %p')) for h in range(0,24)  for m in(0,30) ]

class OpeningHour(models.Model):
    vendor = models.ForeignKey(Vendor,on_delete=models.CASCADE)
    from_hour = models.CharField(choices=FROM_TO_HOURS_24)
    to_hour = models.CharField(choices=FROM_TO_HOURS_24)
    day = models.IntegerField(choices=DAYS)
    is_closed = models.BooleanField(default=False)

    class Meta:
        ordering = ('day','-from_hour')
        unique_together = ('vendor','day','from_hour','to_hour')

    