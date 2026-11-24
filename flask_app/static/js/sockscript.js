const socketio = io();
const messagesEl = document.getElementById("messages");
const lowerEl = document.getElementById("lower");

// ── Helpers ────────────────────────────────────────────────────────────────

function getKey() {
    return {
        shift: document.getElementById("shift").value,
        seed1: document.getElementById("seed1").value,
        seed2: document.getElementById("seed2").value,
        seed3: document.getElementById("seed3").value,
    };
}

function scrollToBottom() {
    messagesEl.scrollTop = messagesEl.scrollHeight;
}

// ── Message rendering ───────────────────────────────────────────────────────

function createMessage(name, msg) {
    const div = document.createElement("div");
    div.className = "text";
    div.innerHTML = `
        <span>
            <strong>${escapeHtml(name)}</strong>:
            <span class="msg-text clickable" title="Click to decrypt">${escapeHtml(msg)}</span>
        </span>
        <span class="muted">${new Date().toLocaleTimeString()}</span>
    `;
    // Attach decrypt listener to the message span
    div.querySelector(".msg-text").addEventListener("click", function () {
        decryptText(this);
    });
    messagesEl.appendChild(div);
    scrollToBottom();
}

function escapeHtml(str) {
    const div = document.createElement("div");
    div.appendChild(document.createTextNode(str));
    return div.innerHTML;
}

// ── Encrypt ─────────────────────────────────────────────────────────────────

function encrypt() {
    const toenc = document.getElementById("toenc");
    const message = toenc.value.trim();
    if (!message) return;

    const payload = { ...getKey(), message };

    fetch("/encrypt", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ key: payload }),
    })
        .then((r) => r.json())
        .then((encrypted) => {
            socketio.emit("message", { data: encrypted });
            toenc.value = "";
        })
        .catch(console.error);
}

// ── Decrypt (click on any message) ─────────────────────────────────────────

function decryptText(el) {
    const payload = { ...getKey(), message: el.textContent };

    fetch("/decrypt", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ key: payload }),
    })
        .then((r) => r.json())
        .then((decrypted) => {
            lowerEl.textContent = decrypted;
            lowerEl.classList.add("decrypted-flash");
            setTimeout(() => lowerEl.classList.remove("decrypted-flash"), 600);
        })
        .catch(console.error);
}

// ── Send clear message ──────────────────────────────────────────────────────

function sendMessage() {
    const input = document.getElementById("message");
    const text = input.value.trim();
    if (!text) return;
    socketio.emit("message", { data: text });
    input.value = "";
}

// ── Replay room history ─────────────────────────────────────────────────────

(function replayHistory() {
    const dataEl = document.getElementById("history-data");
    if (!dataEl) return;
    try {
        JSON.parse(dataEl.textContent).forEach((m) => createMessage(m.name, m.message));
    } catch (err) {
        console.error("Could not load room history:", err);
    }
})();

// ── Socket events ───────────────────────────────────────────────────────────

socketio.on("message", (data) => {
    createMessage(data.name, data.message);
});

// ── Keyboard shortcuts ──────────────────────────────────────────────────────

document.getElementById("message").addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

document.getElementById("toenc").addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        encrypt();
    }
});
