/**
 * FactoryPulse — OEE Analytics Drilldown Page
 */

const OEEPage = {
    async render(container) {
        container.innerHTML = `
            <div class="d-flex justify-content-between align-items-center mb-3">
                <div>
                    <h5 class="fw-bold mb-1">OEE Analytics & Factor Decomposition</h5>
                    <p class="text-muted small mb-0">Deep dive into Availability, Performance, and Quality components.</p>
                </div>
            </div>

            <!-- Machine Selector & Calculator Card -->
            <div class="card border-0 shadow-sm mb-4" style="border-radius: 12px;">
                <div class="card-body p-4">
                    <div class="row g-3 align-items-end">
                        <div class="col-12 col-md-4">
                            <label class="form-label small fw-bold">Select Machine to Inspect</label>
                            <select id="oee-machine-select" class="form-select">
                                <option value="">Loading machines...</option>
                            </select>
                        </div>
                        <div class="col-12 col-md-3">
                            <label class="form-label small fw-bold">Analysis Start Date</label>
                            <input type="date" id="oee-start-date" class="form-control">
                        </div>
                        <div class="col-12 col-md-3">
                            <label class="form-label small fw-bold">Analysis End Date</label>
                            <input type="date" id="oee-end-date" class="form-control">
                        </div>
                        <div class="col-12 col-md-2">
                            <button class="btn btn-primary w-100" id="btn-calc-oee">
                                <i class="bi bi-calculator me-1"></i> Compute OEE
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Calculation Output Area -->
            <div id="oee-calc-output">
                <div class="text-center py-4 text-muted">
                    <i class="bi bi-speedometer2" style="font-size: 3rem; opacity: 0.3;"></i>
                    <p class="mt-2">Select a machine and click "Compute OEE" to analyze factor decomposition.</p>
                </div>
            </div>
        `;

        this.initControls();
    },

    async initControls() {
        const select = document.getElementById("oee-machine-select");
        const sDate = document.getElementById("oee-start-date");
        const eDate = document.getElementById("oee-end-date");
        const calcBtn = document.getElementById("btn-calc-oee");

        const today = new Date();
        const past = new Date(today.getTime() - 7 * 86400000);
        sDate.value = past.toISOString().slice(0, 10);
        eDate.value = today.toISOString().slice(0, 10);

        try {
            const machines = await API.get("/machines");
            select.innerHTML = "";
            machines.forEach(m => {
                const opt = document.createElement("option");
                opt.value = m.id;
                opt.textContent = `${m.machine_code} — ${m.name}`;
                select.appendChild(opt);
            });

            if (machines.length > 0) {
                this.computeMachineOEE(machines[0].id);
            }
        } catch (e) {
            select.innerHTML = `<option value="">Error loading machines</option>`;
        }

        calcBtn.addEventListener("click", () => {
            const mId = select.value;
            if (mId) {
                this.computeMachineOEE(mId);
            }
        });
    },

    async computeMachineOEE(machineId) {
        const out = document.getElementById("oee-calc-output");
        out.innerHTML = `<div class="text-center py-5"><div class="spinner-border text-primary" role="status"></div></div>`;

        const sDate = document.getElementById("oee-start-date").value;
        const eDate = document.getElementById("oee-end-date").value;

        try {
            const res = await API.get(`/oee/machine/${machineId}`, {
                start_date: sDate,
                end_date: eDate
            });

            const flagAlert = res.performance_flagged ? `
                <div class="alert alert-warning py-2 small d-flex align-items-center mb-4">
                    <i class="bi bi-exclamation-triangle-fill fs-5 me-2"></i>
                    <div>
                        <strong>Performance Flagged (>100%):</strong> Calculated speed performance is <code>${res.performance}%</code>. Bounded to 100% in composite OEE. Please audit ideal cycle time baseline.
                    </div>
                </div>
            ` : "";

            out.innerHTML = `
                ${flagAlert}
                <!-- 4 Factor Cards -->
                <div class="row g-3 mb-4">
                    <div class="col-12 col-md-3">
                        <div class="kpi-card border-primary">
                            <div class="kpi-title text-primary">Composite OEE</div>
                            <div class="kpi-value text-primary">${res.oee}%</div>
                            <div class="kpi-subtitle">Availability × Performance × Quality</div>
                        </div>
                    </div>
                    <div class="col-12 col-md-3">
                        <div class="kpi-card">
                            <div class="kpi-title">Availability (A)</div>
                            <div class="kpi-value text-success">${res.availability}%</div>
                            <div class="kpi-subtitle">${res.operating_time_minutes} min / ${res.planned_production_time_minutes} min</div>
                        </div>
                    </div>
                    <div class="col-12 col-md-3">
                        <div class="kpi-card">
                            <div class="kpi-title">Performance (P)</div>
                            <div class="kpi-value text-warning">${res.performance}%</div>
                            <div class="kpi-subtitle">Cycle: ${res.ideal_cycle_time_seconds}s | Units: ${res.total_count}</div>
                        </div>
                    </div>
                    <div class="col-12 col-md-3">
                        <div class="kpi-card">
                            <div class="kpi-title">Quality (Q)</div>
                            <div class="kpi-value text-info">${res.quality}%</div>
                            <div class="kpi-subtitle">${res.good_count} Good / ${res.total_count} Total</div>
                        </div>
                    </div>
                </div>

                <!-- Equation Breakdown & Metrics Details -->
                <div class="row g-3 mb-4">
                    <div class="col-12 col-lg-6">
                        <div class="table-card p-4 h-100">
                            <h6 class="fw-bold mb-3"><i class="bi bi-hourglass-split me-2 text-primary"></i> Time Accounting (Minutes)</h6>
                            <table class="table table-sm">
                                <tbody>
                                    <tr>
                                        <td>Planned Production Time (PPT)</td>
                                        <td class="text-end fw-bold">${res.planned_production_time_minutes} min</td>
                                    </tr>
                                    <tr>
                                        <td>Operating Time (Actual Run)</td>
                                        <td class="text-end fw-bold text-success">${res.operating_time_minutes} min</td>
                                    </tr>
                                    <tr>
                                        <td>Planned Downtime (Changeovers/Maint)</td>
                                        <td class="text-end fw-bold text-secondary">${res.planned_downtime_minutes} min</td>
                                    </tr>
                                    <tr>
                                        <td>Unplanned Downtime (Breakdowns/Jams)</td>
                                        <td class="text-end fw-bold text-danger">${res.unplanned_downtime_minutes} min</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                    <div class="col-12 col-lg-6">
                        <div class="table-card p-4 h-100">
                            <h6 class="fw-bold mb-3"><i class="bi bi-box me-2 text-primary"></i> Production Accounting (Pieces)</h6>
                            <table class="table table-sm">
                                <tbody>
                                    <tr>
                                        <td>Total Manufactured Count</td>
                                        <td class="text-end fw-bold">${res.total_count} pcs</td>
                                    </tr>
                                    <tr>
                                        <td>Good Units (Conforming)</td>
                                        <td class="text-end fw-bold text-success">${res.good_count} pcs</td>
                                    </tr>
                                    <tr>
                                        <td>Scrap Units (Defective)</td>
                                        <td class="text-end fw-bold text-danger">${res.scrap_count} pcs</td>
                                    </tr>
                                    <tr>
                                        <td>Rework Units</td>
                                        <td class="text-end fw-bold text-warning">${res.rework_count} pcs</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>

                <!-- Assumptions Callout -->
                <div class="card bg-light border-0 p-3" style="border-radius: 8px;">
                    <div class="small fw-bold text-muted mb-1"><i class="bi bi-info-circle me-1"></i> Calculation Engine Assumptions</div>
                    <ul class="small text-muted mb-0 ps-3">
                        ${res.assumptions.map(a => `<li>${a}</li>`).join("")}
                    </ul>
                </div>
            `;
        } catch (e) {
            out.innerHTML = `<div class="alert alert-danger">Error calculating OEE: ${e.message}</div>`;
        }
    }
};
