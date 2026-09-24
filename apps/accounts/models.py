from django.contrib.auth.models import AbstractUser
from django.db import models



class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)

    phone_number = models.CharField(
        max_length=15,
        unique=True,
        null=True,
        blank=True
    )

    email_verified = models.BooleanField(default=False)
    
    timezone = models.CharField(max_length=50,default="Asia/Kolkata")
    
    pending_email = models.EmailField(null=True,blank=True)
    pending_email_token = models.CharField(max_length=255,null=True,blank=True)


    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email


