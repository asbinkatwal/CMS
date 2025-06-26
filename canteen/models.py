from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class User(AbstractUser):
    EMPLOYEE = 1
    CANTEEN_ADMIN = 2
    SUPER_USER =3
    
    ROLE_CHOICES = (
        (EMPLOYEE, 'Employee'),
        (CANTEEN_ADMIN, 'Canteen Admin'),
        (SUPER_USER,'Super User')
    )
    
    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, default=SUPER_USER)
    email = models.EmailField(unique=True)
    address = models.JSONField(default=dict ,blank=True , null=True)

    def save(self, *args, **kwargs):
        if self.pk is None and self.role == self.CANTEEN_ADMIN:
            self.is_active = False
        super().save(*args, **kwargs)

class menu (models.Model):
    date= models.DateField( auto_now=False, auto_now_add=False)
    dishes= models.TextField()
    max_capacity=models.PositiveIntegerField()

    def __str__(self):
        return f"menu for {self.date}"
    
class Vote(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    menu = models.ForeignKey(menu, on_delete=models.CASCADE)
    will_attend = models.BooleanField()
    voted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'menu') 