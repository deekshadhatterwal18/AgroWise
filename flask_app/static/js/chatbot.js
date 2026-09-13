const form = document.getElementById("chat-form");
const input = document.getElementById("chat-input");
const chatWindow = document.getElementById("chat-window");


function addMessage(text, sender) {
    const msg = document.createElement("div");
    msg.className = "chat-msg " + sender;

    if (sender.includes("bot-msg")) {
        // Bot ke messages me markdown (bold, bullets, tables) ko
        // HTML me convert karke render karte hain, taaki **bold**
        // jaisa raw text na dikhe, properly formatted dikhe
        msg.innerHTML = marked.parse(text);
    } else {
        // User ke messages plain text hi rehte hain (safe rehta hai)
        msg.textContent = text;
    }

    chatWindow.appendChild(msg);
    chatWindow.scrollTop = chatWindow.scrollHeight;
    return msg;
}

form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const question = input.value.trim();
    if (!question) return;

    addMessage(question, "user-msg");
    input.value = "";

    const loadingMsg = addMessage("Typing...", "bot-msg loading");

    try {
        const res = await fetch("/api/chatbot/ask", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ question })
        });

        const data = await res.json();
        loadingMsg.remove();

        if (data.success) {
            addMessage(data.answer, "bot-msg");

            if (data.sources && data.sources.length > 0) {
                const uniqueSources = [...new Set(data.sources)];
                addMessage("📚 Sources: " + uniqueSources.join(", "), "bot-msg sources");
            }
        } else {
            addMessage("Error: " + data.error, "bot-msg error");
        }
    } catch (err) {
        loadingMsg.remove();
        addMessage("Something went wrong. Please try again.", "bot-msg error");
    }
});
