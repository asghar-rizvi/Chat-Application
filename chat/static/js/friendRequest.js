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
});

function loadFriends() {
    console.log('Loading Friends')
    /*fetch('/get_friends/')
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => console.log("Fetched Friends:", data))
    .catch(error => console.error("Error fetching friends:", error));*/

    fetch('/get_friends/')
    .then(response => response.json())
    .then(data => {
        console.log("Fetched Friends:", data);

        // If `data` is an array instead of an object with `friends`
        let friends = Array.isArray(data) ? data : data.friends;

        if (!friends || !Array.isArray(friends)) {
            throw new Error("Invalid data format received!");
        }

        let friendList = document.getElementById("friends-section");
        friendList.innerHTML = '<h4>Your Friends</h4>';
        friends.forEach(friend => {
            friendList.innerHTML += `<div class="request-item">
                <span>${friend.name}</span>
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
            data.forEach(request => {
                requestList.innerHTML += `<div class="request-item">
                    <span>${request.name}</span>
                    <div>
                        <button class="btn btn-success btn-sm" onclick="handleRequest(${request.id}, 'accept')">ACCEPT</button>
                        <button class="btn btn-danger btn-sm" onclick="handleRequest(${request.id}, 'reject')">REJECT</button>
                    </div>
                </div>`;
            });
        })
        .catch(error => console.error("Error fetching friend requests:", error));
}

function handleRequest(requestId, action) {
    fetch(`/handle_request/${requestId}/`, {
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
        } else {
            console.log(data)
            alert("Action failed!");
        }
    })
    .catch(error => console.error("Error processing request:", error));
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

loadRequests();