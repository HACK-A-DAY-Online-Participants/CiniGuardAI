"""
CinemaGuard - Anti-Piracy SaaS MVP
Main FastAPI application
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, Form, Depends, HTTPException, status
from fastapi.responses import StreamingResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyCookie
from pydantic import BaseModel
import os
from pathlib import Path
import secrets

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


# Authentication
COOKIE_NAME = "session_token"
# In a real app, use a secure random token storage. For this MVP, a single static token is fine or just check presence.
# We'll use a simple hardcoded check for simplicity as requested.
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "12345"
SESSION_TOKEN = "hardcoded-session-token-secret" 

oauth2_scheme = APIKeyCookie(name=COOKIE_NAME, auto_error=False)

async def get_current_user(request: Request):
    token = request.cookies.get(COOKIE_NAME)
    if token != SESSION_TOKEN:
        # If it's an API call, return 401. If it's a page load, redirect to login.
        # For simplicity, we'll raise HTTPException which FastAPI handles, 
        # but for better UX on browser, we might want to redirect.
        # Let's check the accept header or path.
        if request.url.path.startswith("/api") or request.url.path.startswith("/video_feed"):
             raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
            )
        return None # Signal to route handler to redirect
    return "admin"

async def get_current_user_or_redirect(request: Request):
    user = await get_current_user(request)
    if user is None:
        raise HTTPException(status_code=307, headers={"Location": "/login"})
    return user


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize database tables and verify system components on startup"""
    print("\n" + "="*50)
    print("🎬 CinemaGuard Starting Up...")
    print("="*50)
    
    # 1. Verify database connection and tables
    try:
        await init_tables()
        print("✓ Database connection verified")
    except Exception as e:
        print(f"✗ CRITICAL: Database initialization failed: {e}")
        print("  Please check your SUPABASE_URL and SUPABASE_KEY in .env")
        raise
    
    # 2. Verify camera connection
    try:
        camera = get_camera_instance()
        if camera.video and camera.video.isOpened():
            print("✓ Camera connected and ready")
        else:
            print("⚠ WARNING: Camera not connected")
            print("  Check CAMERA_SOURCE in .env (default: webcam 0)")
    except Exception as e:
        print(f"⚠ WARNING: Camera check failed: {e}")
    
    # 3. Verify detector model
    try:
        detector = get_detector()
        if detector.model is not None:
            print("✓ YOLOv8n detection model loaded")
            print(f"  Alert threshold: {detector.STATIONARY_THRESHOLD}s")
            print(f"  Alert cooldown: {detector.ALERT_COOLDOWN}s")
        else:
            print("⚠ WARNING: Detection model not loaded")
    except Exception as e:
        print(f"⚠ WARNING: Detector check failed: {e}")
    
    print("="*50)
    print("✓ CinemaGuard server started successfully")
    print("  Access the dashboard at: http://localhost:8000")
    print("  Monitor page at: http://localhost:8000/monitor")
    print("="*50 + "\n")


# Routes

@app.get("/login")
async def login_page():
    """Serve the login page"""
    login_file = frontend_path / "login.html"
    if login_file.exists():
        with open(login_file, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="Login page not found", status_code=404)

@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    """Handle login submission"""
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
        response.set_cookie(key=COOKIE_NAME, value=SESSION_TOKEN, httponly=True)
        return response
    
    # Return login page with error (simplified for now, just redirect back to login)
    # In a real app, we'd render the template with an error message.
    return RedirectResponse(url="/login?error=invalid", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/logout")
async def logout():
    """Handle logout"""
    response = RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(COOKIE_NAME)
    return response


@app.get("/")
async def index(user: str = Depends(get_current_user_or_redirect)):
    """Serve the main dashboard"""
    index_file = frontend_path / "index.html"
    if index_file.exists():
        with open(index_file, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return {"message": "CinemaGuard API is running"}


@app.get("/setup")
async def setup_page(user: str = Depends(get_current_user_or_redirect)):
    """Serve the grid setup page"""
    setup_file = frontend_path / "setup.html"
    if setup_file.exists():
        with open(setup_file, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return {"error": "Setup page not found"}


@app.get("/monitor")
async def monitor_page(user: str = Depends(get_current_user_or_redirect)):
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
async def video_feed(user: str = Depends(get_current_user_or_redirect)):
    """MJPEG video stream endpoint with phone detection overlay"""
    return StreamingResponse(
        generate_mjpeg_stream(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )


@app.get("/snapshot")
async def snapshot(user: str = Depends(get_current_user_or_redirect)):
    """Get a single frame snapshot as JPEG"""
    from fastapi.responses import Response
    camera = get_camera_instance()
    frame_bytes = camera.get_jpeg_frame()
    if frame_bytes:
        return Response(content=frame_bytes, media_type="image/jpeg")
    return {"error": "No frame available"}


@app.get("/api/grid")
async def get_grid(user: str = Depends(get_current_user_or_redirect)):
    """Get grid configuration"""
    from fastapi import HTTPException
    try:
        hall_name = os.getenv("HALL_NAME", "Cinema Hall 1")
        config = await get_grid_config(hall_name)
        return {"grid_config": config}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/grid")
async def save_grid(grid_config: GridConfig, user: str = Depends(get_current_user_or_redirect)):
    """Save grid configuration"""
    from fastapi import HTTPException
    try:
        hall_name = os.getenv("HALL_NAME", "Cinema Hall 1")
        result = await save_grid_config(hall_name, grid_config.dict())
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/alerts")
async def get_alerts(limit: int = 10, user: str = Depends(get_current_user_or_redirect)):
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
    """WebSocket endpoint for real-time alerts and status updates"""
    # Note: WebSockets are harder to protect with cookies in standard JS WebSocket API without extra work.
    # For this MVP, we'll leave it open or check cookie in handshake if possible.
    # Checking cookie in handshake:
    cookie = websocket.cookies.get(COOKIE_NAME)
    if cookie != SESSION_TOKEN:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await websocket.accept()
    detector = get_detector()
    detector.register_websocket(websocket)
    
    print(f"WebSocket client connected: {websocket.client}")
    
    try:
        # Keep connection alive and send periodic status updates
        # Note: Detection happens in the video_feed endpoint, alerts are broadcast via detector
        import asyncio
        
        while True:
            # Send periodic status updates
            await websocket.send_json({
                'type': 'status',
                'detections': len(detector.zone_tracker),
                'active_zones': len(detector.zone_tracker)
            })
            
            # Wait before next status update
            await asyncio.sleep(1.0)
            
    except WebSocketDisconnect:
        detector.unregister_websocket(websocket)
        print(f"WebSocket client disconnected: {websocket.client}")
    except Exception as e:
        print(f"WebSocket error: {e}")
        detector.unregister_websocket(websocket)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
