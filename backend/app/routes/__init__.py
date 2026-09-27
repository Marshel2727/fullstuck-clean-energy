"""Central registration for all implemented HTTP feature routers."""
from app.routes.auth import router as auth_router
from app.routes.package import router as package_router
from app.routes.article import router as article_router
from app.routes.faq import router as faq_router
from app.routes.archive import router as archive_router
from app.routes.system import router as system_router
from app.routes.customer import router as customer_router
from app.routes.dashboard import router as dashboard_router
from app.routes.energy import router as energy_router
from app.routes.installation import router as installation_router
from app.routes.health import router as health_router

routers = (
    auth_router, package_router, article_router, faq_router, archive_router,
    system_router, customer_router, dashboard_router, energy_router,
    installation_router, health_router,
)
