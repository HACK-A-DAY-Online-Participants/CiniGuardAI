 CinemaGuard - Complete Project Documentation

Table of Contents

1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Features](#features)
4. [Technology Stack](#technology-stack)
5. [Project Structure](#project-structure)
6. [Installation & Setup](#installation--setup)
7. [Configuration](#configuration)
8. [Database Schema](#database-schema)
9. [Backend API Reference](#backend-api-reference)
10. [Frontend Pages](#frontend-pages)
11. [Detection System](#detection-system)
12. [WebSocket Communication](#websocket-communication)
13. [Deployment](#deployment)
14. [Troubleshooting](#troubleshooting)
15. [Development Guide](#development-guide)


Project Overview

**CinemaGuard** is an AI-powered anti-piracy security system designed to detect unauthorized phone usage in cinema theaters. The system uses YOLOv8n object detection to identify phones in real-time video feeds and provides zone-based tracking with risk assessment.

Key Capabilities

- **Real-time Phone Detection**: Uses YOLOv8n AI model to detect phones in video streams
- **Zone-based Tracking**: Maps detections to a configurable grid system (default 10×10)
- **Risk Assessment**: Calculates risk scores based on detection duration
- **Live Monitoring**: WebSocket-based real-time alerts and visualization
- **Cloud Database**: Supabase integration for persistent storage
- **Multi-camera Support**: Works with webcams, IP cameras, and RTSP streams



System Architecture

mermaid
graph TB
    subgraph Frontend
        A[Dashboard<br/>index.html] --> B[Grid Setup<br/>setup.html]
        A --> C[Live Monitor<br/>monitor.html]
    end
    
    subgraph Backend
        D[FastAPI Server<br/>main.py] --> E[Camera Module<br/>camera.py]
        D --> F[Detection Module<br/>detection.py]
        D --> G[Database Module<br/>db.py]
    end
    
    subgraph External
        H[Camera Source<br/>Webcam/IP Camera]
        I[Supabase Database]
        J[YOLOv8n Model]
    end
    
    C -->|WebSocket| D
    B -->|REST API| D
    E -->|Video Stream| H
    F -->|AI Detection| J
    G -->|Data Storage| I
    
    style A fill:#3b82f6
    style B fill:#3b82f6
    style C fill:#3b82f6
    style D fill:#ef4444
    style E fill:#ef4444
    style F fill:#ef4444
    style G fill:#ef4444
    style H fill:#10b981
    style I fill:#10b981
    style J fill:#10b981


Architecture Components

1. **Frontend Layer** (HTML + JavaScript + Alpine.js + Tailwind CSS)
   - Dashboard for overview and recent alerts
   - Grid setup interface for zone configuration
   - Live monitoring with real-time video feed

2. **Backend Layer** (Python + FastAPI)
   - RESTful API endpoints
   - WebSocket server for real-time communication
   - Video streaming with MJPEG
   - AI-powered detection pipeline

3. **Data Layer** (Supabase PostgreSQL)
   - Hall configurations
   - Grid mappings
   - Alert history

4. **AI Layer** (YOLOv8n)
   - Phone detection model
   - Real-time inference
   - Bounding box generation

---

Features

Implemented Features

1. **Phone Detection**
- YOLOv8n-based object detection
- Real-time inference on video streams
- Confidence threshold filtering
- Bounding box visualization

2. **Zone-based Tracking**
- Configurable grid system (rows × columns)
- Perspective transformation support
- Zone-to-detection mapping
- Stationary detection tracking

3. **Risk Assessment**
- Duration-based scoring
- Configurable thresholds (default: 3 seconds)
- High-risk alert triggering (≥80% risk score)
- Alert cooldown mechanism (5 seconds)

4. **Real-time Monitoring**
- Live MJPEG video stream
- WebSocket alerts
- Visual overlays (bounding boxes, grid)
- Alert history sidebar

5. **Grid Configuration**
- Interactive canvas-based setup
- Draggable corner points
- Perspective grid overlay
- Multiple preset options (10×10, 5×5, 20×10, 10×1)

6. **Database Integration**
- Supabase cloud database
- Hall management
- Grid configuration persistence
- Alert logging with timestamps

#### 7. **Multi-camera Support**
- Default webcam (index 0)
- IP cameras (HTTP streams)
- RTSP streams
- IP Webcam app integration



Technology Stack

Backend
| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.8+ | Core language |
| **FastAPI** | Latest | Web framework |
| **Uvicorn** | Latest | ASGI server |
| **OpenCV** | Latest | Video processing |
| **Ultralytics** | Latest | YOLOv8n detection |
| **Supabase** | Latest | Database client |
| **python-dotenv** | Latest | Environment variables |
| **WebSockets** | Latest | Real-time communication |

Frontend
| Technology | Version | Purpose |
|------------|---------|---------|
| **HTML5** | - | Structure |
| **Tailwind CSS** | 3.x | Styling |
| **Alpine.js** | 3.x | Reactivity |
| **Fabric.js** | 5.3.0 | Canvas manipulation |
| **Vanilla JavaScript** | ES6+ | Logic |

Infrastructure
| Service | Purpose |
|---------|---------|
| **Supabase** | PostgreSQL database |
| **YOLOv8n** | Pre-trained model (6.5MB) |



Project Structure


chini woring red/
├── app/
│   ├── __init__.py                 # Package initializer
│   ├── backend/
│   │   ├── __init__.py            # Backend package init
│   │   ├── main.py                # FastAPI application
│   │   ├── camera.py              # Video capture & streaming
│   │   ├── detection.py           # YOLOv8n detection logic
│   │   └── db.py                  # Supabase database operations
│   └── frontend/
│       ├── index.html             # Dashboard page
│       ├── setup.html             # Grid configuration page
│       └── monitor.html           # Live monitoring page
├── .env                           # Environment variables (gitignored)
├── .env.example                   # Environment template
├── .gitignore                     # Git ignore rules
├── requirements.txt               # Python dependencies
├── yolov8n.pt                     # YOLOv8n model weights
├── start.sh                       # Startup script (Linux/Mac)
├── SETUP_GUIDE.md                 # Installation instructions
├── SERVER_GUIDE.md                # Server management guide
└── DOCUMENTATION.md               # This file




Installation & Setup

Prerequisites

- Python 3.8 or higher
- pip package manager
- Webcam or IP camera
- Supabase account (free tier available)

Step 1: Clone/Download Project

bash
cd /path/to/project


Step 2: Install Python Dependencies

Option A: Using pip (recommended)**
bash
pip install -r requirements.txt


Option B: System packages (Linux)**
bash
sudo apt install python3-fastapi python3-opencv python3-dotenv
pip3 install ultralytics supabase --break-system-packages


1. Copy the example environment file:
bash
cp .env.example .env


2. Edit `.env` with your settings:
env
Supabase Configuration (REQUIRED)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key-here

Camera Settings
CAMERA_SOURCE=0                    # 0 for default webcam
CAMERA_SOURCE=http://192.168.1.37:8080/video  # IP Webcam
CAMERA_SOURCE=rtsp://user:pass@ip:port/stream # RTSP camera

Optional: Custom hall name
HALL_NAME=Cinema Hall 1


Step 4: Set Up Supabase Database

Create two tables in your Supabase project:

Table 1: halls
sql
CREATE TABLE halls (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT UNIQUE NOT NULL,
    grid_config JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);


Table 2: alerts
sql
CREATE TABLE alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    hall_id UUID REFERENCES halls(id) ON DELETE CASCADE,
    risk_score FLOAT8 NOT NULL,
    zone TEXT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_alerts_hall_id ON alerts(hall_id);
CREATE INDEX idx_alerts_timestamp ON alerts(timestamp DESC);


Step 5: Run the Server

Windows (PowerShell):
powershell
cd "c:\Users\Reyha\Downloads\chini woring red-20251123T024547Z-1-001\chini woring red"
uvicorn app.backend.main:app --reload


Linux/Mac:
bash
cd "/path/to/chini woring red"
uvicorn app.backend.main:app --reload --host 0.0.0.0 --port 8000


### Step 6: Access the Application

- **Dashboard**: http://localhost:8000/
- **Grid Setup**: http://localhost:8000/setup
- **Live Monitor**: http://localhost:8000/monitor
- **Health Check**: http://localhost:8000/health



Configuration

Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SUPABASE_URL` | Yes | - | Your Supabase project URL |
| `SUPABASE_KEY` | Yes | - | Supabase anonymous key |
| `CAMERA_SOURCE` | No | `0` | Camera source (index, URL, or RTSP) |
| `HALL_NAME` | No | `Cinema Hall 1` | Cinema hall identifier |

Camera Source Options

Default Webcam:
env
CAMERA_SOURCE=0


IP Webcam (Android app):
env
CAMERA_SOURCE=http://192.168.1.37:8080/video


DroidCam:
env
CAMERA_SOURCE=http://192.168.1.100:4747/video


RTSP Camera:
env
CAMERA_SOURCE=rtsp://username:password@192.168.1.50:554/stream


 Detection Parameters

Edit [`app/backend/detection.py`](file:///c:/Users/Reyha/Downloads/chini%20woring%20red-20251123T024547Z-1-001/chini%20woring%20red/app/backend/detection.py) to customize:

python
class PhoneDetector:
    PHONE_CLASS_ID = 67              # COCO class ID for cell phone
    STATIONARY_THRESHOLD = 3.0       # Seconds before triggering alert
    HIGH_RISK_SCORE = 0.8            # Risk threshold for high alerts
    ALERT_COOLDOWN = 5.0             # Seconds between alerts per zone




Database Schema

Table: `halls`

Stores cinema hall configurations and grid mappings.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY | Auto-generated unique identifier |
| `name` | TEXT | UNIQUE, NOT NULL | Hall name (e.g., "Cinema Hall 1") |
| `grid_config` | JSONB | - | Grid configuration JSON |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Creation timestamp |

**Grid Config JSON Structure:**
```json
{
  "corners": [
    {"x": 50, "y": 50},
    {"x": 750, "y": 50},
    {"x": 750, "y": 550},
    {"x": 50, "y": 550}
  ],
  "grid_rows": 10,
  "grid_cols": 10,
  "canvas_width": 800,
  "canvas_height": 600
}


Table: `alerts`

Logs all detection alerts with timestamps.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY | Auto-generated unique identifier |
| `hall_id` | UUID | FOREIGN KEY → halls(id) | Reference to hall |
| `risk_score` | FLOAT8 | NOT NULL | Risk score (0.0 to 1.0) |
| `zone` | TEXT | NOT NULL | Grid zone (e.g., "3,5") |
| `timestamp` | TIMESTAMP | DEFAULT NOW() | Alert timestamp |

**Indexes:**
- `idx_alerts_hall_id` on `hall_id`
- `idx_alerts_timestamp` on `timestamp DESC`



Backend API Reference

REST Endpoints

`GET /`
Description**: Serve the main dashboard page  
Response**: HTML page



 `GET /setup`
**Description**: Serve the grid setup page  
**Response**: HTML page



`GET /monitor`
**Description**: Serve the live monitoring page  
**Response**: HTML page



 `GET /health`
**Description**: Health check endpoint  
**Response**:
```json
{
  "status": "healthy",
  "camera": true,
  "detector": true
}




 `GET /video_feed`
**Description**: MJPEG video stream with detection overlay  
**Response**: `multipart/x-mixed-replace` stream



`GET /snapshot`
**Description**: Capture a single frame as JPEG  
**Response**: JPEG image



`GET /api/grid`
**Description**: Retrieve grid configuration for the current hall  
**Response**:
```json
{
  "grid_config": {
    "corners": [...],
    "grid_rows": 10,
    "grid_cols": 10,
    "canvas_width": 800,
    "canvas_height": 600
  }
}




 `POST /api/grid`
**Description**: Save grid configuration  
**Request Body**:
json
{
  "corners": [
    {"x": 50, "y": 50},
    {"x": 750, "y": 50},
    {"x": 750, "y": 550},
    {"x": 50, "y": 550}
  ],
  "grid_rows": 10,
  "grid_cols": 10,
  "canvas_width": 800,
  "canvas_height": 600
}

**Response**:
json
{
  "status": "success",
  "data": { ... }
}




#### `GET /api/alerts?limit=10`
**Description**: Get recent alerts  
**Query Parameters**:
- `limit` (optional): Number of alerts to retrieve (default: 10)

**Response**:
json
{
  "alerts": [
    {
      "id": "uuid",
      "hall_id": "uuid",
      "zone": "3,5",
      "risk_score": 0.85,
      "timestamp": "2025-11-23T08:15:30Z"
    }
  ]
}



WebSocket Endpoints

`WS /ws/alerts`
**Description**: Real-time alert and status updates

**Outgoing Messages (Server → Client):**

**Status Update:**
json
{
  "type": "status",
  "detections": 2,
  "active_zones": 2
}


**Alert:**
json
{
  "type": "alert",
  "zone": "3,5",
  "risk_score": 0.85,
  "bbox": [120, 80, 220, 280],
  "timestamp": 1700740530
}


Frontend Pages

1. Dashboard (`index.html`)

**Purpose**: Main landing page with navigation and recent alerts

**Features**:
- Navigation cards to Setup and Monitor pages
- Recent alerts table with auto-refresh (10s interval)
- Risk score visualization
- Responsive design

**Key Functions**:
- `alertsData()`: Alpine.js component for alert management
- `loadAlerts()`: Fetch alerts from API
- `formatTime()`: Format Unix timestamps



2. Grid Setup (`setup.html`)

**Purpose**: Configure detection zones with interactive canvas

**Features**:
- Capture frame from camera
- Drag 4 corner points to define screen area
- Adjustable grid size (rows × columns)
- Preset grid options (10×10, 5×5, 20×10, 10×1)
- Save configuration to database

**Key Functions**:
- `captureFrame()`: Fetch snapshot from `/snapshot`
- `initCanvas()`: Initialize Fabric.js canvas
- `createCorners()`: Create draggable corner points
- `updateGrid()`: Redraw grid lines
- `saveGrid()`: POST configuration to `/api/grid`

**Technologies**:
- Fabric.js for canvas manipulation
- Alpine.js for state management



3. Live Monitor (`monitor.html`)

**Purpose**: Real-time monitoring with video feed and alerts

**Features**:
- Live MJPEG video stream
- Canvas overlay for grid and bounding boxes
- WebSocket connection for real-time alerts
- Alert history sidebar
- High-risk alert banner
- Active detection/zone counters

**Key Functions**:
- `init()`: Initialize video, canvas, and WebSocket
- `connectWebSocket()`: Establish WS connection with auto-reconnect
- `handleAlert()`: Process incoming alerts
- `drawBoundingBox()`: Visualize detections on canvas
- `drawGrid()`: Render grid overlay
- `loadHistoricalAlerts()`: Fetch past alerts

**WebSocket Reconnection**:
- Exponential backoff strategy
- Max delay: 30 seconds
- Automatic retry on disconnect


Detection System

Detection Pipeline

mermaid
sequenceDiagram
    participant Camera
    participant VideoCamera
    participant Detector
    participant Database
    participant WebSocket
    
    Camera->>VideoCamera: Capture frame
    VideoCamera->>Detector: Process frame
    Detector->>Detector: Run YOLOv8n inference
    Detector->>Detector: Filter phone detections
    Detector->>Detector: Map to grid zones
    Detector->>Detector: Track duration
    
    alt Duration > 3s
        Detector->>Database: Save alert
        Detector->>WebSocket: Broadcast alert
    end
    
    Detector->>VideoCamera: Return detections
    VideoCamera->>Camera: Stream with overlay


Detection Logic

**File**: [`app/backend/detection.py`](file:///c:/Users/Reyha/Downloads/chini%20woring%20red-20251123T024547Z-1-001/chini%20woring%20red/app/backend/detection.py)

**Class**: `PhoneDetector`

**Key Methods**:

detect_phones(frame)
1. Run YOLOv8n inference on frame
2. Filter for phone class (ID: 67)
3. Extract bounding boxes
4. Map each detection to grid zone
5. Track duration per zone
6. Calculate risk score
7. Trigger alerts if threshold exceeded
8. Return detection list

**Detection Object Structure**:
python
{
    'bbox': (x1, y1, x2, y2),
    'confidence': 0.92,
    'zone': '3,5',
    'risk_score': 0.85,
    'duration': 4.2
}


`get_zone_from_bbox(bbox, frame_width, frame_height)`
Converts bounding box coordinates to grid zone identifier.

**Algorithm**:
1. Calculate center point of bounding box
2. Normalize to 0-1 range
3. Map to grid row/column
4. Return zone string (e.g., "3,5")

`_trigger_alert(zone, risk_score, bbox)`
1. Check alert cooldown
2. Save alert to database
3. Broadcast via WebSocket
4. Update last alert timestamp


WebSocket Communication

 Connection Flow

1. Client connects to `ws://localhost:8000/ws/alerts`
2. Server accepts connection and registers client
3. Server sends periodic status updates (1s interval)
4. Server broadcasts alerts when detections occur
5. Client handles disconnections with auto-reconnect

Message Types

**Status Update** (every 1 second):
json
{
  "type": "status",
  "detections": 2,
  "active_zones": 2
}


**Alert** (on detection):
```json
{
  "type": "alert",
  "zone": "3,5",
  "risk_score": 0.85,
  "bbox": [120, 80, 220, 280],
  "timestamp": 1700740530
}

**Reconnection Strategy** (exponential backoff):
```javascript
reconnectAttempts = 0;
delay = Math.min(1000 * Math.pow(2, reconnectAttempts - 1), 30000);
```

**Delays**:
- Attempt 1: 1 second
- Attempt 2: 2 seconds
- Attempt 3: 4 seconds
- Attempt 4: 8 seconds
- Attempt 5+: 30 seconds (max)



 Deployment

Production Deployment

1. **Server Setup**

**Recommended Specs**:
- CPU: 4+ cores
- RAM: 8GB+
- GPU: Optional (for faster inference)
- OS: Ubuntu 20.04+ / Windows Server

 2. **Install Dependencies**

bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python
sudo apt install python3.10 python3-pip -y

# Install project dependencies
pip3 install -r requirements.txt
```

#### 3. **Configure Environment**

```bash
# Create production .env
nano .env
```

Set production values:
```env
SUPABASE_URL=https://your-production-project.supabase.co
SUPABASE_KEY=your-production-key
CAMERA_SOURCE=rtsp://camera-ip:554/stream
HALL_NAME=Main Theater
```

#### 4. **Run with Systemd (Linux)**

Create service file:
```bash
sudo nano /etc/systemd/system/cinemaguard.service
```

```ini
[Unit]
Description=CinemaGuard Anti-Piracy System
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/cinemaguard
Environment="PATH=/usr/bin"
ExecStart=/usr/bin/uvicorn app.backend.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable cinemaguard
sudo systemctl start cinemaguard
```

#### 5. **Reverse Proxy (Nginx)**

```nginx
server {
    listen 80;
    server_name cinemaguard.example.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /ws/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

#### 6. **SSL Certificate (Let's Encrypt)**

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d cinemaguard.example.com




## Troubleshooting

### Common Issues

#### 1. **Camera Not Detected**

**Symptoms**: Black screen, "No frame available"

**Solutions**:
- Check `CAMERA_SOURCE` in `.env`
- Test camera URL in browser
- Verify camera is on same network
- Try default webcam: `CAMERA_SOURCE=0`

```bash
# Test IP Webcam
curl http://192.168.1.37:8080/video




#### 2. **Database Connection Failed**

**Symptoms**: "Failed to connect to Supabase"

**Solutions**:
- Verify `SUPABASE_URL` and `SUPABASE_KEY`
- Check Supabase project status
- Ensure tables exist (see [Database Schema](#database-schema))
- Check network connectivity

```bash
# Test Supabase connection
curl https://your-project.supabase.co/rest/v1/halls \
  -H "apikey: your-key"




#### 3. **Port Already in Use**

**Symptoms**: "Address already in use"

**Solutions**:

**Windows:**
```powershell
# Find process using port 8000
netstat -ano | findstr :8000
# Kill process
taskkill /PID <PID> /F
```

**Linux:**
```bash
# Find and kill process
sudo lsof -ti:8000 | xargs kill -9


Or use different port:
bash
uvicorn app.backend.main:app --port 8001




#### 4. **WebSocket Disconnects**

**Symptoms**: Frequent reconnections, "WebSocket disconnected"

**Solutions**:
- Check server logs for errors
- Verify network stability
- Increase reconnect delay
- Check firewall settings



#### 5. **Detection Not Working**

**Symptoms**: No bounding boxes, no alerts

**Solutions**:
- Verify YOLOv8n model exists (`yolov8n.pt`)
- Check detection confidence threshold
- Ensure phone is visible in frame
- Review server logs for errors

```bash
# Check model file
ls -lh yolov8n.pt




## Development Guide

### Setting Up Development Environment

```bash
# Clone repository
git clone <repository-url>
cd cinemaguard

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your settings
nano .env


### Running in Development Mode
bash
# Start server with auto-reload
uvicorn app.backend.main:app --reload --log-level debug

# Access application
open http://localhost:8000


### Code Structure Guidelines

**Backend (Python)**:
- Follow PEP 8 style guide
- Use type hints
- Add docstrings to functions
- Handle exceptions gracefully

**Frontend (JavaScript)**:
- Use ES6+ features
- Follow Alpine.js conventions
- Keep components modular
- Add comments for complex logic

### Testing

**Manual Testing Checklist**:
- [ ] Camera feed loads correctly
- [ ] Grid setup saves configuration
- [ ] Phone detection triggers alerts
- [ ] WebSocket connection stable
- [ ] Alerts appear in history
- [ ] Database stores data correctly

### Adding New Features

**Example: Add SMS Alerts**

1. Install Twilio SDK:
```bash
pip install twilio


2. Update `.env`:
env
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_PHONE_NUMBER=+1234567890
ALERT_PHONE_NUMBER=+0987654321


3. Modify [`detection.py`](file:///c:/Users/Reyha/Downloads/chini%20woring%20red-20251123T024547Z-1-001/chini%20woring%20red/app/backend/detection.py):
python
from twilio.rest import Client

def _trigger_alert(self, zone, risk_score, bbox):
    # Existing code...
    
    # Send SMS
    if risk_score >= self.HIGH_RISK_SCORE:
        self._send_sms_alert(zone, risk_score)

def _send_sms_alert(self, zone, risk_score):
    client = Client(os.getenv('TWILIO_ACCOUNT_SID'), 
                    os.getenv('TWILIO_AUTH_TOKEN'))
    message = client.messages.create(
        body=f"ALERT: Phone detected in zone {zone} (Risk: {risk_score*100}%)",
        from_=os.getenv('TWILIO_PHONE_NUMBER'),
        to=os.getenv('ALERT_PHONE_NUMBER')
    )




Performance Optimization

Recommended Settings

**For High-Resolution Cameras**:
python
In camera.py
self.video.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
self.video.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)


**For Faster Detection**:
python
n detection.py
results = self.model(frame, conf=0.5, iou=0.45, imgsz=640)


**For Lower Latency**:
python
In camera.py - _update_frame()
time.sleep(0.01)  # ~100 FPS capture rate




Security Considerations

Production Checklist

- [ ] Change default Supabase keys
- [ ] Enable HTTPS with SSL certificate
- [ ] Restrict CORS origins
- [ ] Add authentication middleware
- [ ] Secure WebSocket connections (WSS)
- [ ] Implement rate limiting
- [ ] Regular security updates
- [ ] Monitor access logs
 Example: Add Basic Auth

python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

security = HTTPBasic()

def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.username != "admin" or credentials.password != "secure_password":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    return credentials.username

@app.get("/monitor", dependencies=[Depends(verify_credentials)])
async def monitor_page():
    # Protected route




