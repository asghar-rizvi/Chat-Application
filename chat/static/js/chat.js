document.addEventListener("DOMContentLoaded", function () {
    loadFriendsList();
    


});
function loadFriendsList() {
    fetch('/get_friends/')
        .then(response => response.json())
        .then(data => {
            let friendsList = document.getElementById("friends-list");
            friendsList.innerHTML = "";
            data.forEach(friend => {
                let friendItem = `<div class="friend-item" onclick="fetchGroupName('${friend.name}')">${friend.name}</div>`;
                friendsList.innerHTML += friendItem;
            });
        })
        .catch(error => console.error("Error loading friends:", error));
}
function fetchGroupName(friendUsername) {
    fetch(`/get_group_name/${friendUsername}/`)
        .then(response => response.json())
        .then(data => {
            if (data.group_name) {
                startWebSocket(data.group_name, friendUsername);
            }
        })
        .catch(error => console.error("Fetch error:", error));
}

function startWebSocket(groupName, friendUsername) {
    const usernameElement = document.getElementById("chat-username");
    const chatMesssages = document.getElementById("chat-messages");
    const sendButton = document.getElementById("send-button");
    const messageInput = document.getElementById("message-input");
    const currentUser = document.getElementById("current-user").dataset.username;
    const userDiv = document.getElementById('current-user');
    const username = userDiv.getAttribute('data-username');
    console.log(username);
    console.log('Inside Start WebSocket...', groupName, friendUsername)
    if (!usernameElement || !chatMesssages || !sendButton || !messageInput) {
        console.error("Chat UI elements not found!");
        return;
    }

    usernameElement.innerText = friendUsername;
    chatMesssages.innerHTML = ""; // Clear previous messages

    const wsUrl = `ws://${window.location.host}/ws/chat/${groupName}/`;
    const chatSocket = new WebSocket(wsUrl);

    chatSocket.onopen = function () {
        console.log("WebSocket connected for group:", groupName);
    };

    chatSocket.onmessage = function (event) {
        const data = JSON.parse(event.data);
        console.log('Inside On message:', data.type);
    
        if (data.type === 'chat_history') {
            // Clear previous messages
            chatMesssages.innerHTML = ""; 
            
            data.messages.forEach(msg => {
                let msgElement = document.createElement("div");
                msgElement.classList.add("message");
                msgElement.classList.add(msg.user === currentUser ? "sent" : "received");
                msgElement.innerHTML = `<strong>${msg.user}:</strong> ${msg.message}`;
        
                chatMesssages.appendChild(msgElement);
                chatMesssages.scrollTop = chatMesssages.scrollHeight;
        
                // Apply the animation immediately after adding
                requestAnimationFrame(() => {
                    msgElement.classList.add("show");  
                });
            });
        
        } else if (data.type === 'chat_message') {
            let msgElement = document.createElement("div");
            msgElement.classList.add("message");
            console.log('DATA USER: ', data.user)
            if (data.user === username) {
                console.log('Matched')
                msgElement.classList.add("sent"); // Add 'sent' class for messages sent by the current user
            } else {
                console.log('Not Matched')
                msgElement.classList.add("received"); // Add 'received' class for messages from others
            }
        
            // Add the message content to the element
            msgElement.innerHTML = `<strong>${data.user}:</strong> ${data.message}`;
        
            // Append the message element to the chat container
            chatMesssages.appendChild(msgElement);
        
            // Scroll to the bottom of the chat container
            chatMesssages.scrollTop = chatMesssages.scrollHeight;
        }
    };
    

    chatSocket.onclose = function () {
        console.log("WebSocket disconnected.");
    };

    sendButton.onclick = function () {
        let message = messageInput.value.trim();

        if (message !== "") {
            chatSocket.send(JSON.stringify({ message: message }));
            messageInput.value = "";
        }
    };

}