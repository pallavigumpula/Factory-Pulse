/**
 * FactoryPulse — Master Data Management Pages:
 * Plants, Lines, Machines, Products, Shifts, Downtime Reasons
 */

const MasterDataPage = {
    // -------------------------------------------------------------
    // Plants
    // -------------------------------------------------------------
    async renderPlants(container) {
        container.innerHTML = `
            <div class="d-flex justify-content-between align-items-center mb-3">
                <div>
                    <h5 class="fw-bold mb-1">Manufacturing Plants & Facilities</h5>
                    <p class="text-muted small mb-0">Manage enterprise manufacturing plants, physical locations, and timezones.</p>
                </div>
                <button class="btn btn-primary btn-sm" id="btn-add-plant"><i class="bi bi-plus-circle me-1"></i> Add Plant</button>
            </div>
            <div class="table-card">
                <div class="table-responsive">
                    <table class="table table-hover align-middle">
                        <thead>
                            <tr>
                                <th>Plant Code</th>
                                <th>Facility Name</th>
                                <th>Location</th>
                                <th>Timezone</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody id="plants-tbody"><tr><td colspan="6" class="text-center py-4 text-muted">Loading...</td></tr></tbody>
                    </table>
                </div>
            </div>
        `;

        document.getElementById("btn-add-plant").onclick = () => this.showPlantModal();
        this.loadPlants();
    },

    async loadPlants() {
        const tbody = document.getElementById("plants-tbody");
        const plants = await API.get("/plants");
        tbody.innerHTML = plants.map(p => `
            <tr>
                <td class="fw-bold font-monospace text-primary">${p.plant_code}</td>
                <td class="fw-semibold">${p.name}</td>
                <td>${p.location || "N/A"}</td>
                <td><span class="badge bg-light text-dark font-monospace">${p.timezone}</span></td>
                <td><span class="badge ${p.is_active ? 'bg-success' : 'bg-secondary'}">${p.is_active ? 'Active' : 'Inactive'}</span></td>
                <td>
                    <button class="btn btn-outline-danger btn-sm py-0 px-2" onclick="MasterDataPage.deletePlant(${p.id})">Delete</button>
                </td>
            </tr>
        `).join("");
    },

    showPlantModal() {
        const modalTitle = document.getElementById("genericModalTitle");
        const modalBody = document.getElementById("genericModalBody");
        const modalSubmit = document.getElementById("genericModalSubmit");

        modalTitle.textContent = "Register Manufacturing Plant";
        modalBody.innerHTML = `
            <div class="mb-3">
                <label class="form-label small fw-bold">Plant Code</label>
                <input type="text" id="m-plant-code" class="form-control" placeholder="e.g. PLANT-03" required>
            </div>
            <div class="mb-3">
                <label class="form-label small fw-bold">Plant Name</label>
                <input type="text" id="m-plant-name" class="form-control" placeholder="Facility descriptive name" required>
            </div>
            <div class="mb-3">
                <label class="form-label small fw-bold">Location</label>
                <input type="text" id="m-plant-loc" class="form-control" placeholder="City, State, Country">
            </div>
            <div class="mb-3">
                <label class="form-label small fw-bold">Timezone</label>
                <input type="text" id="m-plant-tz" class="form-control" value="America/Chicago">
            </div>
        `;

        modalSubmit.onclick = async () => {
            const plant_code = document.getElementById("m-plant-code").value.trim();
            const name = document.getElementById("m-plant-name").value.trim();
            const location = document.getElementById("m-plant-loc").value.trim();
            const timezone = document.getElementById("m-plant-tz").value.trim();

            try {
                await API.post("/plants", { plant_code, name, location, timezone });
                bootstrap.Modal.getInstance(document.getElementById("genericModal")).hide();
                App.showToast("Plant registered successfully.", "success");
                MasterDataPage.loadPlants();
            } catch (err) {
                App.showToast("Error: " + err.message, "danger");
            }
        };

        new bootstrap.Modal(document.getElementById("genericModal")).show();
    },

    async deletePlant(id) {
        if (!confirm("Are you sure you want to delete this plant?")) return;
        try {
            await API.delete(`/plants/${id}`);
            App.showToast("Plant deleted.", "info");
            this.loadPlants();
        } catch (e) {
            App.showToast("Cannot delete plant: " + e.message, "danger");
        }
    },

    // -------------------------------------------------------------
    // Lines
    // -------------------------------------------------------------
    async renderLines(container) {
        container.innerHTML = `
            <div class="d-flex justify-content-between align-items-center mb-3">
                <div>
                    <h5 class="fw-bold mb-1">Production Lines</h5>
                    <p class="text-muted small mb-0">Production lines, target benchmark OEE rates, and parent plant mapping.</p>
                </div>
                <button class="btn btn-primary btn-sm" id="btn-add-line"><i class="bi bi-plus-circle me-1"></i> Add Production Line</button>
            </div>
            <div class="table-card">
                <div class="table-responsive">
                    <table class="table table-hover align-middle">
                        <thead>
                            <tr>
                                <th>Line Code</th>
                                <th>Line Name</th>
                                <th>Plant</th>
                                <th>Target OEE</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody id="lines-tbody"><tr><td colspan="6" class="text-center py-4 text-muted">Loading...</td></tr></tbody>
                    </table>
                </div>
            </div>
        `;

        document.getElementById("btn-add-line").onclick = () => this.showLineModal();
        this.loadLines();
    },

    async loadLines() {
        const tbody = document.getElementById("lines-tbody");
        const lines = await API.get("/lines");
        tbody.innerHTML = lines.map(l => `
            <tr>
                <td class="fw-bold font-monospace text-primary">${l.line_code}</td>
                <td class="fw-semibold">${l.name}</td>
                <td>Plant #${l.plant_id}</td>
                <td><span class="badge bg-primary-subtle text-primary">${l.target_oee}%</span></td>
                <td><span class="badge ${l.is_active ? 'bg-success' : 'bg-secondary'}">${l.is_active ? 'Active' : 'Inactive'}</span></td>
                <td>
                    <button class="btn btn-outline-danger btn-sm py-0 px-2" onclick="MasterDataPage.deleteLine(${l.id})">Delete</button>
                </td>
            </tr>
        `).join("");
    },

    async showLineModal() {
        const plants = await API.get("/plants");
        const modalTitle = document.getElementById("genericModalTitle");
        const modalBody = document.getElementById("genericModalBody");
        const modalSubmit = document.getElementById("genericModalSubmit");

        modalTitle.textContent = "Register Production Line";
        modalBody.innerHTML = `
            <div class="mb-3">
                <label class="form-label small fw-bold">Parent Plant</label>
                <select id="m-line-plant" class="form-select">
                    ${plants.map(p => `<option value="${p.id}">${p.plant_code} - ${p.name}</option>`).join("")}
                </select>
            </div>
            <div class="mb-3">
                <label class="form-label small fw-bold">Line Code</label>
                <input type="text" id="m-line-code" class="form-control" placeholder="e.g. LINE-06" required>
            </div>
            <div class="mb-3">
                <label class="form-label small fw-bold">Line Name</label>
                <input type="text" id="m-line-name" class="form-control" placeholder="Descriptive line name" required>
            </div>
            <div class="mb-3">
                <label class="form-label small fw-bold">Target Benchmark OEE (%)</label>
                <input type="number" id="m-line-target" class="form-control" value="85.00" step="0.5">
            </div>
        `;

        modalSubmit.onclick = async () => {
            const plant_id = parseInt(document.getElementById("m-line-plant").value);
            const line_code = document.getElementById("m-line-code").value.trim();
            const name = document.getElementById("m-line-name").value.trim();
            const target_oee = parseFloat(document.getElementById("m-line-target").value);

            try {
                await API.post("/lines", { plant_id, line_code, name, target_oee });
                bootstrap.Modal.getInstance(document.getElementById("genericModal")).hide();
                App.showToast("Line registered successfully.", "success");
                MasterDataPage.loadLines();
            } catch (err) {
                App.showToast("Error: " + err.message, "danger");
            }
        };

        new bootstrap.Modal(document.getElementById("genericModal")).show();
    },

    async deleteLine(id) {
        if (!confirm("Are you sure you want to delete this line?")) return;
        try {
            await API.delete(`/lines/${id}`);
            App.showToast("Line deleted.", "info");
            this.loadLines();
        } catch (e) {
            App.showToast("Cannot delete line: " + e.message, "danger");
        }
    },

    // -------------------------------------------------------------
    // Machines
    // -------------------------------------------------------------
    async renderMachines(container) {
        container.innerHTML = `
            <div class="d-flex justify-content-between align-items-center mb-3">
                <div>
                    <h5 class="fw-bold mb-1">Equipment & Work Centers</h5>
                    <p class="text-muted small mb-0">Individual machine work centers, OEM models, and operational line routing.</p>
                </div>
                <button class="btn btn-primary btn-sm" id="btn-add-machine"><i class="bi bi-plus-circle me-1"></i> Add Machine</button>
            </div>
            <div class="table-card">
                <div class="table-responsive">
                    <table class="table table-hover align-middle">
                        <thead>
                            <tr>
                                <th>Machine Code</th>
                                <th>Machine Name</th>
                                <th>Line</th>
                                <th>OEM Model</th>
                                <th>Current Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody id="machines-tbody"><tr><td colspan="6" class="text-center py-4 text-muted">Loading...</td></tr></tbody>
                    </table>
                </div>
            </div>
        `;

        document.getElementById("btn-add-machine").onclick = () => this.showMachineModal();
        this.loadMachines();
    },

    async loadMachines() {
        const tbody = document.getElementById("machines-tbody");
        const machines = await API.get("/machines");
        tbody.innerHTML = machines.map(m => {
            const statusClass = `badge-${m.current_status.toLowerCase()}`;
            return `
                <tr>
                    <td class="fw-bold font-monospace text-primary">${m.machine_code}</td>
                    <td class="fw-semibold">${m.name}</td>
                    <td>Line #${m.line_id}</td>
                    <td>${m.model || "Standard"}</td>
                    <td><span class="badge-status ${statusClass}">${m.current_status}</span></td>
                    <td>
                        <button class="btn btn-outline-danger btn-sm py-0 px-2" onclick="MasterDataPage.deleteMachine(${m.id})">Delete</button>
                    </td>
                </tr>
            `;
        }).join("");
    },

    async showMachineModal() {
        const lines = await API.get("/lines");
        const modalTitle = document.getElementById("genericModalTitle");
        const modalBody = document.getElementById("genericModalBody");
        const modalSubmit = document.getElementById("genericModalSubmit");

        modalTitle.textContent = "Register Machine Work Center";
        modalBody.innerHTML = `
            <div class="mb-3">
                <label class="form-label small fw-bold">Assigned Production Line</label>
                <select id="m-mach-line" class="form-select">
                    ${lines.map(l => `<option value="${l.id}">${l.line_code} - ${l.name}</option>`).join("")}
                </select>
            </div>
            <div class="mb-3">
                <label class="form-label small fw-bold">Machine Code</label>
                <input type="text" id="m-mach-code" class="form-control" placeholder="e.g. M-031" required>
            </div>
            <div class="mb-3">
                <label class="form-label small fw-bold">Machine Name</label>
                <input type="text" id="m-mach-name" class="form-control" placeholder="Equipment descriptive name" required>
            </div>
            <div class="mb-3">
                <label class="form-label small fw-bold">OEM Model</label>
                <input type="text" id="m-mach-model" class="form-control" placeholder="e.g. Haas VF-4SS">
            </div>
        `;

        modalSubmit.onclick = async () => {
            const line_id = parseInt(document.getElementById("m-mach-line").value);
            const machine_code = document.getElementById("m-mach-code").value.trim();
            const name = document.getElementById("m-mach-name").value.trim();
            const model = document.getElementById("m-mach-model").value.trim();

            try {
                await API.post("/machines", { line_id, machine_code, name, model });
                bootstrap.Modal.getInstance(document.getElementById("genericModal")).hide();
                App.showToast("Machine registered successfully.", "success");
                MasterDataPage.loadMachines();
            } catch (err) {
                App.showToast("Error: " + err.message, "danger");
            }
        };

        new bootstrap.Modal(document.getElementById("genericModal")).show();
    },

    async deleteMachine(id) {
        if (!confirm("Are you sure you want to delete this machine?")) return;
        try {
            await API.delete(`/machines/${id}`);
            App.showToast("Machine deleted.", "info");
            this.loadMachines();
        } catch (e) {
            App.showToast("Cannot delete machine: " + e.message, "danger");
        }
    },

    // -------------------------------------------------------------
    // Products
    // -------------------------------------------------------------
    async renderProducts(container) {
        container.innerHTML = `
            <div class="d-flex justify-content-between align-items-center mb-3">
                <div>
                    <h5 class="fw-bold mb-1">Product Catalog & Cycle Time Benchmarks</h5>
                    <p class="text-muted small mb-0">Engineered SKUs, standard ideal cycle times (seconds/unit), and product families.</p>
                </div>
                <button class="btn btn-primary btn-sm" id="btn-add-product"><i class="bi bi-plus-circle me-1"></i> Add Product SKU</button>
            </div>
            <div class="table-card">
                <div class="table-responsive">
                    <table class="table table-hover align-middle">
                        <thead>
                            <tr>
                                <th>Product Code</th>
                                <th>Product Name</th>
                                <th>Category</th>
                                <th>Ideal Cycle Time</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody id="products-tbody"><tr><td colspan="6" class="text-center py-4 text-muted">Loading...</td></tr></tbody>
                    </table>
                </div>
            </div>
        `;

        document.getElementById("btn-add-product").onclick = () => this.showProductModal();
        this.loadProducts();
    },

    async loadProducts() {
        const tbody = document.getElementById("products-tbody");
        const products = await API.get("/products");
        tbody.innerHTML = products.map(p => `
            <tr>
                <td class="fw-bold font-monospace text-primary">${p.product_code}</td>
                <td class="fw-semibold">${p.name}</td>
                <td><span class="badge bg-light text-secondary border">${p.category || 'General'}</span></td>
                <td class="fw-bold text-dark font-monospace">${p.ideal_cycle_time_seconds} sec/unit</td>
                <td><span class="badge ${p.is_active ? 'bg-success' : 'bg-secondary'}">${p.is_active ? 'Active' : 'Inactive'}</span></td>
                <td>
                    <button class="btn btn-outline-danger btn-sm py-0 px-2" onclick="MasterDataPage.deleteProduct(${p.id})">Delete</button>
                </td>
            </tr>
        `).join("");
    },

    showProductModal() {
        const modalTitle = document.getElementById("genericModalTitle");
        const modalBody = document.getElementById("genericModalBody");
        const modalSubmit = document.getElementById("genericModalSubmit");

        modalTitle.textContent = "Register Product SKU";
        modalBody.innerHTML = `
            <div class="mb-3">
                <label class="form-label small fw-bold">Product Code</label>
                <input type="text" id="m-prod-code" class="form-control" placeholder="e.g. PROD-021" required>
            </div>
            <div class="mb-3">
                <label class="form-label small fw-bold">Commercial Name</label>
                <input type="text" id="m-prod-name" class="form-control" placeholder="Product name" required>
            </div>
            <div class="mb-3">
                <label class="form-label small fw-bold">Category</label>
                <input type="text" id="m-prod-cat" class="form-control" placeholder="e.g. Electronics, Medical">
            </div>
            <div class="mb-3">
                <label class="form-label small fw-bold">Ideal Cycle Time (Seconds per Unit)</label>
                <input type="number" id="m-prod-cycle" class="form-control" value="20.0" step="0.1" min="0.1" required>
            </div>
        `;

        modalSubmit.onclick = async () => {
            const product_code = document.getElementById("m-prod-code").value.trim();
            const name = document.getElementById("m-prod-name").value.trim();
            const category = document.getElementById("m-prod-cat").value.trim();
            const ideal_cycle_time_seconds = parseFloat(document.getElementById("m-prod-cycle").value);

            try {
                await API.post("/products", { product_code, name, category, ideal_cycle_time_seconds });
                bootstrap.Modal.getInstance(document.getElementById("genericModal")).hide();
                App.showToast("Product registered successfully.", "success");
                MasterDataPage.loadProducts();
            } catch (err) {
                App.showToast("Error: " + err.message, "danger");
            }
        };

        new bootstrap.Modal(document.getElementById("genericModal")).show();
    },

    async deleteProduct(id) {
        if (!confirm("Are you sure you want to delete this product?")) return;
        try {
            await API.delete(`/products/${id}`);
            App.showToast("Product deleted.", "info");
            this.loadProducts();
        } catch (e) {
            App.showToast("Cannot delete product: " + e.message, "danger");
        }
    },

    // -------------------------------------------------------------
    // Shifts
    // -------------------------------------------------------------
    async renderShifts(container) {
        container.innerHTML = `
            <div class="d-flex justify-content-between align-items-center mb-3">
                <div>
                    <h5 class="fw-bold mb-1">Shift Schedules & Planned Breaks</h5>
                    <p class="text-muted small mb-0">Shift windows, operating hours, and statutory break deduction allowances.</p>
                </div>
            </div>
            <div class="table-card">
                <div class="table-responsive">
                    <table class="table table-hover align-middle">
                        <thead>
                            <tr>
                                <th>Shift Code</th>
                                <th>Name</th>
                                <th>Plant</th>
                                <th>Start Time</th>
                                <th>End Time</th>
                                <th>Planned Break</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody id="shifts-tbody"><tr><td colspan="7" class="text-center py-4 text-muted">Loading...</td></tr></tbody>
                    </table>
                </div>
            </div>
        `;

        this.loadShifts();
    },

    async loadShifts() {
        const tbody = document.getElementById("shifts-tbody");
        const shifts = await API.get("/shifts");
        tbody.innerHTML = shifts.map(s => `
            <tr>
                <td class="fw-bold font-monospace text-primary">${s.shift_code}</td>
                <td class="fw-semibold">${s.name}</td>
                <td>Plant #${s.plant_id}</td>
                <td class="font-monospace">${s.start_time}</td>
                <td class="font-monospace">${s.end_time}</td>
                <td><span class="badge bg-secondary-subtle text-secondary">${s.planned_break_minutes} minutes</span></td>
                <td><span class="badge ${s.is_active ? 'bg-success' : 'bg-secondary'}">${s.is_active ? 'Active' : 'Inactive'}</span></td>
            </tr>
        `).join("");
    },

    // -------------------------------------------------------------
    // Downtime Reasons
    // -------------------------------------------------------------
    async renderDowntimeReasons(container) {
        container.innerHTML = `
            <div class="d-flex justify-content-between align-items-center mb-3">
                <div>
                    <h5 class="fw-bold mb-1">Downtime Reasons Taxonomy</h5>
                    <p class="text-muted small mb-0">Standardized root causes categorized by planned vs unplanned stoppages.</p>
                </div>
                <button class="btn btn-primary btn-sm" id="btn-add-dtr"><i class="bi bi-plus-circle me-1"></i> Add Reason Code</button>
            </div>
            <div class="table-card">
                <div class="table-responsive">
                    <table class="table table-hover align-middle">
                        <thead>
                            <tr>
                                <th>Reason Code</th>
                                <th>Name</th>
                                <th>Category</th>
                                <th>Classification</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody id="dtr-tbody"><tr><td colspan="5" class="text-center py-4 text-muted">Loading...</td></tr></tbody>
                    </table>
                </div>
            </div>
        `;

        document.getElementById("btn-add-dtr").onclick = () => this.showDowntimeReasonModal();
        this.loadDowntimeReasons();
    },

    async loadDowntimeReasons() {
        const tbody = document.getElementById("dtr-tbody");
        const reasons = await API.get("/downtime-reasons");
        tbody.innerHTML = reasons.map(r => `
            <tr>
                <td class="fw-bold font-monospace text-primary">${r.reason_code}</td>
                <td class="fw-semibold">${r.name}</td>
                <td><span class="badge bg-light text-dark border">${r.category}</span></td>
                <td>
                    <span class="badge ${r.is_planned ? 'bg-secondary' : 'bg-danger'}">
                        ${r.is_planned ? 'Planned Downtime' : 'Unplanned Stoppage'}
                    </span>
                </td>
                <td>
                    <button class="btn btn-outline-danger btn-sm py-0 px-2" onclick="MasterDataPage.deleteDTR(${r.id})">Delete</button>
                </td>
            </tr>
        `).join("");
    },

    showDowntimeReasonModal() {
        const modalTitle = document.getElementById("genericModalTitle");
        const modalBody = document.getElementById("genericModalBody");
        const modalSubmit = document.getElementById("genericModalSubmit");

        modalTitle.textContent = "Register Downtime Reason Code";
        modalBody.innerHTML = `
            <div class="mb-3">
                <label class="form-label small fw-bold">Reason Code</label>
                <input type="text" id="m-dtr-code" class="form-control" placeholder="e.g. DTR-JAM-02" required>
            </div>
            <div class="mb-3">
                <label class="form-label small fw-bold">Reason Name</label>
                <input type="text" id="m-dtr-name" class="form-control" placeholder="e.g. Feeder Tape Splicing Stoppage" required>
            </div>
            <div class="mb-3">
                <label class="form-label small fw-bold">Category</label>
                <select id="m-dtr-cat" class="form-select">
                    <option value="UNPLANNED_DOWNTIME">UNPLANNED_DOWNTIME</option>
                    <option value="PLANNED_DOWNTIME">PLANNED_DOWNTIME</option>
                    <option value="CHANGEOVER">CHANGEOVER</option>
                    <option value="MAINTENANCE">MAINTENANCE</option>
                    <option value="BREAK">BREAK</option>
                </select>
            </div>
            <div class="form-check mb-3">
                <input class="form-check-input" type="checkbox" id="m-dtr-planned">
                <label class="form-check-label small" for="m-dtr-planned">
                    Is Planned Downtime (deducted as scheduled planned loss)
                </label>
            </div>
        `;

        modalSubmit.onclick = async () => {
            const reason_code = document.getElementById("m-dtr-code").value.trim();
            const name = document.getElementById("m-dtr-name").value.trim();
            const category = document.getElementById("m-dtr-cat").value;
            const is_planned = document.getElementById("m-dtr-planned").checked;

            try {
                await API.post("/downtime-reasons", { reason_code, name, category, is_planned });
                bootstrap.Modal.getInstance(document.getElementById("genericModal")).hide();
                App.showToast("Reason registered.", "success");
                MasterDataPage.loadDowntimeReasons();
            } catch (err) {
                App.showToast("Error: " + err.message, "danger");
            }
        };

        new bootstrap.Modal(document.getElementById("genericModal")).show();
    },

    async deleteDTR(id) {
        if (!confirm("Are you sure you want to delete this downtime reason?")) return;
        try {
            await API.delete(`/downtime-reasons/${id}`);
            App.showToast("Reason deleted.", "info");
            this.loadDowntimeReasons();
        } catch (e) {
            App.showToast("Error: " + e.message, "danger");
        }
    }
};
