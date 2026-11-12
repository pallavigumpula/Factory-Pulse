/**
 * FactoryPulse — Anomaly Detection & Ground Truth Evaluation Page
 */

const AnomaliesPage = {
    async render(container) {
        container.innerHTML = `
            <div class="d-flex justify-content-between align-items-center mb-3">
                <div>
                    <h5 class="fw-bold mb-1">Operational Anomaly Detection & Diagnostics</h5>
                    <p class="text-muted small mb-0">Rule-based detection of telemetry collisions, count discrepancies, and schedule conflicts.</p>
                </div>
                <div class="d-flex gap-2">
                    <button class="btn btn-primary btn-sm" id="btn-run-anomaly-scan">
                        <i class="bi bi-radar me-1"></i> Scan Database for Anomalies
                    </button>
                </div>
            </div>

            <!-- Ground Truth Evaluation Scorecard Row -->
            <div class="card border-0 shadow-sm mb-4" style="border-radius: 12px; background: #0f172a; color: white;">
                <div class="card-body p-4">
                    <div class="d-flex justify-content-between align-items-center mb-3">
                        <h6 class="fw-bold text-white mb-0">
                            <i class="bi bi-award text-warning me-2"></i> Model Benchmark vs Ground Truth (Independent Evaluation)
                        </h6>
                        <span class="badge bg-secondary-subtle text-white small">ground_truth.json</span>
                    </div>

                    <div class="row g-3 text-center" id="gt-metrics-row">
                        <div class="col-6 col-md-3">
                            <div class="text-muted small text-uppercase fw-semibold">Precision</div>
                            <div class="fs-2 fw-bold text-success" id="metric-precision">--</div>
                            <div class="text-secondary small">TP / (TP + FP)</div>
                        </div>
                        <div class="col-6 col-md-3">
                            <div class="text-muted small text-uppercase fw-semibold">Recall</div>
                            <div class="fs-2 fw-bold text-info" id="metric-recall">--</div>
                            <div class="text-secondary small">TP / (TP + FN)</div>
                        </div>
                        <div class="col-6 col-md-3">
                            <div class="text-muted small text-uppercase fw-semibold">F1-Score</div>
                            <div class="fs-2 fw-bold text-warning" id="metric-f1">--</div>
                            <div class="text-secondary small">Harmonic Mean</div>
                        </div>
                        <div class="col-6 col-md-3">
                            <div class="text-muted small text-uppercase fw-semibold">True Positives</div>
                            <div class="fs-2 fw-bold text-white" id="metric-tp">--</div>
                            <div class="text-secondary small" id="metric-fp-fn">FP: -- | FN: --</div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Anomalies List Header & Filter -->
            <div class="d-flex justify-content-between align-items-center mb-3">
                <h6 class="fw-bold mb-0">Detected Anomalies Log (<span id="anom-count">0</span>)</h6>
                <div class="d-flex gap-2">
                    <select id="filter-anom-severity" class="form-select form-select-sm" style="width: 150px;">
                        <option value="">All Severities</option>
                        <option value="CRITICAL">CRITICAL</option>
                        <option value="HIGH">HIGH</option>
                        <option value="MEDIUM">MEDIUM</option>
                        <option value="LOW">LOW</option>
                    </select>
                </div>
            </div>

            <!-- List Container -->
            <div id="anomalies-list" class="mb-4">
                <div class="text-center py-4"><div class="spinner-border text-primary" role="status"></div></div>
            </div>
        `;

        document.getElementById("btn-run-anomaly-scan").addEventListener("click", () => this.runScan());
        document.getElementById("filter-anom-severity").addEventListener("change", (e) => {
            this.loadAnomalies(e.target.value);
        });

        await this.loadMetrics();
        await this.loadAnomalies();
    },

    async loadMetrics() {
        try {
            const m = await API.get("/anomalies/evaluation");
            document.getElementById("metric-precision").textContent = `${(m.precision * 100).toFixed(1)}%`;
            document.getElementById("metric-recall").textContent = `${(m.recall * 100).toFixed(1)}%`;
            document.getElementById("metric-f1").textContent = m.f1_score.toFixed(4);
            document.getElementById("metric-tp").textContent = `${m.true_positives} / ${m.total_ground_truth}`;
            document.getElementById("metric-fp-fn").textContent = `FP: ${m.false_positives} | FN: ${m.false_negatives}`;
        } catch (e) {
            console.error("Error loading metrics:", e);
        }
    },

    async loadAnomalies(severity = "") {
        const list = document.getElementById("anomalies-list");
        try {
            const data = await API.get("/anomalies", { severity });
            document.getElementById("anom-count").textContent = data.length;

            const badgeEl = document.getElementById("sidebar-anomaly-count");
            if (badgeEl) badgeEl.textContent = data.filter(d => d.resolution_status === "OPEN").length;

            if (data.length === 0) {
                list.innerHTML = `<div class="card p-4 text-center text-muted">No anomalies detected with selected filter.</div>`;
                return;
            }

            list.innerHTML = data.map(a => {
                const sevClass = `anomaly-${a.severity.toLowerCase()}`;
                const sevBadge = a.severity === "CRITICAL" ? "bg-danger" : (a.severity === "HIGH" ? "bg-warning text-dark" : "bg-primary");
                
                return `
                    <div class="anomaly-card ${sevClass}">
                        <div class="d-flex justify-content-between align-items-start mb-2">
                            <div>
                                <span class="badge ${sevBadge} me-2">${a.severity}</span>
                                <span class="fw-bold text-dark font-monospace">${a.anomaly_code}</span>
                                <span class="badge bg-light text-secondary ms-2">${a.anomaly_type}</span>
                            </div>
                            <div class="d-flex align-items-center gap-2">
                                <span class="badge bg-secondary-subtle text-secondary">${new Date(a.timestamp).toLocaleString()}</span>
                                <div class="dropdown">
                                    <button class="btn btn-sm btn-outline-secondary dropdown-toggle py-0 px-2" style="font-size: 0.75rem;" data-bs-toggle="dropdown">
                                        Status: <strong>${a.resolution_status}</strong>
                                    </button>
                                    <ul class="dropdown-menu dropdown-menu-end shadow-sm">
                                        <li><a class="dropdown-item" href="javascript:void(0)" onclick="AnomaliesPage.updateStatus(${a.id}, 'OPEN')">OPEN</a></li>
                                        <li><a class="dropdown-item" href="javascript:void(0)" onclick="AnomaliesPage.updateStatus(${a.id}, 'INVESTIGATING')">INVESTIGATING</a></li>
                                        <li><a class="dropdown-item" href="javascript:void(0)" onclick="AnomaliesPage.updateStatus(${a.id}, 'RESOLVED')">RESOLVED</a></li>
                                        <li><a class="dropdown-item" href="javascript:void(0)" onclick="AnomaliesPage.updateStatus(${a.id}, 'FALSE_POSITIVE')">FALSE_POSITIVE</a></li>
                                    </ul>
                                </div>
                            </div>
                        </div>

                        <p class="mb-2 text-dark" style="font-size: 0.9rem;">${a.description}</p>

                        <div class="row g-2 mb-2 p-2 bg-light rounded" style="font-size: 0.8rem;">
                            <div class="col-12 col-md-6">
                                <span class="text-muted fw-bold">Expected Condition:</span> <code class="text-success">${a.expected_value}</code>
                            </div>
                            <div class="col-12 col-md-6">
                                <span class="text-muted fw-bold">Actual Value:</span> <code class="text-danger">${a.actual_value}</code>
                            </div>
                        </div>

                        <div class="small text-muted d-flex align-items-center">
                            <i class="bi bi-wrench-adjustable me-2 text-primary"></i>
                            <strong>Recommended Action:</strong> &nbsp;${a.recommended_action}
                        </div>
                    </div>
                `;
            }).join("");
        } catch (e) {
            list.innerHTML = `<div class="alert alert-danger">Error loading anomalies: ${e.message}</div>`;
        }
    },

    async runScan() {
        const btn = document.getElementById("btn-run-anomaly-scan");
        btn.disabled = true;
        btn.innerHTML = `<span class="spinner-border spinner-border-sm me-1" role="status"></span> Scanning...`;

        try {
            const detected = await API.post("/anomalies/scan");
            App.showToast(`Scan complete: ${detected.length} anomalies identified.`, "success");
            await this.loadMetrics();
            await this.loadAnomalies();
        } catch (e) {
            App.showToast("Scan error: " + e.message, "danger");
        } finally {
            btn.disabled = false;
            btn.innerHTML = `<i class="bi bi-radar me-1"></i> Scan Database for Anomalies`;
        }
    },

    async updateStatus(anomalyId, status) {
        try {
            await API.put(`/anomalies/${anomalyId}/status`, { resolution_status: status });
            App.showToast(`Anomaly status set to ${status}`, "success");
            this.loadAnomalies();
        } catch (e) {
            App.showToast("Error updating status: " + e.message, "danger");
        }
    }
};
