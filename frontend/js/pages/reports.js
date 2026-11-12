/**
 * FactoryPulse — Reports & Exports Center
 */

const ReportsPage = {
    async render(container) {
        container.innerHTML = `
            <div class="d-flex justify-content-between align-items-center mb-3">
                <div>
                    <h5 class="fw-bold mb-1">Reports, Analytics & Data Export Center</h5>
                    <p class="text-muted small mb-0">Generate standard manufacturing reports, export raw telemetry in CSV and JSON formats.</p>
                </div>
            </div>

            <!-- Export Cards Grid -->
            <div class="row g-3 mb-4">
                <div class="col-12 col-md-6 col-xl-3">
                    <div class="card h-100 p-3 border-0 shadow-sm" style="border-radius: 12px;">
                        <div class="d-flex align-items-center gap-3 mb-3">
                            <div class="p-3 bg-primary-subtle text-primary rounded-3 fs-4">
                                <i class="bi bi-file-earmark-spreadsheet"></i>
                            </div>
                            <div>
                                <h6 class="fw-bold mb-0">OEE Metrics Export</h6>
                                <span class="text-muted small">CSV Spreadsheet</span>
                            </div>
                        </div>
                        <p class="text-muted small flex-grow-1">Export full machine Availability, Performance, Quality, and OEE KPIs by date window.</p>
                        <a href="/api/v1/reports/oee/export/csv" class="btn btn-primary btn-sm w-100">
                            <i class="bi bi-download me-1"></i> Download CSV
                        </a>
                    </div>
                </div>

                <div class="col-12 col-md-6 col-xl-3">
                    <div class="card h-100 p-3 border-0 shadow-sm" style="border-radius: 12px;">
                        <div class="d-flex align-items-center gap-3 mb-3">
                            <div class="p-3 bg-info-subtle text-info rounded-3 fs-4">
                                <i class="bi bi-filetype-json"></i>
                            </div>
                            <div>
                                <h6 class="fw-bold mb-0">OEE Records (JSON)</h6>
                                <span class="text-muted small">Structured Data</span>
                            </div>
                        </div>
                        <p class="text-muted small flex-grow-1">Machine OEE data formatted for external MES ingestion or ERP synchronization.</p>
                        <a href="/api/v1/reports/oee/export/json" class="btn btn-outline-info btn-sm w-100">
                            <i class="bi bi-download me-1"></i> Download JSON
                        </a>
                    </div>
                </div>

                <div class="col-12 col-md-6 col-xl-3">
                    <div class="card h-100 p-3 border-0 shadow-sm" style="border-radius: 12px;">
                        <div class="d-flex align-items-center gap-3 mb-3">
                            <div class="p-3 bg-danger-subtle text-danger rounded-3 fs-4">
                                <i class="bi bi-shield-exclamation"></i>
                            </div>
                            <div>
                                <h6 class="fw-bold mb-0">Anomaly Audit Log</h6>
                                <span class="text-muted small">CSV Compliance</span>
                            </div>
                        </div>
                        <p class="text-muted small flex-grow-1">Complete audit log of all identified data anomalies and operational violations.</p>
                        <a href="/api/v1/reports/anomalies/export/csv" class="btn btn-outline-danger btn-sm w-100">
                            <i class="bi bi-download me-1"></i> Download Anomalies CSV
                        </a>
                    </div>
                </div>

                <div class="col-12 col-md-6 col-xl-3">
                    <div class="card h-100 p-3 border-0 shadow-sm" style="border-radius: 12px;">
                        <div class="d-flex align-items-center gap-3 mb-3">
                            <div class="p-3 bg-warning-subtle text-warning rounded-3 fs-4">
                                <i class="bi bi-bug"></i>
                            </div>
                            <div>
                                <h6 class="fw-bold mb-0">Ground Truth Labels</h6>
                                <span class="text-muted small">JSON Benchmark</span>
                            </div>
                        </div>
                        <p class="text-muted small flex-grow-1">Download official ground-truth benchmark labels for ML / model evaluation.</p>
                        <a href="/api/v1/reports/anomalies/export/json" class="btn btn-outline-warning btn-sm w-100">
                            <i class="bi bi-download me-1"></i> Download GT JSON
                        </a>
                    </div>
                </div>
            </div>

            <!-- Production Summary Table -->
            <div class="table-card mb-4">
                <div class="card-header">
                    <h6 class="fw-bold mb-0">Production Completion Summary</h6>
                </div>
                <div class="table-responsive">
                    <table class="table table-hover align-middle">
                        <thead>
                            <tr>
                                <th>Order Code</th>
                                <th>Line</th>
                                <th>Product</th>
                                <th>Target</th>
                                <th>Produced</th>
                                <th>Completion %</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody id="rpt-prod-tbody"><tr><td colspan="7" class="text-center py-4 text-muted">Loading summary...</td></tr></tbody>
                    </table>
                </div>
            </div>

            <!-- Downtime Summary Table -->
            <div class="table-card">
                <div class="card-header">
                    <h6 class="fw-bold mb-0">Equipment Downtime Summary by Root Cause</h6>
                </div>
                <div class="table-responsive">
                    <table class="table table-hover align-middle">
                        <thead>
                            <tr>
                                <th>Reason Code</th>
                                <th>Name</th>
                                <th>Category</th>
                                <th>Classification</th>
                                <th>Incidents</th>
                                <th>Total Minutes</th>
                                <th>% of Downtime</th>
                            </tr>
                        </thead>
                        <tbody id="rpt-dt-tbody"><tr><td colspan="7" class="text-center py-4 text-muted">Loading summary...</td></tr></tbody>
                    </table>
                </div>
            </div>
        `;

        this.loadSummaries();
    },

    async loadSummaries() {
        const prodTbody = document.getElementById("rpt-prod-tbody");
        const dtTbody = document.getElementById("rpt-dt-tbody");

        try {
            const prod = await API.get("/reports/production-summary");
            prodTbody.innerHTML = prod.map(p => `
                <tr>
                    <td class="fw-bold font-monospace text-primary">${p.order_code}</td>
                    <td>${p.line_code}</td>
                    <td>${p.product_name}</td>
                    <td>${p.target_quantity.toLocaleString()}</td>
                    <td class="fw-semibold text-success">${p.produced_quantity.toLocaleString()}</td>
                    <td>
                        <div class="d-flex align-items-center gap-2">
                            <div class="progress flex-grow-1" style="height: 6px;">
                                <div class="progress-bar ${p.completion_rate >= 100 ? 'bg-success' : 'bg-primary'}" style="width: ${p.completion_rate}%"></div>
                            </div>
                            <span class="small text-muted">${p.completion_rate}%</span>
                        </div>
                    </td>
                    <td><span class="badge ${p.status === 'COMPLETED' ? 'bg-success' : 'bg-primary'}">${p.status}</span></td>
                </tr>
            `).join("");

            const dt = await API.get("/reports/downtime-summary");
            dtTbody.innerHTML = dt.map(d => `
                <tr>
                    <td class="font-monospace text-primary">${d.reason_code}</td>
                    <td class="fw-semibold">${d.name}</td>
                    <td><span class="badge bg-light text-dark border">${d.category}</span></td>
                    <td><span class="badge ${d.is_planned ? 'bg-secondary' : 'bg-danger'}">${d.is_planned ? 'Planned' : 'Unplanned'}</span></td>
                    <td>${d.incidents}</td>
                    <td class="fw-bold text-danger">${d.duration_minutes} min</td>
                    <td>${d.percentage}%</td>
                </tr>
            `).join("");
        } catch (e) {
            console.error("Error loading summaries:", e);
        }
    }
};
