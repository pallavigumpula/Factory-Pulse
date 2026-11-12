/**
 * FactoryPulse — AI Manufacturing Analytics Assistant Page
 */

const AssistantPage = {
    async render(container) {
        container.innerHTML = `
            <div class="d-flex justify-content-between align-items-center mb-3">
                <div>
                    <h5 class="fw-bold mb-1">AI Manufacturing Operations Assistant</h5>
                    <p class="text-muted small mb-0">Deterministic root cause analysis and prescriptive engineering actions based on actual shop-floor data.</p>
                </div>
            </div>

            <!-- Quick Suggestion Chips -->
            <div class="d-flex flex-wrap gap-2 mb-3">
                <button class="btn btn-sm btn-outline-secondary rounded-pill chip-query" data-q="Which machine has the highest downtime?">
                    <i class="bi bi-search me-1"></i> Which machine has the highest downtime?
                </button>
                <button class="btn btn-sm btn-outline-secondary rounded-pill chip-query" data-q="Why did OEE decrease today?">
                    <i class="bi bi-search me-1"></i> Why did OEE decrease today?
                </button>
                <button class="btn btn-sm btn-outline-secondary rounded-pill chip-query" data-q="Which line has the best performance?">
                    <i class="bi bi-search me-1"></i> Which line has the best performance?
                </button>
                <button class="btn btn-sm btn-outline-secondary rounded-pill chip-query" data-q="What are the major causes of production loss?">
                    <i class="bi bi-search me-1"></i> What are the major causes of production loss?
                </button>
                <button class="btn btn-sm btn-outline-secondary rounded-pill chip-query" data-q="What actions can improve OEE?">
                    <i class="bi bi-lightbulb me-1"></i> What actions can improve OEE?
                </button>
            </div>

            <!-- Chat Container -->
            <div class="assistant-chat-container">
                <div class="chat-history" id="chat-messages">
                    <div class="chat-bubble-ai">
                        <div class="fw-bold mb-1"><i class="bi bi-robot text-primary me-1"></i> FactoryPulse AI Assistant</div>
                        Hello! I am your manufacturing intelligence agent. I analyze live equipment state telemetry, discrete counts, shift breakdowns, and quality results to identify bottlenecks and prescribe corrective actions. Ask me any operational question or select a prompt above!
                    </div>
                </div>

                <div class="p-3 border-top bg-light d-flex gap-2" style="border-radius: 0 0 12px 12px;">
                    <input type="text" id="assistant-input" class="form-control" placeholder="Ask a question about machine downtime, line performance, or OEE loss...">
                    <button class="btn btn-primary px-4" id="assistant-send-btn">
                        <i class="bi bi-send-fill me-1"></i> Ask
                    </button>
                </div>
            </div>
        `;

        this.initChat();
    },

    initChat() {
        const input = document.getElementById("assistant-input");
        const sendBtn = document.getElementById("assistant-send-btn");

        sendBtn.onclick = () => this.handleSend();
        input.addEventListener("keydown", (e) => {
            if (e.key === "Enter") this.handleSend();
        });

        document.querySelectorAll(".chip-query").forEach(chip => {
            chip.onclick = () => {
                input.value = chip.getAttribute("data-q");
                this.handleSend();
            };
        });
    },

    async handleSend() {
        const input = document.getElementById("assistant-input");
        const q = input.value.trim();
        if (!q) return;

        const history = document.getElementById("chat-messages");

        // Append User bubble
        const userBubble = document.createElement("div");
        userBubble.className = "chat-bubble-user";
        userBubble.textContent = q;
        history.appendChild(userBubble);
        input.value = "";
        history.scrollTop = history.scrollHeight;

        // Append loading bubble
        const loadingBubble = document.createElement("div");
        loadingBubble.className = "chat-bubble-ai";
        loadingBubble.innerHTML = `
            <div class="d-flex align-items-center gap-2">
                <span class="spinner-border spinner-border-sm text-primary" role="status"></span>
                <span>Analyzing shop-floor database records and calculating diagnostics...</span>
            </div>
        `;
        history.appendChild(loadingBubble);
        history.scrollTop = history.scrollHeight;

        try {
            const res = await API.post("/assistant/query", { question: q });

            const insightsHtml = res.insights && res.insights.length > 0 ? `
                <div class="mt-2 pt-2 border-top">
                    <strong class="text-primary small"><i class="bi bi-graph-up me-1"></i> Data Insights:</strong>
                    <ul class="small mb-1 ps-3 text-secondary">
                        ${res.insights.map(i => `<li>${i}</li>`).join("")}
                    </ul>
                </div>
            ` : "";

            const actionsHtml = res.suggested_actions && res.suggested_actions.length > 0 ? `
                <div class="mt-2 pt-2 border-top">
                    <strong class="text-success small"><i class="bi bi-check2-circle me-1"></i> Recommended Engineering Actions:</strong>
                    <ul class="small mb-0 ps-3 text-secondary">
                        ${res.suggested_actions.map(a => `<li>${a}</li>`).join("")}
                    </ul>
                </div>
            ` : "";

            loadingBubble.innerHTML = `
                <div class="fw-bold mb-1"><i class="bi bi-robot text-primary me-1"></i> FactoryPulse AI Assistant</div>
                <div>${res.answer.replace(/\n/g, "<br>")}</div>
                ${insightsHtml}
                ${actionsHtml}
            `;
        } catch (err) {
            loadingBubble.innerHTML = `
                <div class="text-danger fw-semibold">Error processing query: ${err.message}</div>
            `;
        } finally {
            history.scrollTop = history.scrollHeight;
        }
    }
};
