from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes.auth import router as auth_router
from backend.routes.bank_accounts import router as bank_router
from backend.routes.vaults import router as vaults_router
from backend.routes.allocation import router as allocation_router
from backend.routes.transactions import router as transactions_router
from backend.routes.dashboard import router as dashboard_router
from backend.routes.vault_rules import router as vault_rules_router
import backend.models

app = FastAPI(
    title="Vaults API",
    description="Digital envelope budgeting system",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(bank_router)
app.include_router(vaults_router)
app.include_router(allocation_router)
app.include_router(transactions_router)
app.include_router(dashboard_router)
app.include_router(vault_rules_router)


@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Vaults API is running"}