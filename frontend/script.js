const user_input = document.getElementById("user-input")

const send_button = document.getElementById("send-button")

const chat_messages = document.querySelector(".chat-messages")

const reset_button = document.getElementById("reset-button");

send_button.addEventListener("click", async () => {

    const query = user_input.value;

    const user_message = document.createElement("div");

    user_message.className = "user-message";

    user_message.textContent = query;

    chat_messages.appendChild(user_message);


    user_input.value = "";

    const loading_message = document.createElement("div")

    loading_message.className = "assistant-message";

    loading_message.textContent = "Waiting..."

    chat_messages.appendChild(loading_message)

    const response = await fetch(
        "http://127.0.0.1:8000/chat",
        {
            method : "POST",
            headers : {
                "Content-Type" : "application/json"
            },
            body : JSON.stringify({
                "query" : query
            })
        }
    );

    const data = await response.json()

    loading_message.remove();

    const assistant_message = document.createElement("div");

    assistant_message.className = "assistant-message";

    assistant_message.textContent = data.answer;

    chat_messages.appendChild(assistant_message);

});

user_input.addEventListener("keydown", (event) => {

    if (event.key === "Enter") {
        send_button.click();
    }

});

reset_button.addEventListener("click", () => {

    chat_messages.innerHTML = "";

})

