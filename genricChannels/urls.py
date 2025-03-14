from django.contrib import admin
from django.urls import path
from chat.views import *
urlpatterns = [
    path('', signup,name= 'register'),
    path('login/', login_view, name = 'login'),
    path('chat/', chat, name = 'chat'),
    path('searchUser/', searchUser, name = 'searchUser'),
    path('searchUserByName/', searchUserByName, name = 'searchUserByName'),
    path("send_friend_request/<str:username>/", send_friend_request, name="send_friend_request"),

    path('network/',network , name ='network'),
    
    path('admin/', admin.site.urls),
]
