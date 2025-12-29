from fastapi import FastAPI
from app.api.router import api_router

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

    return app