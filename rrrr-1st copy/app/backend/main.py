"""
CinemaGuard - Anti-Piracy SaaS MVP
Main FastAPI application
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from pathlib import Path

from .camera import generate_mjpeg_stream, get_camera_instance
from .detection import get_detector
from .db import init_tables, save_grid_config, get_grid_config, get_recent_alerts

# Initialize FastAPI app
app = FastAPI(
    title="CinemaGuard",
    description="Anti-Piracy Cinema Security System",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (frontend)
frontend_path = Path(__file__).parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")


# Pydantic models
class GridConfig(BaseModel):
    corners: list
    grid_rows: int = 10
    grid_cols: int = 10
    canvas_width: int
    canvas_height: int


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize database tables on startup"""
    await init_tables()
    print("✓ CinemaGuard server started")


# Routes
@app.get("/")
async def index():
    """Serve the main dashboard"""
    index_file = frontend_path / "index.html"
    if index_file.exists():
        with open(index_file, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return {"message": "CinemaGuard API is running"}


@app.get("/setup")
async def setup_page():
    """Serve the grid setup page"""
    setup_file = frontend_path / "setup.html"
    if setup_file.exists():
        with open(setup_file, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return {"error": "Setup page not found"}


@app.get("/monitor")
async def monitor_page():
    """Serve the monitoring page"""
    monitor_file = frontend_path / "monitor.html"
    if monitor_file.exists():
        with open(monitor_file, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return {"error": "Monitor page not found"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "camera": get_camera_instance().video.isOpened() if get_camera_instance().video else False,
        "detector": get_detector().model is not None
    }


@app.get("/video_feed")
async def video_feed():
    """MJPEG video stream endpoint"""
    return StreamingResponse(
        generate_mjpeg_stream(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )


@app.get("/snapshot")
async def snapshot():
    """Get a single frame snapshot as JPEG"""
    from fastapi.responses import Response
    camera = get_camera_instance()
    frame_bytes = camera.get_jpeg_frame()
    if frame_bytes:
        return Response(content=frame_bytes, media_type="image/jpeg")
    return {"error": "No frame available"}


@app.get("/api/grid")
async def get_grid():
    """Get grid configuration"""
    from fastapi import HTTPException
    try:
        hall_name = os.getenv("HALL_NAME", "Cinema Hall 1")
        config = await get_grid_config(hall_name)
        return {"grid_config": config}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/grid")
async def save_grid(grid_config: GridConfig):
    """Save grid configuration"""
    from fastapi import HTTPException
    try:
        hall_name = os.getenv("HALL_NAME", "Cinema Hall 1")
        result = await save_grid_config(hall_name, grid_config.dict())
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/alerts")
async def get_alerts(limit: int = 10):
    """Get recent alerts"""
    from fastapi import HTTPException
    try:
        hall_name = os.getenv("HALL_NAME", "Cinema Hall 1")
        alerts = await get_recent_alerts(hall_name, limit)
        return {"alerts": alerts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/ws/alerts")
async def websocket_alerts(websocket: WebSocket):
    """WebSocket endpoint for real-time alerts"""
    await websocket.accept()
    detector = get_detector()
    detector.register_websocket(websocket)
    
    try:
        # Keep connection alive and process detections
        camera = get_camera_instance()
        
        while True:
            # Get frame and run detection
            frame = camera.get_frame()
            if frame is not None:
                detections = await detector.detect_phones(frame)
                
                # Send detection status (even if no phones detected)
                await websocket.send_json({
                    'type': 'status',
                    'detections': len(detections),
                    'active_zones': len(detector.zone_tracker)
                })
            
            # Wait a bit to avoid overwhelming the client
            import asyncio
            await asyncio.sleep(0.5)
            
    except WebSocketDisconnect:
        detector.unregister_websocket(websocket)
        print("WebSocket client disconnected")
    except Exception as e:
        print(f"WebSocket error: {e}")
        detector.unregister_websocket(websocket)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
