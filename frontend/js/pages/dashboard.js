/**
 * FactoryPulse — Main Dashboard Page View
 */

const DashboardPage = {
    filters: {
        plant_id: "",
        line_id: "",
        machine_id: "",
        days: 7
    },

    async render(container) {
        container.innerHTML = `
            <!-- Filter Bar -->
            <div class="filter-bar d-flex flex-wrap align-items-center justify-content-between gap-3">
                <div class="d-flex flex-wrap align-items-center gap-3">
                    <div>
                        <label class="form-label small text-muted mb-1 fw-bold">Plant</label>
                        <select id="filter-plant" class="form-select form-select-sm" style="min-width: 180px;">
                            <option value="">All Plants</option>
                        </select>
                    </div>
                    <div>
                        <label class="form-label small text-muted mb-1 fw-bold">Production Line</label>
                        <select id="filter-line" class="form-select form-select-sm" style="min-width: 180px;">
                            <option value="">All Lines</option>
                        </select>
                    </div>
                    <div>
                        <label class="form-label small text-muted mb-1 fw-bold">Time Window</label>
                        <select id="filter-days" class="form-select form-select-sm" style="min-width: 140px;">
                            <option value="7" selected>Last 7 Days</option>
                            <option value="14">Last 14 Days</option>
                            <option value="30">Last 30 Days</option>
                        </select>
                    </div>
                </div>
                <div class="d-flex align-items-end">
                    <button class="btn btn-primary btn-sm px-3" id="btn-refresh-dashboard">
                        <i class="bi bi-arrow-clockwise me-1"></i> Refresh Real-Time Data
                    </button>
                </div>
            </div>

            <!-- KPI Cards Row 1: OEE & Factors -->
            <div class="row g-3 mb-4">
                <div class="col-12 col-sm-6 col-xl-3">
                    <div class="kpi-card">
                        <div class="kpi-title">Overall OEE</div>
                        <div class="kpi-value text-primary" id="kpi-oee">--%</div>
                        <div class="kpi-subtitle d-flex justify-content-between align-items-center">
                            <span>Target Benchmark: 85%</span>
                            <span class="badge bg-primary-subtle text-primary" id="kpi-oee-status">Live</span>
                        </div>
                        <i class="bi bi-speedometer2 kpi-icon-watermark"></i>
                    </div>
                </div>
                <div class="col-12 col-sm-6 col-xl-3">
                    <div class="kpi-card">
                        <div class="kpi-title">Availability</div>
                        <div class="kpi-value text-success" id="kpi-availability">--%</div>
                        <div class="kpi-subtitle" id="kpi-operating-time">Operating: -- hrs</div>
                        <i class="bi bi-clock-history kpi-icon-watermark"></i>
                    </div>
                </div>
                <div class="col-12 col-sm-6 col-xl-3">
                    <div class="kpi-card">
                        <div class="kpi-title">Performance</div>
                        <div class="kpi-value text-warning" id="kpi-performance">--%</div>
                        <div class="kpi-subtitle" id="kpi-flagged-count">Over-speed alerts: 0</div>
                        <i class="bi bi-lightning-charge kpi-icon-watermark"></i>
                    </div>
                </div>
                <div class="col-12 col-sm-6 col-xl-3">
                    <div class="kpi-card">
                        <div class="kpi-title">Quality Yield</div>
                        <div class="kpi-value text-info" id="kpi-quality">--%</div>
                        <div class="kpi-subtitle" id="kpi-scrap-summary">Scrap: -- pcs</div>
                        <i class="bi bi-patch-check kpi-icon-watermark"></i>
                    </div>
                </div>
            </div>

            <!-- KPI Cards Row 2: Volume & Downtime -->
            <div class="row g-3 mb-4">
                <div class="col-12 col-sm-6 col-xl-3">
                    <div class="kpi-card">
                        <div class="kpi-title">Total Production</div>
                        <div class="kpi-value" id="kpi-total-prod">--</div>
                        <div class="kpi-subtitle text-muted">Total units manufactured</div>
                        <i class="bi bi-box-seam kpi-icon-watermark"></i>
                    </div>
                </div>
                <div class="col-12 col-sm-6 col-xl-3">
                    <div class="kpi-card">
                        <div class="kpi-title">Good Units</div>
                        <div class="kpi-value text-success" id="kpi-good-count">--</div>
                        <div class="kpi-subtitle text-muted">First-pass conforming</div>
                        <i class="bi bi-check-circle kpi-icon-watermark"></i>
                    </div>
                </div>
                <div class="col-12 col-sm-6 col-xl-3">
                    <div class="kpi-card">
                        <div class="kpi-title">Scrap Units</div>
                        <div class="kpi-value text-danger" id="kpi-scrap-count">--</div>
                        <div class="kpi-subtitle text-muted">Non-conforming loss</div>
                        <i class="bi bi-x-circle kpi-icon-watermark"></i>
                    </div>
                </div>
                <div class="col-12 col-sm-6 col-xl-3">
                    <div class="kpi-card">
                        <div class="kpi-title">Total Downtime</div>
                        <div class="kpi-value text-danger" id="kpi-downtime">-- min</div>
                        <div class="kpi-subtitle" id="kpi-unplanned-dt">Unplanned: -- min</div>
                        <i class="bi bi-pause-circle kpi-icon-watermark"></i>
                    </div>
                </div>
            </div>

            <!-- Charts Row 1: Trend & Machine Status Distribution -->
            <div class="row g-3 mb-4">
                <div class="col-12 col-lg-8">
                    <div class="chart-card">
                        <div class="d-flex justify-content-between align-items-center mb-2">
                            <h6 class="fw-bold mb-0">OEE & Three Factor Trends Over Time</h6>
                            <span class="badge bg-light text-secondary">Daily Window</span>
                        </div>
                        <div id="chart-oee-trend"></div>
                    </div>
                </div>
                <div class="col-12 col-lg-4">
                    <div class="chart-card">
                        <div class="d-flex justify-content-between align-items-center mb-2">
                            <h6 class="fw-bold mb-0">Equipment Status Mix</h6>
                            <span class="badge bg-light text-secondary" id="active-machines-badge">30 Machines</span>
                        </div>
                        <div id="chart-status-pie"></div>
                    </div>
                </div>
            </div>

            <!-- Charts Row 2: Machine Ranking & Pareto Downtime -->
            <div class="row g-3 mb-4">
                <div class="col-12 col-lg-6">
                    <div class="chart-card">
                        <div class="d-flex justify-content-between align-items-center mb-2">
                            <h6 class="fw-bold mb-0">OEE by Production Machine</h6>
                            <span class="badge bg-light text-secondary">Target = 85%</span>
                        </div>
                        <div id="chart-oee-machines"></div>
                    </div>
                </div>
                <div class="col-12 col-lg-6">
                    <div class="chart-card">
                        <div class="d-flex justify-content-between align-items-center mb-2">
                            <h6 class="fw-bold mb-0">Downtime Pareto by Reason Code</h6>
                            <span class="badge bg-danger-subtle text-danger">Lost Minutes</span>
                        </div>
                        <div id="chart-downtime-reasons"></div>
                    </div>
                </div>
            </div>

            <!-- Charts Row 3: Line Comparison & Good vs Scrap -->
            <div class="row g-3 mb-4">
                <div class="col-12 col-lg-8">
                    <div class="chart-card">
                        <div class="d-flex justify-content-between align-items-center mb-2">
                            <h6 class="fw-bold mb-0">OEE vs Target by Production Line</h6>
                            <span class="badge bg-light text-secondary">Line Aggregates</span>
                        </div>
                        <div id="chart-oee-lines"></div>
                    </div>
                </div>
                <div class="col-12 col-lg-4">
                    <div class="chart-card">
                        <div class="d-flex justify-content-between align-items-center mb-2">
                            <h6 class="fw-bold mb-0">Quality Breakdown (Good vs Scrap vs Rework)</h6>
                        </div>
                        <div id="chart-quality-donut"></div>
                    </div>
                </div>
            </div>
        `;

        this.initFilters();
        await this.loadDashboardData();
    },

    async initFilters() {
        const plantSelect = document.getElementById("filter-plant");
        const lineSelect = document.getElementById("filter-line");
        const daysSelect = document.getElementById("filter-days");
        const refreshBtn = document.getElementById("btn-refresh-dashboard");

        try {
            const plants = await API.get("/plants");
            plants.forEach(p => {
                const opt = document.createElement("option");
                opt.value = p.id;
                opt.textContent = `${p.plant_code} - ${p.name}`;
                plantSelect.appendChild(opt);
            });

            const lines = await API.get("/lines");
            lines.forEach(l => {
                const opt = document.createElement("option");
                opt.value = l.id;
                opt.textContent = `${l.line_code} - ${l.name}`;
                lineSelect.appendChild(opt);
            });
        } catch (e) {
            console.error("Error loading filter dropdowns:", e);
        }

        plantSelect.addEventListener("change", (e) => {
            this.filters.plant_id = e.target.value;
            this.loadDashboardData();
        });

        lineSelect.addEventListener("change", (e) => {
            this.filters.line_id = e.target.value;
            this.loadDashboardData();
        });

        daysSelect.addEventListener("change", (e) => {
            this.filters.days = parseInt(e.target.value);
            this.loadDashboardData();
        });

        refreshBtn.addEventListener("click", () => {
            this.loadDashboardData();
        });
    },

    async loadDashboardData() {
        try {
            // 1. Fetch KPI cards
            const kpi = await API.get("/oee/dashboard-kpis", {
                plant_id: this.filters.plant_id,
                line_id: this.filters.line_id
            });

            document.getElementById("kpi-oee").textContent = `${kpi.overall_oee}%`;
            document.getElementById("kpi-availability").textContent = `${kpi.availability}%`;
            document.getElementById("kpi-performance").textContent = `${kpi.performance}%`;
            document.getElementById("kpi-quality").textContent = `${kpi.quality}%`;

            document.getElementById("kpi-total-prod").textContent = Number(kpi.total_production).toLocaleString();
            document.getElementById("kpi-good-count").textContent = Number(kpi.good_count).toLocaleString();
            document.getElementById("kpi-scrap-count").textContent = Number(kpi.scrap_count).toLocaleString();
            document.getElementById("kpi-downtime").textContent = `${kpi.total_downtime_minutes} min`;
            document.getElementById("kpi-unplanned-dt").textContent = `Unplanned: ${kpi.unplanned_downtime_minutes} min`;
            document.getElementById("kpi-flagged-count").textContent = `Over-speed alerts: ${kpi.performance_flagged_count}`;
            document.getElementById("active-machines-badge").textContent = `${kpi.active_machines_count} / ${kpi.total_machines_count} Running`;

            // 2. Fetch Trend Data
            const trend = await API.get("/oee/trend", {
                line_id: this.filters.line_id,
                days: this.filters.days
            });
            Charts.renderOEETrendChart("chart-oee-trend", trend);

            // 3. Fetch Machines & Status Distribution
            const machines = await API.get("/machines", {
                line_id: this.filters.line_id
            });
            Charts.renderStatusDistributionChart("chart-status-pie", machines);

            // 4. Fetch Machine OEE rankings
            const machineOEE = await API.get("/oee/by-machine", {
                line_id: this.filters.line_id
            });
            Charts.renderOEEByMachineChart("chart-oee-machines", machineOEE);

            // 5. Fetch Line OEE comparison
            const lineOEE = await API.get("/oee/by-line");
            Charts.renderOEEByLineChart("chart-oee-lines", lineOEE);

            // 6. Fetch Downtime Reasons
            const downtime = await API.get("/oee/downtime-reasons", {
                line_id: this.filters.line_id
            });
            Charts.renderDowntimeParetoChart("chart-downtime-reasons", downtime);

            // 7. Render Quality Donut
            Charts.renderGoodVsScrapChart("chart-quality-donut", kpi.good_count, kpi.scrap_count, kpi.rework_count);

        } catch (error) {
            console.error("Dashboard data load error:", error);
            App.showToast("Failed to load dashboard data: " + error.message, "danger");
        }
    }
};
