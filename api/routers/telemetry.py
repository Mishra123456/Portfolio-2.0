from fastapi import APIRouter, Request
from api.schemas import TelemetryEvent
import logging
import json

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/event")
async def track_event(event: TelemetryEvent, request: Request):
    """
    Endpoint to track visitor interactions and session telemetry.
    Logs to the terminal for real-time monitoring.
    """
    visitor_ip = request.client.host
    log_data = {
        "ip": visitor_ip,
        "type": event.event_type,
        "duration": event.duration_seconds,
        "metadata": event.metadata
    }
    
    logger.info(f"TELEMETRY: {json.dumps(log_data)}")
    return {"status": "recorded"}

# In-memory session tracking (simplified)
active_sessions = set()

@router.get("/live-stats")
async def get_live_stats():
    """
    Returns the current active neural links (mocked for simplicity but ready for redis/memcached).
    """
    import random
    # Simulation logic for '11/10' feel
    count = random.randint(3, 12) 
    return {"active_links": count}
