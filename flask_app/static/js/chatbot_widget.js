const toggleBtn = document.getElementById("chatbot-toggle-btn");
const panel = document.getElementById("chatbot-panel");
const closeBtn = document.getElementById("chatbot-close-btn");
const expandBtn = document.getElementById("chatbot-expand-btn");
const widgetForm = document.getElementById("widget-chat-form");
const widgetInput = document.getElementById("widget-chat-input");
const widgetWindow = document.getElementById("widget-chat-window");

toggleBtn.addEventListener("click", () => {
    panel.classList.toggle("hidden");
    if (!panel.classList.contains("hidden")) {
        widgetInput.focus();
    }
});

closeBtn.addEventListener("click", () => {
    panel.classList.add("hidden");
    panel.classList.remove("fullscreen");
});

expandBtn.addEventListener("click", () => {
    panel.classList.toggle("fullscreen");
    expandBtn.textContent = panel.classList.contains("fullscreen") ? "⤢" : "⛶";
});

function addWidgetMessage(text, sender) {
    const msg = document.createElement("div");
    msg.className = "chat-msg " + sender;

    if (sender.includes("bot-msg")) {
        msg.innerHTML = marked.parse(text);
    } else {
        msg.textContent = text;
    }

    widgetWindow.appendChild(msg);
    widgetWindow.scrollTop = widgetWindow.scrollHeight;
    return msg;
}

widgetForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const question = widgetInput.value.trim();
    if (!question) return;

    addWidgetMessage(question, "user-msg");
    widgetInput.value = "";

    const loadingMsg = addWidgetMessage("Typing...", "bot-msg loading");

    try {
        const res = await fetch("/api/chatbot/ask", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ question })
        });

        const data = await res.json();
        loadingMsg.remove();

        if (data.success) {
            addWidgetMessage(data.answer, "bot-msg");
        } else {
            addWidgetMessage("Error: " + data.error, "bot-msg error");
        }
    } catch (err) {
        loadingMsg.remove();
        addWidgetMessage("Something went wrong. Please try again.", "bot-msg error");
    }
});
