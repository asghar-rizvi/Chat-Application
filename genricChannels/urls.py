from django.contrib import admin
from django.urls import path
from chat.views import *
urlpatterns = [
    path('', signup,name= 'register'),
    path('login/', login_view, name = 'login'),
    
    path('chat/', chat, name = 'chat'),
    path('profile_page/', profile_page, name = 'chat'),
    
    path('searchUser/', searchUser, name = 'searchUser'),
    path('searchUserByName/', searchUserByName, name = 'searchUserByName'),
    path("send_friend_request/<str:username>/", send_friend_request, name="send_friend_request"),
    

    path("get_friends/", get_friends, name="get_friends"),
    path("remove-friend/", remove_friend, name="remove_friend"),
    path("get_friend_requests/", get_friend_requests, name="get_friend_requests"),
    path("handle_request/<int:request_id>/", handle_request, name="handle_request"),
    
    path("get_group_name/<str:friend_username>/", get_group_name, name="get_group_name"),

    path('network/',network , name ='network'),
    path('logout/',logout_user , name ='logout'),
    
    path('admin/', admin.site.urls),
]
