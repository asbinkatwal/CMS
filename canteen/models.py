from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class User(AbstractUser):
    EMPLOYEE = 1
    CANTEEN_ADMIN = 2
    
    ROLE_CHOICES = (
        (EMPLOYEE, 'Employee'),
        (CANTEEN_ADMIN, 'Canteen Admin'),
    )
    
    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, default=EMPLOYEE)
    email = models.EmailField(unique=True)


class menu (models.Model):
    date= models.DateField( auto_now=False, auto_now_add=False)
    dishes= models.TextField()
    max_capacity=models.PositiveIntegerField()

    def __str__(self):
        return f"menu fro {self.date}"
    
class Vote(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    menu = models.ForeignKey(menu, on_delete=models.CASCADE)
    will_attend = models.BooleanField()
    voted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'menu') 