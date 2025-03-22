from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .models import *
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
import json
from django.db.models import Q


def signup(request):
    if request.method == "POST":
        data = request.POST
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Account with this username already exists')
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Account with this email already exists')
            return redirect('register')

        user = User.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
            password=password  
        )

        messages.success(request, 'Account created successfully! Please log in.')
        return redirect('login')

    return render(request, 'register.html')



def login_view(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, 'No account exists with this email.')
            return redirect('register')

        user = authenticate(username=user.username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('chat')
        else:
            messages.error(request, 'Email or password is incorrect.')
            return redirect('login')
    return render(request, 'login.html')


@login_required
def chat(request):
    user = request.user.username
    return render(request, 'chat.html', {'user':user})


@login_required
def network(request):
    return render(request,'friendRequest.html')


@login_required
def searchUser(request):
    excluded_users = FriendRequest.objects.filter(
        sender=request.user, status__in=["accepted", "pending"]
    ).values_list("receiver", flat=True)

    # Fetch users excluding self and those in `excluded_users`
    users = User.objects.exclude(username=request.user.username).exclude(id__in=excluded_users)[:15]
    total_users = len(User.objects.exclude(username=request.user.username))

    users_list = []
    for user in users:
        request_sent = FriendRequest.objects.filter(sender=request.user, receiver=user).exists()
        users_list.append({
            'id': user.id,
            'username': user.username,
            'full_name': f"{user.first_name} {user.last_name}",
            'request_sent': request_sent
        })
    return render(request, "SearchUser.html", {"users": users_list, 'totalUsers' : total_users})


@login_required
def searchUserByName(request):
    query = request.GET.get('q', '').strip()  # Trim whitespace
    if query:
        users = User.objects.filter(username__icontains=query).exclude(id=request.user.id)[:10]
    else:
        return JsonResponse({'error': 'No user found'}, status=400)  # Proper error response
    
    users_list = []
    for user in users:
        request_sent = FriendRequest.objects.filter(sender=request.user, receiver=user).exists()
        users_list.append({
            'id': user.id,
            'username': user.username,
            'full_name': f"{user.first_name} {user.last_name}",
            'request_sent': request_sent
        })
    
    return JsonResponse(users_list, safe=False)
    
    
@login_required
def send_friend_request(request, username):
    if request.method == "POST":
        receiver = get_object_or_404(User, username=username)
        sender = request.user
        
        # Check if request already exists
        if FriendRequest.objects.filter(sender=sender, receiver=receiver).exists():
            print('Already Exists')
            return JsonResponse({"message": "Friend request already sent!", "status": "warning"})

        # Save new friend request
        FriendRequest.objects.create(sender=sender, receiver=receiver)
        print("Request being Send")
        return JsonResponse({"message": "Friend request sent!", "status": "success"})
    

    return JsonResponse({"message": "Invalid request!", "status": "error"})
    
     
  
    
@login_required
def get_friends(request):
    """Returns a list of friends for the logged-in user."""
    print('get friends')
    user = request.user
    friends = Friendship.objects.filter(user1=user) | Friendship.objects.filter(user2=user)
    print('Inside gET friends')
    print(friends)
    friend_list = [
        {"id": f.user2.id if f.user1 == user else f.user1.id, 
         "name": f.user2.username if f.user1 == user else f.user1.username}
        for f in friends
    ]
    print('Friends of the user:...', friend_list)
    return JsonResponse({"friends": friend_list})


@login_required
def get_friend_requests(request):
    """Returns a list of pending friend requests for the logged-in user."""
    user = request.user
    requests = FriendRequest.objects.filter(receiver=user, status="pending")
    
    request_list = [{"id": req.id, "name": req.sender.username} for req in requests]
    
    return JsonResponse(request_list, safe=False)

@login_required
def remove_friend(request):
    if request.method == "POST":
        friend_id = request.POST.get("friend_id")
        user = request.user

        try:
            # Find the friendship where user1 and user2 match (friendship is mutual)
            friendship = Friendship.objects.filter(
                (Q(user1=user) & Q(user2_id=friend_id)) | (Q(user1_id=friend_id) & Q(user2=user))
            ).first()

            if friendship:
                friendship.delete()
                return JsonResponse({"success": True, "message": "Friend removed successfully."})
            else:
                return JsonResponse({"success": False, "message": "Friendship not found."}, status=404)

        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)}, status=500)

    return JsonResponse({"success": False, "message": "Invalid request."}, status=400)


@login_required
def handle_request(request, request_id):
    """Handles accepting or rejecting friend requests."""

    if request.method == "POST":
        try:
            data = json.loads(request.body)  
            action = data.get("action")  
            print(action)
            if not action:
                return JsonResponse({"success": False, "message": "Action missing"}, status=400)

            friend_request = get_object_or_404(FriendRequest, id=request_id, receiver=request.user)

            if action == "accept":
                Friendship.objects.create(user1=friend_request.sender, user2=request.user)
                friend_request.status = "accepted"
                friend_request.save()
                
                user1, user2 = sorted([friend_request.sender, request.user], key=lambda x: x.username)
                groupname = user1.username + '_' + user2.username
                print(groupname)
                Group.objects.create(group_name=groupname, user1=user1, user2=user2)
                return JsonResponse({"success": True, "message": "Friend request accepted!"})

            elif action == "reject":
                friend_request.status = "rejected"
                friend_request.save()
                return JsonResponse({"success": True, "message": "Friend request rejected!"})

        except json.JSONDecodeError:
            return JsonResponse({"success": False, "message": "Invalid JSON"}, status=400)

    return JsonResponse({"success": False, "message": "Invalid request"}, status=400)
    

@login_required
def chat_view(request):
    return render(request, "chat.html")

@login_required
def get_friends(request):
    friends = Friendship.objects.filter(user1=request.user) | Friendship.objects.filter(user2=request.user)
    friend_list = [
        {"id": f.user2.id if f.user1 == request.user else f.user1.id, "name": f.user2.username if f.user1 == request.user else f.user1.username}
        for f in friends
    ]
    return JsonResponse(friend_list, safe=False)

@login_required
def get_group_name(request, friend_username):
    try:
        friend = User.objects.get(username=friend_username)
        user1, user2 = sorted([request.user, friend], key=lambda x: x.username)
        group = Group.objects.get(user1=user1, user2=user2)
        print(group)
        return JsonResponse({"group_name": group.group_name})
    except Group.DoesNotExist:
        return JsonResponse({"error": "Group not found"}, status=404)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)


@login_required
def profile_page(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)  # Parse JSON data
            request.user.first_name = data.get("first_name", request.user.first_name)
            request.user.last_name = data.get("last_name", request.user.last_name)
            request.user.email = data.get("email", request.user.email)
            if data.get("password"):
                request.user.set_password(data["password"])
            request.user.save()

            messages.success(request, "Profile updated successfully!")  # Success message

            return JsonResponse({
                "message": "Profile updated successfully!",
                "status": "success",
                "message_type": "success"
            })  # ✅ Send message in JSON response

        except Exception as e:
            messages.error(request, "Error updating profile!")  # Error message
            return JsonResponse({
                "message": "Error updating profile!",
                "status": "error",
                "message_type": "error"
            })  # ✅ Send error message in JSON response

    return render(request, "profile.html", {"user": request.user})

def logout_user(request):
    logout(request)  
    return redirect('login') 