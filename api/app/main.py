from fastapi import FastAPI

from app.deps import CurrentUser


def create_app() -> FastAPI:
    app = FastAPI(title="PetCare API", version="0.1.0")

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

    return app


app = create_app()
