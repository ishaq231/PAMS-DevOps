from fastapi import FastAPI

from .auth_routes import router as auth_router
from .tenant_routes import router as tenant_router
from .finance_routes import router as finance_router
from .frontdesk_routes import router as frontdesk_router
from .location_routes import router as location_router
from .apartment_routes import router as apartment_router
from .lease_routes import router as lease_router
from .maintenance_routes import router as maintenance_router
from .user_routes import router as user_router
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="PAMS API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://pams-devops-1.onrender.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_router)
app.include_router(tenant_router)
app.include_router(finance_router)
app.include_router(frontdesk_router)
app.include_router(location_router)
app.include_router(apartment_router)
app.include_router(lease_router)
app.include_router(maintenance_router)
app.include_router(user_router)