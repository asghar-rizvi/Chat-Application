function toggleView(section) {
    if (section === 'friends') {
        document.getElementById('friends-section').style.display = 'block';
        document.getElementById('requests-section').style.display = 'none';
        document.getElementById('show-friends').classList.add('active');
        document.getElementById('show-requests').classList.remove('active');
        loadFriends();
    } else {
        document.getElementById('friends-section').style.display = 'none';
        document.getElementById('requests-section').style.display = 'block';
        document.getElementById('show-friends').classList.remove('active');
        document.getElementById('show-requests').classList.add('active');
        loadRequests();
    }
}


document.addEventListener("DOMContentLoaded", function () {
    loadFriends(); // Load friends list by default
    updateFriendRequestCount();
});

function updateFriendRequestCount() {
    fetch('/get_friend_request_count/')
        .then(response => response.json())
        .then(data => {
            let requestCountElement = document.getElementById('request-count');
            if (requestCountElement) {
                if (data.count > 0) {
                    requestCountElement.classList.add('notification-bubble'); 
                    requestCountElement.textContent = data.count;
                } else {
                    requestCountElement.classList.remove('notification-bubble');
                }
            }
        })
        .catch(error => console.error('Error fetching friend request count:', error));
}

function loadFriends() {
    console.log('Loading Friends')
    fetch('/get_friends/')
    .then(response => response.json())
    .then(data => {

        let friends = Array.isArray(data) ? data : data.friends;

        if (!friends || !Array.isArray(friends)) {
            throw new Error("Invalid data format received!");
        }

        let friendList = document.getElementById("friends-section");
        friendList.innerHTML = '<h4>Your Friends</h4>';
        friends.forEach(friend => {
            console.log('Freindds...', friend.name)
            friendList.innerHTML += 
            `<div class="friend-item">
                <span>${friend.name}</span>
                <div>
                        <button class="btn btn-danger btn-sm" onclick="RemoveFriend(${friend.id})">Remove</button>
                </div>
            </div>`;
            
        });
    })
    .catch(error => console.error("Error fetching friends:", error));

}

function loadRequests() {
    fetch('/get_friend_requests/')
        .then(response => response.json())
        .then(data => {
            let requestList = document.getElementById("friend-requests");
            requestList.innerHTML = '';
            console.log(data.length)
            data.forEach(request => {
                requestList.innerHTML += `<div class="request-item">
                    <span>${request.name}</span>
                    <div>
                        <button class="btn btn-outline-primary btn-sm active" onclick="handleRequest(${request.id}, 'accept')">ACCEPT</button>
                        <button class="btn btn-danger btn-sm" onclick="handleRequest(${request.id}, 'reject')">REJECT</button>
                    </div>
                </div>`;
                
            });
        })
        .catch(error => console.error("Error fetching friend requests:", error));
}

function handleRequest(requestId, action) {
    fetch(`/handle_request/${requestId}/`,{
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken()  // Add CSRF token here
        },
        body: JSON.stringify({ action: action })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            loadRequests(); 
            updateFriendRequestCount();
            location.reload();
        } else {
            console.log(data)
            alert("Action failed!");
        }
    })
    .catch(error => console.error("Error processing request:", error));
    
    
}

function RemoveFriend(friendId) {
    console.log('friend...', friendId)
    fetch('/remove-friend/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': getCSRFToken() // Ensure CSRF token is included
        },
        body: `friend_id=${friendId}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            alert(data.message);
        }
    })
    .catch(error => console.error('Error:', error));
}



function getCSRFToken() {
    let csrfToken = null;
    document.cookie.split(';').forEach(cookie => {
        let [name, value] = cookie.trim().split('=');
        if (name === 'csrftoken') {
            csrfToken = value;
        }
    });
    return csrfToken;
}