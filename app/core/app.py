from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.router import api_router

RECRUITER_UI_DIR = Path(__file__).resolve().parents[1] / "ui" / "recruiter"


def create_app() -> FastAPI:
    app = FastAPI(
        title="Astro IT Profile",
        version="0.1.0",
        description="Portfolio backend: astrology + IT profile generator",
    )

    app.include_router(api_router)

    @app.get("/")
    def root():
        return {"message": "Astro IT Profile backend is running"}

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
