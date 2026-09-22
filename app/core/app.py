from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes.beta_access import router as beta_access_router
from app.api.router import api_router
from app.core.beta_middleware import BetaGateMiddleware
from app.core.runtime_checks import validate_runtime

RECRUITER_UI_DIR = Path(__file__).resolve().parents[1] / "ui" / "recruiter"


def create_app(*, run_startup_checks: bool = True) -> FastAPI:
    if run_startup_checks:
        validate_runtime()

    app = FastAPI(
        title="Astro IT Profile",
        version="0.1.0",
        description="Portfolio backend: astrology + IT profile generator",
    )

    app.add_middleware(BetaGateMiddleware)
    app.include_router(beta_access_router)
    app.include_router(api_router)

    @app.get("/")
    def root():
        return RedirectResponse(url="/recruiter", status_code=303)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.get("/recruiter", include_in_schema=False)
    def recruiter_prototype():
        return FileResponse(RECRUITER_UI_DIR / "index.html")

    app.mount(
        "/recruiter/assets",
        StaticFiles(directory=RECRUITER_UI_DIR),
        name="recruiter_assets",
    )

    return app
