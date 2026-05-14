from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from core.config import settings
from api.routers import contact, telemetry
from db.database import engine, Base
from contextlib import asynccontextmanager
from core.limiter import limiter
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
import os
import pathlib
import shutil

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()

app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan
)

# Setup Rate Limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Setup Routers
app.include_router(contact.router, prefix=f"{settings.API_V1_STR}/contact", tags=["Contact"])
app.include_router(telemetry.router, prefix=f"{settings.API_V1_STR}/telemetry", tags=["Telemetry"])

# Mount artifacts directory for AI generated images
brain_dir = pathlib.Path(settings.BRAIN_DIR).resolve()
print(f"Mounting assets from: {brain_dir}")
app.mount("/assets", StaticFiles(directory=str(brain_dir)), name="assets")

# Ensure templates directory is current directory
templates = Jinja2Templates(directory=".")

@app.get("/sync-assets")
async def sync_assets():
    """Emergency asset synchronization for Vercel deployment."""
    source_dir = settings.BRAIN_DIR
    target_dir = os.path.join(os.getcwd(), "assets")
    
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    
    synced = []
    for file in os.listdir(source_dir):
        if file.endswith(".png"):
            shutil.copy(os.path.join(source_dir, file), os.path.join(target_dir, file))
            synced.append(file)
            
    return {"status": "success", "message": f"Synced {len(synced)} images to local assets folder", "files": synced}

@app.get("/", response_class=HTMLResponse)
async def serve_frontend(request: Request):
    return templates.TemplateResponse("code.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
