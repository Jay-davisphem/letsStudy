from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings                                                                                 
from django.db.models.signals import post_save                                                                   
from django.dispatch import receiver                                                                             
from rest_framework.authtoken.models import Token  

class User(AbstractUser):
    name = models.CharField(max_length=200, null=True)
    email = models.EmailField(unique=True, null=True)
    bio = models.TextField(null=True)
    avatar = models.ImageField(null=True, default="avatar.svg")
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.username

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)

class Room(models.Model):
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    topic = models.ForeignKey("Topic", on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    participants = models.ManyToManyField(User, related_name="participants", blank=True)
    updated = models.DateTimeField(auto_now=True)  # saves everytime
    created = models.DateTimeField(auto_now_add=True)  # once on creation

    class Meta:
        ordering = ["-updated", "-created"]

    def __str__(self):
        return str(self.name)


class Topic(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    body = models.TextField()
    updated = models.DateTimeField(auto_now=True)  # saves everytime
    created = models.DateTimeField(auto_now_add=True)  # once on creation

    class Meta:
        ordering = ["-updated", "-created"]

    def __str__(self):
        elipsis = ""
        if len(self.body) > 50:
            elipsis = "..."
        return f"{self.body[:50]}{elipsis}"
