function searchUsers() {
    let searchInput = document.getElementById("search");
    if (!searchInput) {
        console.error("Search input field not found!");
        return;
    }

    let query = searchInput.value.trim();
    let userList = document.querySelector(".list-group");

    if (!userList) {
        console.error("User list container not found!");
        return;
    }

    if (query === "") {
        fetch("/searchUser/")
            .then(response => response.text()) // Fetch HTML response instead of JSON
            .then(html => {
                let parser = new DOMParser();
                let doc = parser.parseFromString(html, "text/html");
                let newUserList = doc.querySelector(".list-group");
                if (newUserList) {
                    userList.innerHTML = newUserList.innerHTML; // Replace content
                }
            })
            .catch(error => console.error("Error resetting users:", error));
        return;
    }

    // ✅ Continue with normal search if query is not empty
    fetch(`/searchUserByName/?q=${encodeURIComponent(query)}`, {
        method: "GET",
        headers: { "X-Requested-With": "XMLHttpRequest" }
    })
    .then(response => response.json())
    .then(data => {
        userList.innerHTML = ""; 

        if (!Array.isArray(data)) {
            console.error("Invalid response format:", data);
            return;
        }

        if (data.length === 0) {
            userList.innerHTML = `<p class="text-muted p-2">No users found.</p>`;
            return;
        }

        data.forEach(user => {
            let userItem = document.createElement("div");
            userItem.classList.add("list-group-item", "d-flex", "justify-content-between", "align-items-center", "user-item");
        
            let userName = document.createElement("span");
            userName.classList.add("username");
            userName.textContent = user.username;  // Display searched user’s username
        
            let button = document.createElement("button");
            button.type = "button";  // Prevent form submission
            button.classList.add("btn", "btn-primary");
            button.textContent = user.request_sent ? "Request Sent" : "Send Request";
            button.disabled = user.request_sent;
            
            // Pass receiver's username (searched user)
            button.onclick = () => sendFriendRequest(user.username, button);
        
            userItem.appendChild(userName);
            userItem.appendChild(button);
            userList.appendChild(userItem);
        });
        
    })
    .catch(error => console.error("Error fetching users:", error));
}


function sendFriendRequest(username, button) {
    console.log("Sending Request...", username);

    fetch(`/send_friend_request/${username}/`, {
        method: "POST",
        headers: {
            "X-CSRFToken": getCSRFToken(), // ✅ Ensure CSRF token is included
            "Content-Type": "application/json",
        },
        body: JSON.stringify({})
    })
    .then(response => response.json())
    .then(data => {
        console.log("Response:", data);

        showMessage(data.message, data.status);

        if (data.status === "success") {
            button.textContent = "Request Sent";
            button.disabled = true;
            button.classList.remove("btn-primary");
            button.classList.add("btn-secondary");
        }
    })
    .catch(error => console.error("Error sending request:", error));
}


function showMessage(message, status) {
    let messageDiv = document.getElementById("message-box");
    console.log('inside Showmessage')
    if (!messageDiv) {
        messageDiv = document.createElement("div");
        messageDiv.id = "message-box";
        messageDiv.className = "message-box";
        document.body.appendChild(messageDiv);
        console.log('first if')
    }

    messageDiv.textContent = message;
    messageDiv.classList.remove("alert-success", "alert-warning", "alert-danger", "show");
    console.log('first out if')

    if (status === "success") {
        messageDiv.classList.add("alert-success");
    } else if (status === "warning") {
        messageDiv.classList.add("alert-warning");
    } else {
        messageDiv.classList.add("alert-danger");
    }

    // Show the message box
    messageDiv.classList.add("show");
    console.log('first animination')
    // Hide the message box after 3 seconds
    setTimeout(() => {
        messageDiv.classList.remove("show");
        setTimeout(() => { messageDiv.remove(); }, 500); // Wait for the animation to finish
    }, 3000);
}

function getCSRFToken() {
    let csrfTokenInput = document.querySelector("[name=csrfmiddlewaretoken]");
    return csrfTokenInput ? csrfTokenInput.value : "";
}