/**
 * FactoryPulse — Master Application Router & State Manager
 */

const App = {
    currentRoute: "dashboard",

    routes: {
        "dashboard": { title: "Main Dashboard", handler: (c) => DashboardPage.render(c) },
        "monitoring": { title: "Machine Monitoring", handler: (c) => MonitoringPage.render(c) },
        "oee": { title: "OEE Analytics & Factor Decomposition", handler: (c) => OEEPage.render(c) },
        "anomalies": { title: "Anomaly Detection & Ground Truth", handler: (c) => AnomaliesPage.render(c) },
        "assistant": { title: "AI Analytics Assistant", handler: (c) => AssistantPage.render(c) },
        "orders": { title: "Production Orders", handler: (c) => ProductionPage.renderOrders(c) },
        "counts": { title: "Production Counts Ledger", handler: (c) => ProductionPage.renderCounts(c) },
        "inspections": { title: "Quality Inspections", handler: (c) => ProductionPage.renderInspections(c) },
        "downtime": { title: "Downtime Management", handler: (c) => ProductionPage.renderDowntime(c) },
        "reports": { title: "Reports & Data Exports", handler: (c) => ReportsPage.render(c) },
        "plants": { title: "Manufacturing Plants", handler: (c) => MasterDataPage.renderPlants(c) },
        "lines": { title: "Production Lines", handler: (c) => MasterDataPage.renderLines(c) },
        "machines": { title: "Equipment & Work Centers", handler: (c) => MasterDataPage.renderMachines(c) },
        "products": { title: "Product Catalog & Cycle Times", handler: (c) => MasterDataPage.renderProducts(c) },
        "shifts": { title: "Shift Schedules", handler: (c) => MasterDataPage.renderShifts(c) },
        "downtime-reasons": { title: "Downtime Reasons Taxonomy", handler: (c) => MasterDataPage.renderDowntimeReasons(c) },
        "users": { title: "User Management & RBAC", handler: (c) => UsersPage.render(c) },
        "settings": { title: "System & Database Configuration", handler: (c) => SettingsPage.render(c) }
    },

    init() {
        console.log("Initializing FactoryPulse platform UI...");
        Auth.init();

        // Listen for hash changes
        window.addEventListener("hashchange", () => {
            const route = window.location.hash.replace("#", "") || "dashboard";
            this.navigate(route);
        });

        // Toggle mobile sidebar
        const toggleBtn = document.getElementById("sidebar-toggle-btn");
        if (toggleBtn) {
            toggleBtn.onclick = () => {
                document.getElementById("sidebar").classList.toggle("show");
            };
        }

        // Close sidebar when clicking links on mobile
        document.querySelectorAll(".sidebar-nav .nav-link").forEach(link => {
            link.addEventListener("click", () => {
                if (window.innerWidth < 992) {
                    document.getElementById("sidebar").classList.remove("show");
                }
            });
        });

        // Initial navigation
        const initialRoute = window.location.hash.replace("#", "") || "dashboard";
        this.navigate(initialRoute);
    },

    navigate(routeName) {
        if (!this.routes[routeName]) {
            routeName = "dashboard";
        }
        this.currentRoute = routeName;

        // Update active class in sidebar
        document.querySelectorAll(".sidebar-nav .nav-link").forEach(link => {
            if (link.getAttribute("data-page") === routeName) {
                link.classList.add("active");
            } else {
                link.classList.remove("active");
            }
        });

        // Update page title
        const config = this.routes[routeName];
        const titleEl = document.getElementById("current-page-title");
        if (titleEl) {
            titleEl.textContent = config.title;
        }
        document.title = `${config.title} — FactoryPulse`;

        // Render page view
        const container = document.getElementById("app-view");
        if (container) {
            container.innerHTML = `<div class="text-center py-5"><div class="spinner-border text-primary" role="status"></div></div>`;
            try {
                config.handler(container);
            } catch (err) {
                console.error(`Error rendering route ${routeName}:`, err);
                container.innerHTML = `<div class="alert alert-danger">Error rendering page: ${err.message}</div>`;
            }
        }
    },

    showToast(message, type = "success") {
        const toastEl = document.getElementById("liveToast");
        const bodyEl = document.getElementById("toast-message");
        if (!toastEl || !bodyEl) return;

        bodyEl.textContent = message;
        toastEl.className = `toast align-items-center text-white border-0 bg-${type}`;

        const toast = new bootstrap.Toast(toastEl, { delay: 3500 });
        toast.show();
    }
};

// Start application when DOM is ready
document.addEventListener("DOMContentLoaded", () => {
    App.init();
});
