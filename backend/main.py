from fastapi import FastAPI
from api import wardrobe

app = FastAPI(title="Virtual Closet API", version="0.1.0")
app.include_router(wardrobe.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}