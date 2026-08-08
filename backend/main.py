from fastapi import FastAPI
from api import wardrobe, users, tryon
from services.storage import ensure_bucket_exists
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Virtual Closet API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(wardrobe.router)
app.include_router(users.router)
app.include_router(tryon.router)

@app.on_event("startup")
def on_startup():
    ensure_bucket_exists()

@app.get("/health")
def health_check():
    return {"status": "ok"}