# 🎬 CinemaGuard - Server Management Guide

## ✅ Current Status

**Server:** 🟢 Running  
**URL:** http://localhost:8000  
**Camera:** IP Webcam (192.168.1.37:8080)  
**Detection:** YOLOv8n Active  

---

## 🚀 Start/Stop Commands

### Stop the Server
Press `Ctrl + C` in the terminal running uvicorn

### Start the Server
```powershell
cd c:\Users\Reyha\Downloads\rrrrrrrrrrrrrrrr
uvicorn app.backend.main:app --reload
```

### Restart the Server
1. Stop: `Ctrl + C`
2. Start: Run the command above

---

## 🎥 Camera Configuration

**Current Setup:** IP Webcam  
**URL:** http://192.168.1.37:8080/video

### To Change Camera Source:

Edit `.env` file and update line 4:

**IP Webcam:**
```env
CAMERA_SOURCE=http://192.168.1.37:8080/video
```

**Default Webcam:**
```env
CAMERA_SOURCE=0
```

**DroidCam:**
```env
CAMERA_SOURCE=http://YOUR_IP:4747/video
```

After editing `.env`, the server auto-reloads (no restart needed)!

---

## 📱 Access Points

| Page | URL | Purpose |
|------|-----|---------|
| **Dashboard** | http://localhost:8000/ | Main landing page |
| **Grid Setup** | http://localhost:8000/setup | Configure detection zones |
| **Live Monitor** | http://localhost:8000/monitor | Real-time monitoring |
| **Video Feed** | http://localhost:8000/video_feed | Raw MJPEG stream |
| **Health Check** | http://localhost:8000/health | Server status |

---

## 🔍 Troubleshooting

### Camera Not Working?

1. **Check IP Webcam app** is running on your phone
2. **Verify network:** Phone and PC on same WiFi
3. **Test in browser:** Open http://192.168.1.37:8080 to verify stream
4. **Update .env** if IP address changed
5. **Restart server** with `Ctrl + C` then rerun uvicorn command

### Server Won't Start?

```powershell
# Kill any stuck processes
Get-Process -Name uvicorn | Stop-Process -Force

# Then restart
cd c:\Users\Reyha\Downloads\rrrrrrrrrrrrrrrr
uvicorn app.backend.main:app --reload
```

### Port 8000 Already in Use?

```powershell
uvicorn app.backend.main:app --reload --port 8001
```
Then access via http://localhost:8001

---

## 🎯 Quick Test

1. **Start server** (if not running)
2. **Open** http://localhost:8000/monitor
3. **Hold phone** in front of IP Webcam
4. **Wait 30 seconds** in same position
5. **Alert triggers** - red border, bounding box appears!

---

## 📋 Project Files

```
c:\Users\Reyha\Downloads\rrrrrrrrrrrrrrrr\
├── .env                    # Camera & config settings
├── requirements.txt        # Python dependencies
├── app/
│   ├── backend/
│   │   ├── main.py        # FastAPI server
│   │   ├── camera.py      # Video streaming
│   │   ├── detection.py   # YOLOv8n AI
│   │   └── db.py          # Database
│   └── frontend/
│       ├── index.html     # Dashboard
│       ├── setup.html     # Grid setup
│       └── monitor.html   # Live monitor
```

---

## ⚡ Pro Tips

- Server auto-reloads when you edit Python files or `.env`
- Keep IP Webcam app in foreground on your phone
- Use Grid Setup to define screen area for zone-based tracking
- Alerts are shown in real-time via WebSocket
- **Supabase database is required** - ensure SUPABASE_URL and SUPABASE_KEY are set in `.env`

---

**Need help?** All features are working! Just navigate to the URLs above. 🚀
