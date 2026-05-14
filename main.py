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

# Ensure templates directory is absolute for Vercel
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=BASE_DIR)

# Dynamic Asset Mounting
production_assets = os.path.join(BASE_DIR, "assets")
if os.path.exists(production_assets):
    app.mount("/assets", StaticFiles(directory=production_assets), name="assets")
else:
    app.mount("/assets", StaticFiles(directory=str(settings.BRAIN_DIR)), name="assets")

@app.get("/", response_class=HTMLResponse)
async def serve_frontend(request: Request):
    return templates.TemplateResponse("code.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
