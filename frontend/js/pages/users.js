/**
 * FactoryPulse — User Management & RBAC Page
 */

const UsersPage = {
    async render(container) {
        container.innerHTML = `
            <div class="d-flex justify-content-between align-items-center mb-3">
                <div>
                    <h5 class="fw-bold mb-1">User Accounts & Role-Based Access Control (RBAC)</h5>
                    <p class="text-muted small mb-0">Manage system operators, engineers, and administrative permission tiers.</p>
                </div>
                <button class="btn btn-primary btn-sm" id="btn-add-user"><i class="bi bi-person-plus me-1"></i> Add User</button>
            </div>
            <div class="table-card">
                <div class="table-responsive">
                    <table class="table table-hover align-middle">
                        <thead>
                            <tr>
                                <th>Username</th>
                                <th>Full Name</th>
                                <th>Email</th>
                                <th>Assigned Role</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody id="users-tbody"><tr><td colspan="6" class="text-center py-4 text-muted">Loading users...</td></tr></tbody>
                    </table>
                </div>
            </div>
        `;

        document.getElementById("btn-add-user").onclick = () => this.showUserModal();
        this.loadUsers();
    },

    async loadUsers() {
        const tbody = document.getElementById("users-tbody");
        try {
            const users = await API.get("/users");
            tbody.innerHTML = users.map(u => {
                const roleColors = {
                    ADMIN: "bg-dark",
                    OPERATOR: "bg-primary",
                    MAINTENANCE: "bg-warning text-dark",
                    QUALITY: "bg-info text-dark",
                    PLANNER: "bg-success"
                };
                const badgeClass = roleColors[u.role] || "bg-secondary";

                return `
                    <tr>
                        <td class="fw-bold font-monospace text-primary">${u.username}</td>
                        <td class="fw-semibold">${u.full_name}</td>
                        <td class="text-muted">${u.email}</td>
                        <td><span class="badge ${badgeClass}">${u.role}</span></td>
                        <td><span class="badge ${u.is_active ? 'bg-success' : 'bg-secondary'}">${u.is_active ? 'Active' : 'Suspended'}</span></td>
                        <td>
                            <button class="btn btn-outline-danger btn-sm py-0 px-2" onclick="UsersPage.deleteUser(${u.id}, '${u.username}')">Delete</button>
                        </td>
                    </tr>
                `;
            }).join("");
        } catch (e) {
            tbody.innerHTML = `<tr><td colspan="6" class="text-danger text-center py-3">Error: ${e.message} (Requires ADMIN role)</td></tr>`;
        }
    },

    showUserModal() {
        const modalTitle = document.getElementById("genericModalTitle");
        const modalBody = document.getElementById("genericModalBody");
        const modalSubmit = document.getElementById("genericModalSubmit");

        modalTitle.textContent = "Create User Account";
        modalBody.innerHTML = `
            <div class="mb-3">
                <label class="form-label small fw-bold">Username</label>
                <input type="text" id="m-user-username" class="form-control" placeholder="e.g. operator2" required>
            </div>
            <div class="mb-3">
                <label class="form-label small fw-bold">Full Name</label>
                <input type="text" id="m-user-fullname" class="form-control" placeholder="Full name" required>
            </div>
            <div class="mb-3">
                <label class="form-label small fw-bold">Email Address</label>
                <input type="email" id="m-user-email" class="form-control" placeholder="user@factorypulse.internal" required>
            </div>
            <div class="mb-3">
                <label class="form-label small fw-bold">Role Assignment</label>
                <select id="m-user-role" class="form-select">
                    <option value="OPERATOR">OPERATOR (Log events & counts)</option>
                    <option value="MAINTENANCE">MAINTENANCE (Manage downtime & repairs)</option>
                    <option value="QUALITY">QUALITY (Quality inspections)</option>
                    <option value="PLANNER">PLANNER (Production orders & schedules)</option>
                    <option value="ADMIN">ADMIN (Full administrative privileges)</option>
                </select>
            </div>
            <div class="mb-3">
                <label class="form-label small fw-bold">Password</label>
                <input type="password" id="m-user-pwd" class="form-control" placeholder="Temporary password" required>
            </div>
        `;

        modalSubmit.onclick = async () => {
            const username = document.getElementById("m-user-username").value.trim();
            const full_name = document.getElementById("m-user-fullname").value.trim();
            const email = document.getElementById("m-user-email").value.trim();
            const role = document.getElementById("m-user-role").value;
            const password = document.getElementById("m-user-pwd").value;

            try {
                await API.post("/users", { username, full_name, email, role, password });
                bootstrap.Modal.getInstance(document.getElementById("genericModal")).hide();
                App.showToast("User account created.", "success");
                UsersPage.loadUsers();
            } catch (err) {
                App.showToast("Error: " + err.message, "danger");
            }
        };

        new bootstrap.Modal(document.getElementById("genericModal")).show();
    },

    async deleteUser(id, username) {
        if (!confirm(`Are you sure you want to delete user ${username}?`)) return;
        try {
            await API.delete(`/users/${id}`);
            App.showToast("User account deleted.", "info");
            this.loadUsers();
        } catch (e) {
            App.showToast("Cannot delete user: " + e.message, "danger");
        }
    }
};
