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
    # Initialize DB (Safe for Serverless)
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        print(f"Database initialization skipped or failed: {e}")
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
app.mount("/brain", StaticFiles(directory=str(settings.BRAIN_DIR)), name="brain")

@app.get("/", response_class=HTMLResponse)
async def serve_frontend(request: Request):
    try:
        brain_dir = str(settings.BRAIN_DIR)
        dst_dir = os.path.join(BASE_DIR, "assets")
        os.makedirs(dst_dir, exist_ok=True)
        
        copies = [
            ("orange_neural_universe_v4_1787048972596.png", "orange_neural_universe_v4.png"),
            ("media__1787049693108.png", "trustscope_ui_v2.png"),
            ("media__1787049384093.png", "degradx_ui_v2.png"),
            ("media__1787049549912.png", "emotion_ai_ui_v2.png"),
        ]
        for src_name, dst_name in copies:
            src_path = os.path.join(brain_dir, src_name)
            dst_path = os.path.join(dst_dir, dst_name)
            if os.path.exists(src_path) and not os.path.exists(dst_path):
                shutil.copy(src_path, dst_path)
    except Exception as e:
        pass
    return templates.TemplateResponse("code.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
