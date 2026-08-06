from fastapi import FastAPI
from api import wardrobe, users
from services.storage import ensure_bucket_exists

app = FastAPI(title="Virtual Closet API", version="0.1.0")

app.include_router(wardrobe.router)
app.include_router(users.router)

@app.on_event("startup")
def on_startup():
    ensure_bucket_exists()

@app.get("/health")
def health_check():
    return {"status": "ok"}