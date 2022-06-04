import algoliasearch_django as algol
from algoliasearch_django import AlgoliaIndex
from algoliasearch_django.decorators import register

from .models import User, Room, Message, Topic

@register(User)
class UserIndex(AlgoliaIndex):
    fields = ["name", "bio", "avatar", "username", "pk"]

algol.register(Room)
algol.register(Topic)
algol.register(Message)
