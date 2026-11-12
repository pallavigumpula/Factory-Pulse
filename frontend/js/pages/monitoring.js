/**
 * FactoryPulse — Machine Monitoring Live Status Page
 */

const MonitoringPage = {
    async render(container) {
        container.innerHTML = `
            <div class="d-flex justify-content-between align-items-center mb-3">
                <div>
                    <h5 class="fw-bold mb-1">Equipment Telemetry & Live Status</h5>
                    <p class="text-muted small mb-0">Real-time machine states across all production lines.</p>
                </div>
                <div class="d-flex gap-2">
                    <button class="btn btn-outline-primary btn-sm" id="btn-refresh-monitoring">
                        <i class="bi bi-arrow-clockwise me-1"></i> Refresh Status
                    </button>
                    <button class="btn btn-primary btn-sm" id="btn-record-event-modal">
                        <i class="bi bi-plus-circle me-1"></i> Log Machine Event
                    </button>
                </div>
            </div>

            <div id="monitoring-grid" class="row g-3">
                <div class="col-12 text-center py-5">
                    <div class="spinner-border text-primary" role="status"></div>
                </div>
            </div>
        `;

        document.getElementById("btn-refresh-monitoring").addEventListener("click", () => this.loadData());
        document.getElementById("btn-record-event-modal").addEventListener("click", () => this.showEventModal());

        await this.loadData();
    },

    async loadData() {
        const grid = document.getElementById("monitoring-grid");
        try {
            const [lines, machines] = await Promise.all([
                API.get("/lines"),
                API.get("/machines")
            ]);

            grid.innerHTML = "";

            lines.forEach(line => {
                const lineMachines = machines.filter(m => m.line_id === line.id);
                const lineSection = document.createElement("div");
                lineSection.className = "col-12 mb-4";
                lineSection.innerHTML = `
                    <div class="d-flex align-items-center justify-content-between border-bottom pb-2 mb-3">
                        <h6 class="fw-bold text-dark mb-0">
                            <i class="bi bi-diagram-3 text-primary me-2"></i> ${line.line_code} — ${line.name}
                        </h6>
                        <span class="badge bg-light text-secondary border">Target OEE: ${line.target_oee}%</span>
                    </div>
                    <div class="row g-3" id="line-grid-${line.id}"></div>
                `;
                grid.appendChild(lineSection);

                const container = document.getElementById(`line-grid-${line.id}`);
                lineMachines.forEach(m => {
                    const statusClass = `badge-${m.current_status.toLowerCase()}`;
                    const dotClass = `dot-${m.current_status.toLowerCase()}`;
                    const card = document.createElement("div");
                    card.className = "col-12 col-sm-6 col-md-4 col-xl-2";
                    card.innerHTML = `
                        <div class="machine-card h-100">
                            <div class="d-flex justify-content-between align-items-start mb-2">
                                <span class="fw-bold font-monospace text-primary">${m.machine_code}</span>
                                <span class="badge-status ${statusClass}">
                                    <span class="status-dot ${dotClass}"></span> ${m.current_status}
                                </span>
                            </div>
                            <div class="fw-semibold text-truncate small mb-1" title="${m.name}">${m.name}</div>
                            <div class="text-muted" style="font-size: 0.72rem;">Model: ${m.model || "Standard"}</div>
                            <button class="btn btn-outline-secondary btn-sm w-100 mt-3 py-1" style="font-size: 0.75rem;" onclick="MonitoringPage.quickChangeStatus(${m.id}, '${m.machine_code}')">
                                <i class="bi bi-pencil-square me-1"></i> Update State
                            </button>
                        </div>
                    `;
                    container.appendChild(card);
                });
            });
        } catch (e) {
            grid.innerHTML = `<div class="alert alert-danger">Error loading equipment telemetry: ${e.message}</div>`;
        }
    },

    async quickChangeStatus(machineId, machineCode) {
        const modalTitle = document.getElementById("genericModalTitle");
        const modalBody = document.getElementById("genericModalBody");
        const modalSubmit = document.getElementById("genericModalSubmit");

        modalTitle.textContent = `Update State — ${machineCode}`;
        modalBody.innerHTML = `
            <div class="mb-3">
                <label class="form-label small fw-bold">Select New Machine State</label>
                <select id="quick-state" class="form-select">
                    <option value="RUNNING">RUNNING</option>
                    <option value="STOPPED">STOPPED</option>
                    <option value="IDLE">IDLE</option>
                    <option value="CHANGEOVER">CHANGEOVER</option>
                    <option value="MAINTENANCE">MAINTENANCE</option>
                    <option value="BREAK">BREAK</option>
                </select>
            </div>
            <div class="mb-3">
                <label class="form-label small fw-bold">Technician Notes</label>
                <input type="text" id="quick-notes" class="form-control" placeholder="Operational status transition">
            </div>
        `;

        modalSubmit.onclick = async () => {
            const newState = document.getElementById("quick-state").value;
            const notes = document.getElementById("quick-notes").value;
            const now = new Date();
            const past = new Date(now.getTime() - 60000); // 1 minute event

            try {
                await API.post("/machine-events", {
                    machine_id: machineId,
                    state: newState,
                    start_time: past.toISOString(),
                    end_time: now.toISOString(),
                    notes: notes || "State transition via Monitoring UI"
                });
                bootstrap.Modal.getInstance(document.getElementById("genericModal")).hide();
                App.showToast(`Machine ${machineCode} state updated to ${newState}`, "success");
                MonitoringPage.loadData();
            } catch (err) {
                App.showToast("Failed to update state: " + err.message, "danger");
            }
        };

        const modal = new bootstrap.Modal(document.getElementById("genericModal"));
        modal.show();
    },

    showEventModal() {
        const modalTitle = document.getElementById("genericModalTitle");
        const modalBody = document.getElementById("genericModalBody");
        const modalSubmit = document.getElementById("genericModalSubmit");

        modalTitle.textContent = "Log Machine State Event";
        modalBody.innerHTML = `
            <div class="mb-3">
                <label class="form-label small fw-bold">Machine ID</label>
                <input type="number" id="evt-machine-id" class="form-control" placeholder="e.g. 1" required>
            </div>
            <div class="mb-3">
                <label class="form-label small fw-bold">State</label>
                <select id="evt-state" class="form-select">
                    <option value="RUNNING">RUNNING</option>
                    <option value="STOPPED">STOPPED</option>
                    <option value="IDLE">IDLE</option>
                    <option value="CHANGEOVER">CHANGEOVER</option>
                    <option value="MAINTENANCE">MAINTENANCE</option>
                    <option value="BREAK">BREAK</option>
                </select>
            </div>
            <div class="row g-2 mb-3">
                <div class="col-6">
                    <label class="form-label small fw-bold">Start Time</label>
                    <input type="datetime-local" id="evt-start" class="form-control" required>
                </div>
                <div class="col-6">
                    <label class="form-label small fw-bold">End Time</label>
                    <input type="datetime-local" id="evt-end" class="form-control" required>
                </div>
            </div>
            <div class="mb-3">
                <label class="form-label small fw-bold">Notes</label>
                <input type="text" id="evt-notes" class="form-control" placeholder="Operator observations">
            </div>
        `;

        // Pre-fill times
        const now = new Date();
        const past = new Date(now.getTime() - 15 * 60000);
        document.getElementById("evt-start").value = past.toISOString().slice(0, 16);
        document.getElementById("evt-end").value = now.toISOString().slice(0, 16);

        modalSubmit.onclick = async () => {
            const mId = parseInt(document.getElementById("evt-machine-id").value);
            const state = document.getElementById("evt-state").value;
            const start = new Date(document.getElementById("evt-start").value).toISOString();
            const end = new Date(document.getElementById("evt-end").value).toISOString();
            const notes = document.getElementById("evt-notes").value;

            try {
                await API.post("/machine-events", {
                    machine_id: mId,
                    state,
                    start_time: start,
                    end_time: end,
                    notes
                });
                bootstrap.Modal.getInstance(document.getElementById("genericModal")).hide();
                App.showToast("Machine event successfully logged.", "success");
                MonitoringPage.loadData();
            } catch (err) {
                App.showToast("Error: " + err.message, "danger");
            }
        };

        const modal = new bootstrap.Modal(document.getElementById("genericModal"));
        modal.show();
    }
};
