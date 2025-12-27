from fastapi import FastAPI
app = FastAPI()

@app.get("/")
def root():
    return {"message": "Astro IT Profile backend is running"}


