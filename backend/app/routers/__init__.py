from backend.app.routers.auth import router as auth_router
from backend.app.routers.users import router as users_router
from backend.app.routers.plants import router as plants_router
from backend.app.routers.lines import router as lines_router
from backend.app.routers.machines import router as machines_router
from backend.app.routers.shifts import router as shifts_router
from backend.app.routers.products import router as products_router
from backend.app.routers.downtime import router as downtime_router
from backend.app.routers.production_orders import router as po_router
from backend.app.routers.machine_events import router as events_router
from backend.app.routers.production_counts import router as counts_router
from backend.app.routers.quality_inspections import router as qc_router
from backend.app.routers.oee import router as oee_router
from backend.app.routers.anomalies import router as anomalies_router
from backend.app.routers.reports import router as reports_router
from backend.app.routers.assistant import router as assistant_router

__all__ = [
    "auth_router",
    "users_router",
    "plants_router",
    "lines_router",
    "machines_router",
    "shifts_router",
    "products_router",
    "downtime_router",
    "po_router",
    "events_router",
    "counts_router",
    "qc_router",
    "oee_router",
    "anomalies_router",
    "reports_router",
    "assistant_router"
]
