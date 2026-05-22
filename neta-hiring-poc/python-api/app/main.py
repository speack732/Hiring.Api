from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes.auth import router as auth_router
from app.api.routes.employees import router as employees_router
from app.core.logging import configure_logging
from app.db.session import SessionLocal
from app.services.identity_seed import seed_admin_user


configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    db = SessionLocal()
    try:
        seed_admin_user(db)
    finally:
        db.close()

    yield


app = FastAPI(
    title="NetaSystems Hiring API",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(auth_router)
app.include_router(employees_router)

@app.get("/")
def root():
    return {
        "message": "NetaSystems Hiring API running"
    }
