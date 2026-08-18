from fastapi import FastAPI, Response, status
from sqlalchemy import text

from app.deps import CurrentUser, DbSession
from app.exception_handlers import register_exception_handlers
from app.logging_config import configure_logging
from app.middleware import RequestIdMiddleware
from app.routers import appointments, clinics, pets

configure_logging()


def create_app() -> FastAPI:
    app = FastAPI(title="PetCare API", version="0.1.0")
    app.add_middleware(RequestIdMiddleware)
    register_exception_handlers(app)

    app.include_router(appointments.router)
    app.include_router(clinics.router)
    app.include_router(pets.router)

    @app.get("/health")
    def health(db: DbSession, response: Response) -> dict[str, str]:
        try:
            db.execute(text("SELECT 1"))
        except Exception:
            response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
            return {"status": "degraded", "database": "down"}
        return {"status": "ok", "database": "up"}

    @app.get("/me")
    def me(current_user: CurrentUser):
        return {
            "id": current_user.id,
            "email": current_user.email,
            "role": current_user.role,
        }

    return app


app = create_app()
