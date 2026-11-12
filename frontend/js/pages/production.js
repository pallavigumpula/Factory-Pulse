/**
 * FactoryPulse — Production Execution Pages:
 * Orders, Production Counts (with traceable corrections), Quality Inspections, Downtime
 */

const ProductionPage = {
    // -------------------------------------------------------------
    // 1. Production Orders View
    // -------------------------------------------------------------
    async renderOrders(container) {
        container.innerHTML = `
            <div class="d-flex justify-content-between align-items-center mb-3">
                <div>
                    <h5 class="fw-bold mb-1">Production Work Orders (PO)</h5>
                    <p class="text-muted small mb-0">Scheduled work orders, line assignments, and batch completion rates.</p>
                </div>
                <button class="btn btn-primary btn-sm" id="btn-create-po-modal">
                    <i class="bi bi-plus-circle me-1"></i> New Production Order
                </button>
            </div>

            <div class="table-card">
                <div class="table-responsive">
                    <table class="table table-hover align-middle">
                        <thead>
                            <tr>
                                <th>Order Code</th>
                                <th>Line</th>
                                <th>Product</th>
                                <th>Target Qty</th>
                                <th>Produced Qty</th>
                                <th>Completion</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody id="po-table-body">
                            <tr><td colspan="8" class="text-center py-4 text-muted">Loading orders...</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
        `;

        document.getElementById("btn-create-po-modal").addEventListener("click", () => this.showCreatePOModal());
        await this.loadOrders();
    },

    async loadOrders() {
        const tbody = document.getElementById("po-table-body");
        try {
            const orders = await API.get("/production-orders");
            if (orders.length === 0) {
                tbody.innerHTML = `<tr><td colspan="8" class="text-center py-4 text-muted">No production orders found.</td></tr>`;
                return;
            }

            tbody.innerHTML = orders.map(o => {
                const pct = o.target_quantity > 0 ? Math.min(100, Math.round(o.produced_quantity / o.target_quantity * 100)) : 0;
                const statusBadge = o.status === "COMPLETED" ? "bg-success" : (o.status === "IN_PROGRESS" ? "bg-primary" : "bg-secondary");
                return `
                    <tr>
                        <td class="fw-bold font-monospace text-primary">${o.order_code}</td>
                        <td>Line #${o.line_id}</td>
                        <td>Product #${o.product_id}</td>
                        <td>${o.target_quantity.toLocaleString()} pcs</td>
                        <td class="fw-semibold text-success">${o.produced_quantity.toLocaleString()} pcs</td>
                        <td style="min-width: 140px;">
                            <div class="d-flex align-items-center gap-2">
                                <div class="progress flex-grow-1" style="height: 6px;">
                                    <div class="progress-bar ${pct >= 100 ? 'bg-success' : 'bg-primary'}" style="width: ${pct}%"></div>
                                </div>
                                <span class="small text-muted">${pct}%</span>
                            </div>
                        </td>
                        <td><span class="badge ${statusBadge}">${o.status}</span></td>
                        <td>
                            <button class="btn btn-outline-secondary btn-sm py-0 px-2" onclick="ProductionPage.showUpdatePOStatusModal(${o.id}, '${o.order_code}', '${o.status}')">
                                Update
                            </button>
                        </td>
                    </tr>
                `;
            }).join("");
        } catch (e) {
            tbody.innerHTML = `<tr><td colspan="8" class="text-danger text-center py-3">Error: ${e.message}</td></tr>`;
        }
    },

    async showCreatePOModal() {
        const [lines, products] = await Promise.all([API.get("/lines"), API.get("/products")]);

        const modalTitle = document.getElementById("genericModalTitle");
        const modalBody = document.getElementById("genericModalBody");
        const modalSubmit = document.getElementById("genericModalSubmit");

        modalTitle.textContent = "Schedule Production Order";
        modalBody.innerHTML = `
            <div class="mb-3">
                <label class="form-label small fw-bold">Production Line</label>
                <select id="modal-po-line" class="form-select" required>
                    ${lines.map(l => `<option value="${l.id}">${l.line_code} - ${l.name}</option>`).join("")}
                </select>
            </div>
            <div class="mb-3">
                <label class="form-label small fw-bold">Manufactured Product</label>
                <select id="modal-po-product" class="form-select" required>
                    ${products.map(p => `<option value="${p.id}">${p.product_code} - ${p.name} (${p.ideal_cycle_time_seconds}s)</option>`).join("")}
                </select>
            </div>
            <div class="mb-3">
                <label class="form-label small fw-bold">Target Quantity (pieces)</label>
                <input type="number" id="modal-po-target" class="form-control" value="1000" min="1" required>
            </div>
        `;

        modalSubmit.onclick = async () => {
            const line_id = parseInt(document.getElementById("modal-po-line").value);
            const product_id = parseInt(document.getElementById("modal-po-product").value);
            const target_quantity = parseInt(document.getElementById("modal-po-target").value);

            try {
                await API.post("/production-orders", {
                    line_id,
                    product_id,
                    target_quantity,
                    status: "PLANNED"
                });
                bootstrap.Modal.getInstance(document.getElementById("genericModal")).hide();
                App.showToast("Production Order created successfully.", "success");
                ProductionPage.loadOrders();
            } catch (err) {
                App.showToast("Error creating order: " + err.message, "danger");
            }
        };

        new bootstrap.Modal(document.getElementById("genericModal")).show();
    },

    showUpdatePOStatusModal(orderId, orderCode, currentStatus) {
        const modalTitle = document.getElementById("genericModalTitle");
        const modalBody = document.getElementById("genericModalBody");
        const modalSubmit = document.getElementById("genericModalSubmit");

        modalTitle.textContent = `Update Status — ${orderCode}`;
        modalBody.innerHTML = `
            <div class="mb-3">
                <label class="form-label small fw-bold">Order Lifecycle Status</label>
                <select id="modal-po-status" class="form-select">
                    <option value="PLANNED" ${currentStatus === "PLANNED" ? "selected" : ""}>PLANNED</option>
                    <option value="IN_PROGRESS" ${currentStatus === "IN_PROGRESS" ? "selected" : ""}>IN_PROGRESS</option>
                    <option value="COMPLETED" ${currentStatus === "COMPLETED" ? "selected" : ""}>COMPLETED</option>
                    <option value="ON_HOLD" ${currentStatus === "ON_HOLD" ? "selected" : ""}>ON_HOLD</option>
                    <option value="CANCELLED" ${currentStatus === "CANCELLED" ? "selected" : ""}>CANCELLED</option>
                </select>
            </div>
        `;

        modalSubmit.onclick = async () => {
            const status = document.getElementById("modal-po-status").value;
            try {
                await API.put(`/production-orders/${orderId}`, { status });
                bootstrap.Modal.getInstance(document.getElementById("genericModal")).hide();
                App.showToast("Order status updated.", "success");
                ProductionPage.loadOrders();
            } catch (err) {
                App.showToast("Error updating order: " + err.message, "danger");
            }
        };

        new bootstrap.Modal(document.getElementById("genericModal")).show();
    },

    // -------------------------------------------------------------
    // 2. Production Counts View (with Traceable Corrections)
    // -------------------------------------------------------------
    async renderCounts(container) {
        container.innerHTML = `
            <div class="d-flex justify-content-between align-items-center mb-3">
                <div>
                    <h5 class="fw-bold mb-1">Production Counts & Audit Ledger</h5>
                    <p class="text-muted small mb-0">Traceable count events with auditable non-destructive corrections.</p>
                </div>
                <div class="d-flex gap-2">
                    <button class="btn btn-outline-warning btn-sm" id="btn-correct-count-modal">
                        <i class="bi bi-pencil-square me-1"></i> Log Traceable Count Correction
                    </button>
                    <button class="btn btn-primary btn-sm" id="btn-record-count-modal">
                        <i class="bi bi-plus-circle me-1"></i> Record Production Count
                    </button>
                </div>
            </div>

            <div class="table-card">
                <div class="table-responsive">
                    <table class="table table-hover align-middle">
                        <thead>
                            <tr>
                                <th>Count Code</th>
                                <th>PO Code</th>
                                <th>Machine</th>
                                <th>Type</th>
                                <th>Quantity</th>
                                <th>Timestamp</th>
                                <th>Correction Trace Ref</th>
                                <th>Reason</th>
                            </tr>
                        </thead>
                        <tbody id="counts-table-body">
                            <tr><td colspan="8" class="text-center py-4 text-muted">Loading count events...</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
        `;

        document.getElementById("btn-record-count-modal").addEventListener("click", () => this.showRecordCountModal());
        document.getElementById("btn-correct-count-modal").addEventListener("click", () => this.showCorrectionModal());
        await this.loadCounts();
    },

    async loadCounts() {
        const tbody = document.getElementById("counts-table-body");
        try {
            const counts = await API.get("/production-counts");
            if (counts.length === 0) {
                tbody.innerHTML = `<tr><td colspan="8" class="text-center py-4 text-muted">No counts recorded yet.</td></tr>`;
                return;
            }

            tbody.innerHTML = counts.map(c => {
                let badgeClass = "bg-success";
                if (c.count_type === "SCRAP") badgeClass = "bg-danger";
                if (c.count_type === "REWORK") badgeClass = "bg-warning text-dark";
                if (c.count_type === "CORRECTION") badgeClass = "bg-info text-dark";

                const refLabel = c.reference_count_id ? `<span class="badge bg-light text-dark font-monospace border">Ref #${c.reference_count_id}</span>` : `<span class="text-muted">—</span>`;

                return `
                    <tr>
                        <td class="font-monospace fw-semibold text-primary">${c.count_code}</td>
                        <td>PO #${c.production_order_id}</td>
                        <td>M #${c.machine_id}</td>
                        <td><span class="badge ${badgeClass}">${c.count_type}</span></td>
                        <td class="fw-bold ${c.quantity < 0 ? 'text-danger' : 'text-dark'}">${c.quantity > 0 && c.count_type === 'CORRECTION' ? '+' : ''}${c.quantity} pcs</td>
                        <td class="small text-muted">${new Date(c.timestamp).toLocaleString()}</td>
                        <td>${refLabel}</td>
                        <td class="small text-truncate" style="max-width: 150px;">${c.reason || "Standard entry"}</td>
                    </tr>
                `;
            }).join("");
        } catch (e) {
            tbody.innerHTML = `<tr><td colspan="8" class="text-danger text-center py-3">Error: ${e.message}</td></tr>`;
        }
    },

    async showRecordCountModal() {
        const [orders, machines] = await Promise.all([API.get("/production-orders"), API.get("/machines")]);

        const modalTitle = document.getElementById("genericModalTitle");
        const modalBody = document.getElementById("genericModalBody");
        const modalSubmit = document.getElementById("genericModalSubmit");

        modalTitle.textContent = "Log Production Count";
        modalBody.innerHTML = `
            <div class="mb-3">
                <label class="form-label small fw-bold">Associated Production Order</label>
                <select id="modal-cnt-po" class="form-select" required>
                    ${orders.map(o => `<option value="${o.id}" data-prod="${o.product_id}">${o.order_code} (Line #${o.line_id})</option>`).join("")}
                </select>
            </div>
            <div class="mb-3">
                <label class="form-label small fw-bold">Producing Machine</label>
                <select id="modal-cnt-machine" class="form-select" required>
                    ${machines.map(m => `<option value="${m.id}">${m.machine_code} - ${m.name}</option>`).join("")}
                </select>
            </div>
            <div class="mb-3">
                <label class="form-label small fw-bold">Count Classification</label>
                <select id="modal-cnt-type" class="form-select">
                    <option value="GOOD">GOOD (First-pass conforming)</option>
                    <option value="SCRAP">SCRAP (Defective non-conforming)</option>
                    <option value="REWORK">REWORK (Secondary processing)</option>
                </select>
            </div>
            <div class="mb-3">
                <label class="form-label small fw-bold">Quantity (pieces)</label>
                <input type="number" id="modal-cnt-qty" class="form-control" value="50" min="1" required>
            </div>
        `;

        modalSubmit.onclick = async () => {
            const poSelect = document.getElementById("modal-cnt-po");
            const po_id = parseInt(poSelect.value);
            const product_id = parseInt(poSelect.selectedOptions[0].getAttribute("data-prod"));
            const machine_id = parseInt(document.getElementById("modal-cnt-machine").value);
            const count_type = document.getElementById("modal-cnt-type").value;
            const quantity = parseInt(document.getElementById("modal-cnt-qty").value);

            try {
                await API.post("/production-counts", {
                    production_order_id: po_id,
                    machine_id,
                    product_id,
                    count_type,
                    quantity,
                    timestamp: new Date().toISOString()
                });
                bootstrap.Modal.getInstance(document.getElementById("genericModal")).hide();
                App.showToast("Count recorded successfully.", "success");
                ProductionPage.loadCounts();
            } catch (err) {
                App.showToast("Error recording count: " + err.message, "danger");
            }
        };

        new bootstrap.Modal(document.getElementById("genericModal")).show();
    },

    async showCorrectionModal() {
        const modalTitle = document.getElementById("genericModalTitle");
        const modalBody = document.getElementById("genericModalBody");
        const modalSubmit = document.getElementById("genericModalSubmit");

        modalTitle.textContent = "Log Traceable Count Correction";
        modalBody.innerHTML = `
            <div class="alert alert-info py-2 small mb-3">
                <i class="bi bi-shield-check me-1"></i> Audit Compliance: Historical counts will NOT be overwritten. An explicit traceable correction transaction will be permanently recorded.
            </div>
            <div class="mb-3">
                <label class="form-label small fw-bold">Reference Production Count ID</label>
                <input type="number" id="modal-corr-ref-id" class="form-control" placeholder="ID from count table (e.g. 1)" required>
            </div>
            <div class="mb-3">
                <label class="form-label small fw-bold">Quantity Adjustment Delta</label>
                <input type="number" id="modal-corr-delta" class="form-control" placeholder="e.g. -5 or +10" required>
                <div class="form-text small">Enter negative delta to reduce count (e.g. -10) or positive to add.</div>
            </div>
            <div class="mb-3">
                <label class="form-label small fw-bold">Justification / Reason</label>
                <input type="text" id="modal-corr-reason" class="form-control" placeholder="e.g. Sensor double-count correction or operator miscount" required>
            </div>
        `;

        modalSubmit.onclick = async () => {
            const ref_id = parseInt(document.getElementById("modal-corr-ref-id").value);
            const delta = parseInt(document.getElementById("modal-corr-delta").value);
            const reason = document.getElementById("modal-corr-reason").value;

            if (!ref_id || isNaN(delta) || !reason) {
                App.showToast("Please fill all required correction fields.", "warning");
                return;
            }

            try {
                await API.post("/production-counts/correct", {
                    reference_count_id: ref_id,
                    corrected_quantity_delta: delta,
                    reason
                });
                bootstrap.Modal.getInstance(document.getElementById("genericModal")).hide();
                App.showToast("Traceable count correction saved.", "success");
                ProductionPage.loadCounts();
            } catch (err) {
                App.showToast("Correction failed: " + err.message, "danger");
            }
        };

        new bootstrap.Modal(document.getElementById("genericModal")).show();
    },

    // -------------------------------------------------------------
    // 3. Quality Inspections View
    // -------------------------------------------------------------
    async renderInspections(container) {
        container.innerHTML = `
            <div class="d-flex justify-content-between align-items-center mb-3">
                <div>
                    <h5 class="fw-bold mb-1">Quality Control & Inspection Audits</h5>
                    <p class="text-muted small mb-0">Part sample audits, defect classifications, and pass/fail gate results.</p>
                </div>
                <button class="btn btn-primary btn-sm" id="btn-create-qc-modal">
                    <i class="bi bi-plus-circle me-1"></i> Log Quality Inspection
                </button>
            </div>

            <div class="table-card">
                <div class="table-responsive">
                    <table class="table table-hover align-middle">
                        <thead>
                            <tr>
                                <th>QC Code</th>
                                <th>Order</th>
                                <th>Machine</th>
                                <th>Sample Size</th>
                                <th>Passed</th>
                                <th>Failed</th>
                                <th>Defect Type</th>
                                <th>Status</th>
                                <th>Timestamp</th>
                            </tr>
                        </thead>
                        <tbody id="qc-table-body">
                            <tr><td colspan="9" class="text-center py-4 text-muted">Loading QC records...</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
        `;

        document.getElementById("btn-create-qc-modal").addEventListener("click", () => this.showCreateQCModal());
        await this.loadInspections();
    },

    async loadInspections() {
        const tbody = document.getElementById("qc-table-body");
        try {
            const records = await API.get("/quality-inspections");
            if (records.length === 0) {
                tbody.innerHTML = `<tr><td colspan="9" class="text-center py-4 text-muted">No inspection records logged yet.</td></tr>`;
                return;
            }

            tbody.innerHTML = records.map(r => {
                const statusBadge = r.status === "PASSED" ? "bg-success" : (r.status === "FAILED" ? "bg-danger" : "bg-warning text-dark");
                return `
                    <tr>
                        <td class="font-monospace fw-semibold text-primary">${r.inspection_code}</td>
                        <td>PO #${r.production_order_id}</td>
                        <td>M #${r.machine_id}</td>
                        <td class="fw-bold">${r.sample_size} pcs</td>
                        <td class="text-success fw-semibold">${r.passed_count}</td>
                        <td class="${r.failed_count > 0 ? 'text-danger fw-bold' : 'text-muted'}">${r.failed_count}</td>
                        <td>${r.defect_type ? `<span class="badge bg-light text-danger border">${r.defect_type}</span>` : `<span class="text-muted">None</span>`}</td>
                        <td><span class="badge ${statusBadge}">${r.status}</span></td>
                        <td class="small text-muted">${new Date(r.timestamp).toLocaleString()}</td>
                    </tr>
                `;
            }).join("");
        } catch (e) {
            tbody.innerHTML = `<tr><td colspan="9" class="text-danger text-center py-3">Error: ${e.message}</td></tr>`;
        }
    },

    async showCreateQCModal() {
        const [orders, machines] = await Promise.all([API.get("/production-orders"), API.get("/machines")]);

        const modalTitle = document.getElementById("genericModalTitle");
        const modalBody = document.getElementById("genericModalBody");
        const modalSubmit = document.getElementById("genericModalSubmit");

        modalTitle.textContent = "Log Quality Inspection Record";
        modalBody.innerHTML = `
            <div class="mb-3">
                <label class="form-label small fw-bold">Production Order</label>
                <select id="modal-qc-po" class="form-select" required>
                    ${orders.map(o => `<option value="${o.id}">${o.order_code}</option>`).join("")}
                </select>
            </div>
            <div class="mb-3">
                <label class="form-label small fw-bold">Inspection Station / Machine</label>
                <select id="modal-qc-machine" class="form-select" required>
                    ${machines.map(m => `<option value="${m.id}">${m.machine_code} - ${m.name}</option>`).join("")}
                </select>
            </div>
            <div class="row g-2 mb-3">
                <div class="col-4">
                    <label class="form-label small fw-bold">Sample Size</label>
                    <input type="number" id="modal-qc-sample" class="form-control" value="25" min="1" required>
                </div>
                <div class="col-4">
                    <label class="form-label small fw-bold">Passed Count</label>
                    <input type="number" id="modal-qc-passed" class="form-control" value="25" min="0" required>
                </div>
                <div class="col-4">
                    <label class="form-label small fw-bold">Failed Count</label>
                    <input type="number" id="modal-qc-failed" class="form-control" value="0" min="0" required>
                </div>
            </div>
            <div class="mb-3">
                <label class="form-label small fw-bold">Defect Taxonomy</label>
                <input type="text" id="modal-qc-defect" class="form-control" placeholder="e.g. Solder bridge, dimensional out-of-spec, scratch">
            </div>
            <div class="mb-3">
                <label class="form-label small fw-bold">Inspection Disposition</label>
                <select id="modal-qc-status" class="form-select">
                    <option value="PASSED">PASSED</option>
                    <option value="FAILED">FAILED</option>
                    <option value="CONDITIONAL">CONDITIONAL</option>
                </select>
            </div>
        `;

        modalSubmit.onclick = async () => {
            const po_id = parseInt(document.getElementById("modal-qc-po").value);
            const m_id = parseInt(document.getElementById("modal-qc-machine").value);
            const sample_size = parseInt(document.getElementById("modal-qc-sample").value);
            const passed_count = parseInt(document.getElementById("modal-qc-passed").value);
            const failed_count = parseInt(document.getElementById("modal-qc-failed").value);
            const defect_type = document.getElementById("modal-qc-defect").value;
            const status = document.getElementById("modal-qc-status").value;

            try {
                await API.post("/quality-inspections", {
                    production_order_id: po_id,
                    machine_id: m_id,
                    sample_size,
                    passed_count,
                    failed_count,
                    defect_type: defect_type || null,
                    status,
                    timestamp: new Date().toISOString()
                });
                bootstrap.Modal.getInstance(document.getElementById("genericModal")).hide();
                App.showToast("Quality inspection logged.", "success");
                ProductionPage.loadInspections();
            } catch (err) {
                App.showToast("Error: " + err.message, "danger");
            }
        };

        new bootstrap.Modal(document.getElementById("genericModal")).show();
    },

    // -------------------------------------------------------------
    // 4. Downtime Management View
    // -------------------------------------------------------------
    async renderDowntime(container) {
        container.innerHTML = `
            <div class="d-flex justify-content-between align-items-center mb-3">
                <div>
                    <h5 class="fw-bold mb-1">Downtime Tracking & Root Cause Analysis</h5>
                    <p class="text-muted small mb-0">Equipment stoppages, breakdown durations, and categorization taxonomy.</p>
                </div>
            </div>

            <div class="row g-3 mb-4">
                <div class="col-12 col-lg-8">
                    <div class="chart-card">
                        <h6 class="fw-bold mb-2">Downtime Duration Pareto Analysis</h6>
                        <div id="chart-downtime-page-pareto"></div>
                    </div>
                </div>
                <div class="col-12 col-lg-4">
                    <div class="table-card p-3 h-100">
                        <h6 class="fw-bold mb-3">Top Downtime Root Causes</h6>
                        <div id="downtime-top-reasons" class="small">
                            <div class="text-center py-3 text-muted">Loading reasons...</div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="table-card">
                <div class="card-header">
                    <h6 class="fw-bold mb-0">Chronological Equipment Stoppage Events</h6>
                </div>
                <div class="table-responsive">
                    <table class="table table-hover align-middle">
                        <thead>
                            <tr>
                                <th>Event Code</th>
                                <th>Machine</th>
                                <th>State</th>
                                <th>Start Time</th>
                                <th>End Time</th>
                                <th>Duration</th>
                                <th>Notes</th>
                            </tr>
                        </thead>
                        <tbody id="dt-events-table-body">
                            <tr><td colspan="7" class="text-center py-4 text-muted">Loading events...</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
        `;

        await this.loadDowntimeData();
    },

    async loadDowntimeData() {
        const topEl = document.getElementById("downtime-top-reasons");
        const tbody = document.getElementById("dt-events-table-body");

        try {
            const dtData = await API.get("/oee/downtime-reasons");
            Charts.renderDowntimeParetoChart("chart-downtime-page-pareto", dtData);

            if (dtData.length === 0) {
                topEl.innerHTML = `<div class="text-muted text-center">No downtime recorded.</div>`;
            } else {
                topEl.innerHTML = dtData.slice(0, 5).map(d => `
                    <div class="d-flex justify-content-between align-items-center mb-2 pb-2 border-bottom">
                        <div>
                            <div class="fw-bold text-dark">${d.name}</div>
                            <span class="badge ${d.is_planned ? 'bg-secondary' : 'bg-danger'}">${d.category}</span>
                        </div>
                        <div class="text-end">
                            <div class="fw-bold text-danger">${d.duration_minutes} min</div>
                            <div class="text-muted" style="font-size: 0.72rem;">${d.incident_count} events</div>
                        </div>
                    </div>
                `).join("");
            }

            // Load machine state events for stoppages
            const events = await API.get("/machine-events", { state: "STOPPED", limit: 50 });
            if (events.length === 0) {
                tbody.innerHTML = `<tr><td colspan="7" class="text-center py-4 text-muted">No stoppage events recorded.</td></tr>`;
                return;
            }

            tbody.innerHTML = events.map(e => `
                <tr>
                    <td class="font-monospace fw-semibold text-primary">${e.event_code}</td>
                    <td>Machine #${e.machine_id}</td>
                    <td><span class="badge bg-danger">${e.state}</span></td>
                    <td class="small text-muted">${new Date(e.start_time).toLocaleString()}</td>
                    <td class="small text-muted">${new Date(e.end_time).toLocaleString()}</td>
                    <td class="fw-bold text-danger">${Math.round(e.duration_seconds / 60)} min</td>
                    <td class="small text-muted">${e.notes || "Stoppage recorded"}</td>
                </tr>
            `).join("");
        } catch (e) {
            console.error("Error loading downtime:", e);
        }
    }
};
