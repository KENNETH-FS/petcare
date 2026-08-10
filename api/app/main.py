from fastapi import FastAPI

from app.deps import CurrentUser
from app.errors import NotFoundError
from app.exception_handlers import register_exception_handlers


def create_app() -> FastAPI:
    app = FastAPI(title="PetCare API", version="0.1.0")
    register_exception_handlers(app)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/me")
    def me(current_user: CurrentUser):
        return {
            "id": current_user.id,
            "email": current_user.email,
            "role": current_user.role,
        }

    @app.get("/boom-404")
    def boom_404():
        raise NotFoundError("Test.", code="TEST_404")

    @app.get("/boom-500")
    def boom_500():
        return 1 / 0

    return app


app = create_app()
