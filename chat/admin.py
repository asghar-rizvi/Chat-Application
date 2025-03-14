from django.contrib import admin
from .models import *

admin.site.register(FriendRequest)
admin.site.register(Friendship)
admin.site.register(Group)
admin.site.register(ChatMessage)