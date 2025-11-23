# CinemaGuard Setup Guide

## Quick Start

### 1. Install System Dependencies

```bash
# Install uvicorn
sudo apt install uvicorn

# Install Python packages
sudo apt install python3-fastapi python3-opencv python3-dotenv
```

### 2. Install Python Dependencies (Alternative Method)

If you prefer using pip with virtual environment:

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Install Ultralytics (YOLO)

```bash
# System-wide
sudo apt install python3-pip
pip3 install ultralytics --break-system-packages

# OR in virtual environment
source venv/bin/activate
pip install ultralytics
```

### 4. Install Supabase Client

```bash
# System-wide
pip3 install supabase --break-system-packages

# OR in virtual environment
pip install supabase
```

### 5. Configure Environment

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` with your settings:
```
CAMERA_SOURCE=0
HALL_NAME=Cinema Hall 1
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

### 6. Run the Server

```bash
# From project directory
cd "/home/reyhan/Desktop/rrrr-1st copy"

# Run with uvicorn
uvicorn app.backend.main:app --reload --host 0.0.0.0 --port 8000
```

### 7. Access the Application

- **Dashboard**: http://localhost:8000/
- **Setup Grid**: http://localhost:8000/setup
- **Live Monitor**: http://localhost:8000/monitor

## Complete Dependency List

The `requirements.txt` includes:
- `fastapi` - Web framework
- `uvicorn[standard]` - ASGI server
- `opencv-python` - Computer vision
- `ultralytics` - YOLOv8 detection
- `supabase` - Database client
- `python-dotenv` - Environment variables
- `python-multipart` - File uploads
- `websockets` - Real-time alerts

## Troubleshooting

### "ModuleNotFoundError: No module named 'fastapi'"
```bash
sudo apt install python3-fastapi
# OR
pip3 install fastapi --break-system-packages
```

### "ModuleNotFoundError: No module named 'cv2'"
```bash
sudo apt install python3-opencv
```

### "ModuleNotFoundError: No module named 'ultralytics'"
```bash
pip3 install ultralytics --break-system-packages
```

### Camera not detected
- Check `CAMERA_SOURCE` in `.env`
- Try `CAMERA_SOURCE=0` for default webcam
- For RTSP: `CAMERA_SOURCE=rtsp://username:password@ip:port/stream`

## Features

✅ **Red Phone Detection Indicators** - Shows red bounding boxes and labels on detected phones  
✅ **Real-time Monitoring** - Live camera feed with detection overlay  
✅ **WebSocket Alerts** - Instant notifications when phones detected  
✅ **Grid-based Tracking** - 10x10 zone tracking system  
✅ **Risk Assessment** - Duration-based risk scoring  

## Testing Phone Detection

1. Start the server
2. Open http://localhost:8000/monitor
3. Point your camera at a phone
4. You should see:
   - Red bounding box around the phone
   - "PHONE DETECTED" label
   - Alert in the sidebar after 30 seconds
