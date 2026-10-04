const messageInput = document.getElementById("messageInput");
const messages = document.getElementById("messages");
const sendButton = document.getElementById("sendButton");


messageInput.addEventListener("keydown", function (event) {

    if (event.key === "Enter" && !event.shiftKey) {

        event.preventDefault();

        sendMessage();

    }

});


messageInput.addEventListener("input", function () {

    this.style.height = "auto";

    this.style.height = this.scrollHeight + "px";

});


async function sendMessage() {

    const message = messageInput.value.trim();


    if (!message) {
        return;
    }


    // Remove welcome screen
    const welcome = document.querySelector(".welcome");

    if (welcome) {
        welcome.remove();
    }


    // Add user message
    addMessage(message, "user");


    // Clear input
    messageInput.value = "";

    messageInput.style.height = "auto";


    // Disable button
    sendButton.disabled = true;


    // Show typing animation
    const typingElement = showTyping();


    try {

        const response = await fetch("/chat", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                message: message
            })

        });


        const data = await response.json();


        // Remove typing animation
        typingElement.remove();


        // Add bot reply
        addMessage(
            data.reply,
            "bot"
        );


    } catch (error) {

        typingElement.remove();


        addMessage(
            "⚠️ Something went wrong. Make sure the Python server and Ollama are running.",
            "bot"
        );


        console.error(error);

    }


    sendButton.disabled = false;


    // Focus back on input
    messageInput.focus();

}


function addMessage(text, sender) {

    const messageDiv = document.createElement("div");

    messageDiv.classList.add(
        "message",
        sender
    );


    const avatar = document.createElement("div");

    avatar.classList.add("avatar");


    if (sender === "user") {

        avatar.classList.add("user-avatar");

        avatar.textContent = "👤";

    } else {

        avatar.classList.add("bot-avatar");

        avatar.textContent = "🤖";

    }


    const content = document.createElement("div");

    content.classList.add("message-content");

    content.textContent = text;


    messageDiv.appendChild(avatar);

    messageDiv.appendChild(content);


    messages.appendChild(messageDiv);


    scrollToBottom();

}


function showTyping() {

    const typingMessage = document.createElement("div");

    typingMessage.classList.add(
        "message",
        "bot"
    );


    typingMessage.innerHTML = `

        <div class="avatar bot-avatar">
            🤖
        </div>

        <div class="message-content">

            <div class="typing">

                <span></span>
                <span></span>
                <span></span>

            </div>

        </div>

    `;


    messages.appendChild(typingMessage);


    scrollToBottom();


    return typingMessage;

}


function scrollToBottom() {

    messages.scrollTop = messages.scrollHeight;

}


function sendSuggestion(button) {

    messageInput.value = button.textContent.trim();

    sendMessage();

}


async function resetChat() {

    try {

        await fetch("/reset", {
            method: "POST"
        });


        messages.innerHTML = `

            <div class="welcome">

                <div class="welcome-icon">
                    🤖
                </div>

                <h2>
                    New conversation started
                </h2>

                <p>
                    How can I help you today?
                </p>

            </div>

        `;


    } catch (error) {

        console.error(error);

    }

}