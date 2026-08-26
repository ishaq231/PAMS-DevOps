from fastapi import FastAPI

from .auth_routes import router as auth_router
from .tenant_routes import router as tenant_router
from .fianance_routes import router as finance_router
from .frontdesk_routes import router as frontdesk_router

app = FastAPI(title="PAMS API")

app.include_router(auth_router)
app.include_router(tenant_router)
app.include_router(finance_router)
app.include_router(frontdesk_router)