document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("updateForm");
    const inputs = form.querySelectorAll("input");
    const updateButton = document.querySelector(".btn-update");

    // Enable Update button on input change
    inputs.forEach(input => {
        input.addEventListener("input", () => {
            updateButton.disabled = false;
            updateButton.classList.add("active");
        });
    });

    // Handle form submission using Fetch API
    form.addEventListener("submit", async function (event) {
        event.preventDefault();
        const formData = {
            first_name: document.getElementById("first_name").value,
            last_name: document.getElementById("last_name").value,
            email: document.getElementById("email").value,
            password: document.getElementById("password").value
        };

        const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value;

        try {
            const response = await fetch("{% url 'chat' %}", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken
                },
                body: JSON.stringify(formData)
            });

            const data = await response.json();
            if (data.status === "success") { 
                updateButton.disabled = true;
                updateButton.classList.remove("active");
                location.reload();

            } else {
                alert("Error: " + data.message);
            }
        } catch (error) {
            console.error("Error updating profile:", error);
            alert("An error occurred while updating.");
        }
    });
    
});