/**
 * FactoryPulse — Authentication Controller
 */

const Auth = {
    modalInstance: null,

    init() {
        const modalEl = document.getElementById("loginModal");
        if (modalEl) {
            this.modalInstance = new bootstrap.Modal(modalEl, { backdrop: "static", keyboard: false });
        }

        const loginForm = document.getElementById("login-form");
        if (loginForm) {
            loginForm.addEventListener("submit", (e) => this.handleLogin(e));
        }

        const logoutBtn = document.getElementById("logout-btn");
        if (logoutBtn) {
            logoutBtn.addEventListener("click", () => this.handleLogout());
        }

        // Check active session on initial load
        this.checkAuth();
    },

    async checkAuth() {
        const token = API.getToken();
        if (!token) {
            this.showLoginModal();
            return false;
        }

        try {
            const user = await API.get("/auth/me");
            API.setCurrentUser(user);
            this.updateUserUI(user);
            return true;
        } catch (err) {
            this.showLoginModal();
            return false;
        }
    },

    showLoginModal() {
        if (this.modalInstance) {
            this.modalInstance.show();
        }
    },

    hideLoginModal() {
        if (this.modalInstance) {
            this.modalInstance.hide();
        }
    },

    async handleLogin(e) {
        e.preventDefault();
        const username = document.getElementById("login-username").value.trim();
        const password = document.getElementById("login-password").value;
        const errAlert = document.getElementById("login-error-alert");
        const submitBtn = document.getElementById("login-submit-btn");

        errAlert.classList.add("d-none");
        submitBtn.disabled = true;
        submitBtn.innerHTML = `<span class="spinner-border spinner-border-sm me-1" role="status"></span> Signing in...`;

        try {
            const res = await API.post("/auth/login", { username, password });
            API.setToken(res.access_token);
            API.setCurrentUser(res.user);
            this.updateUserUI(res.user);
            this.hideLoginModal();
            App.showToast("Signed in successfully as " + res.user.full_name, "success");

            // Load initial view or current hash
            const currentRoute = window.location.hash.replace("#", "") || "dashboard";
            App.navigate(currentRoute);
        } catch (error) {
            errAlert.textContent = error.message || "Invalid username or password";
            errAlert.classList.remove("d-none");
        } finally {
            submitBtn.disabled = false;
            submitBtn.innerHTML = `<i class="bi bi-box-arrow-in-right me-1"></i> Sign In to Platform`;
        }
    },

    async handleLogout() {
        try {
            await API.post("/auth/logout").catch(() => {});
        } finally {
            API.clearToken();
            App.showToast("Signed out", "info");
            this.showLoginModal();
        }
    },

    updateUserUI(user) {
        if (!user) return;
        const nameEl = document.getElementById("topbar-user-name");
        const roleEl = document.getElementById("topbar-user-role");
        const avatarEl = document.getElementById("topbar-user-avatar");

        if (nameEl) nameEl.textContent = user.full_name;
        if (roleEl) roleEl.textContent = user.role;
        if (avatarEl) avatarEl.textContent = (user.username || "A").substring(0, 1).toUpperCase();
    },

    hasRole(...roles) {
        const u = API.getCurrentUser();
        if (!u) return false;
        if (u.role === "ADMIN") return true;
        return roles.includes(u.role);
    }
};
