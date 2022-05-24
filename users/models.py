from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.

# User Model
class User(AbstractUser):

    name = models.CharField(null=True, blank=True, max_length=128)
    email = models.EmailField(null=True, blank=True, max_length=128)
    password = models.CharField(null=True, blank=True, max_length=128)
    created_at = models.DateTimeField(null=True, auto_now_add=True)
    updated_at = models.DateTimeField(null=True, auto_now=True)

    def __str__(self):
        return str(self.email) + ' - id - ' + str(self.id)


# User token Model
class UserToken(models.Model):

    user = models.ForeignKey(User, related_name="user", on_delete=models.CASCADE)
    token = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.user) + ' UserTokenID ' + str(self.id)


# Notes Model
class Notes(models.Model):

    user = models.ForeignKey(User, related_name="note_user", on_delete=models.CASCADE)
    title = models.CharField(null=True, blank=True, max_length=128)
    desc = models.CharField(null=True, blank=True, max_length=128)
    tag = models.CharField(null=True, blank=True, max_length=128)
    created_at = models.DateTimeField(null=True, auto_now_add=True)
    updated_at = models.DateTimeField(null=True, auto_now=True)

    def __str__(self):
        return str(self.title) + ' - id - ' + str(self.id) + ' ' +str(self.user.email)