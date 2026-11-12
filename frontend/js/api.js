/**
 * FactoryPulse — API Client
 * Manages JWT tokens, JSON requests, and backend endpoints.
 */

const API = {
    BASE_URL: "/api/v1",

    getToken() {
        return localStorage.getItem("factorypulse_token");
    },

    setToken(token) {
        localStorage.setItem("factorypulse_token", token);
    },

    clearToken() {
        localStorage.removeItem("factorypulse_token");
        localStorage.removeItem("factorypulse_user");
    },

    getCurrentUser() {
        const u = localStorage.getItem("factorypulse_user");
        return u ? JSON.parse(u) : null;
    },

    setCurrentUser(user) {
        localStorage.setItem("factorypulse_user", JSON.stringify(user));
    },

    async request(endpoint, options = {}) {
        const url = `${this.BASE_URL}${endpoint}`;
        const headers = {
            "Content-Type": "application/json",
            ...(options.headers || {})
        };

        const token = this.getToken();
        if (token) {
            headers["Authorization"] = `Bearer ${token}`;
        }

        try {
            const response = await fetch(url, {
                ...options,
                headers
            });

            if (response.status === 401) {
                this.clearToken();
                window.location.hash = "#login";
                Auth.showLoginModal();
                throw new Error("Session expired. Please sign in again.");
            }

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ detail: response.statusText }));
                const message = errorData.detail || `Request failed with status ${response.status}`;
                throw new Error(message);
            }

            // If empty response (204 No Content)
            if (response.status === 204) {
                return null;
            }

            return await response.json();
        } catch (error) {
            console.error(`API Error on [${options.method || "GET"} ${endpoint}]:`, error);
            throw error;
        }
    },

    get(endpoint, params = {}) {
        const queryString = new URLSearchParams(
            Object.entries(params).filter(([_, v]) => v !== undefined && v !== null && v !== "")
        ).toString();
        const fullUrl = queryString ? `${endpoint}?${queryString}` : endpoint;
        return this.request(fullUrl, { method: "GET" });
    },

    post(endpoint, data = {}) {
        return this.request(endpoint, {
            method: "POST",
            body: JSON.stringify(data)
        });
    },

    put(endpoint, data = {}) {
        return this.request(endpoint, {
            method: "PUT",
            body: JSON.stringify(data)
        });
    },

    delete(endpoint) {
        return this.request(endpoint, { method: "DELETE" });
    }
};
