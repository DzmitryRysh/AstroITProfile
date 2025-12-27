from fastapi import FastAPI
app = FastAPI(
    title="Astro IT Profile",
    version="0.1.0",
    description="Portfolio backend: astrology + IT profile generator",
)

@app.get("/")
def root():
    return {"message": "Astro IT Profile backend is running"}


