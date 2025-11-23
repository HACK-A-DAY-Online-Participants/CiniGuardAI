"""
Detection module for CinemaGuard
Implements YOLOv8n phone detection with zone-based tracking
"""
import cv2
import time
from typing import Dict, List, Tuple, Optional
from collections import defaultdict
import os

# Import YOLO
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    print("⚠ Ultralytics not available. Detection disabled.")

from .db import save_alert


class PhoneDetector:
    """YOLOv8n-based phone detector with zone tracking"""
    
    # COCO dataset class ID for cell phone
    PHONE_CLASS_ID = 67
    
    # Risk thresholds
    STATIONARY_THRESHOLD = 30.0  # seconds
    HIGH_RISK_SCORE = 0.8
    
    def __init__(self, hall_name: str = "Cinema Hall 1"):
        self.hall_name = hall_name
        self.model = None
        self.grid_size = 10  # 10x10 grid
        
        # Track phone positions: {zone: first_seen_timestamp}
        self.zone_tracker: Dict[str, float] = {}
        
        # Store active alerts to prevent duplicates
        self.active_alerts: Dict[str, float] = {}
        
        # WebSocket connections for broadcasting alerts
        self.ws_connections = []
        
        if YOLO_AVAILABLE:
            try:
                # Load YOLOv8n model (will auto-download on first run)
                print("Loading YOLOv8n model...")
                self.model = YOLO('yolov8n.pt')
                print("✓ YOLOv8n model loaded successfully")
            except Exception as e:
                print(f"✗ Failed to load YOLO model: {e}")
    
    def register_websocket(self, ws):
        """Register a WebSocket connection for alerts"""
        self.ws_connections.append(ws)
    
    def unregister_websocket(self, ws):
        """Unregister a WebSocket connection"""
        if ws in self.ws_connections:
            self.ws_connections.remove(ws)
    
    def get_zone_from_bbox(self, bbox: Tuple[int, int, int, int], 
                          frame_width: int, frame_height: int) -> str:
        """
        Convert bounding box to grid zone (e.g., "3,5")
        bbox format: (x1, y1, x2, y2)
        """
        x1, y1, x2, y2 = bbox
        
        # Get center point of bounding box
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        
        # Calculate grid position
        grid_x = int((center_x / frame_width) * self.grid_size)
        grid_y = int((center_y / frame_height) * self.grid_size)
        
        # Clamp to grid boundaries
        grid_x = max(0, min(self.grid_size - 1, grid_x))
        grid_y = max(0, min(self.grid_size - 1, grid_y))
        
        return f"{grid_x},{grid_y}"
    
    async def detect_phones(self, frame) -> List[Dict]:
        """
        Detect phones in frame and return detections with risk assessment
        Returns: List of detection dicts with keys: bbox, confidence, zone, risk_score, duration
        """
        if self.model is None or frame is None:
            return []
        
        detections = []
        current_time = time.time()
        frame_height, frame_width = frame.shape[:2]
        
        # Run YOLO detection
        results = self.model(frame, verbose=False)
        
        # Track detected zones in this frame
        detected_zones = set()
        
        for result in results:
            boxes = result.boxes
            for box in boxes:
                # Check if detection is a phone
                class_id = int(box.cls[0])
                if class_id == self.PHONE_CLASS_ID:
                    confidence = float(box.conf[0])
                    
                    # Get bounding box
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    bbox = (x1, y1, x2, y2)
                    
                    # Determine grid zone
                    zone = self.get_zone_from_bbox(bbox, frame_width, frame_height)
                    detected_zones.add(zone)
                    
                    # Track zone duration
                    if zone not in self.zone_tracker:
                        self.zone_tracker[zone] = current_time
                    
                    duration = current_time - self.zone_tracker[zone]
                    
                    # Calculate risk score based on duration
                    risk_score = min(1.0, duration / self.STATIONARY_THRESHOLD)
                    
                    detection = {
                        'bbox': bbox,
                        'confidence': confidence,
                        'zone': zone,
                        'duration': duration,
                        'risk_score': risk_score
                    }
                    
                    detections.append(detection)
                    
                    # Check if we should trigger an alert
                    if duration >= self.STATIONARY_THRESHOLD:
                        # Only alert once per zone until it moves
                        if zone not in self.active_alerts:
                            await self._trigger_alert(zone, risk_score, bbox)
                            self.active_alerts[zone] = current_time
        
        # Clean up zones that are no longer detected
        zones_to_remove = set(self.zone_tracker.keys()) - detected_zones
        for zone in zones_to_remove:
            del self.zone_tracker[zone]
            if zone in self.active_alerts:
                del self.active_alerts[zone]
        
        return detections
    
    async def _trigger_alert(self, zone: str, risk_score: float, bbox: Tuple[int, int, int, int]):
        """Trigger an alert for a stationary phone"""
        print(f"🚨 ALERT: Phone detected in zone {zone} for >{self.STATIONARY_THRESHOLD}s (Risk: {risk_score:.2f})")
        
        # Save to database
        try:
            await save_alert(self.hall_name, risk_score, zone)
        except Exception as e:
            print(f"⚠ Failed to save alert to database: {e}")
        
        # Broadcast via WebSocket
        alert_data = {
            'type': 'alert',
            'zone': zone,
            'risk_score': risk_score,
            'bbox': bbox,
            'timestamp': time.time()
        }
        
        # Send to all connected WebSocket clients
        disconnected = []
        for ws in self.ws_connections:
            try:
                await ws.send_json(alert_data)
            except Exception as e:
                print(f"WebSocket send failed: {e}")
                disconnected.append(ws)
        
        # Remove disconnected clients
        for ws in disconnected:
            self.unregister_websocket(ws)
    
    def draw_detections(self, frame, detections: List[Dict]):
        """Draw bounding boxes and info on frame"""
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            risk_score = det['risk_score']
            
            # Color based on risk: green -> yellow -> red
            if risk_score < 0.5:
                color = (0, 255, 0)  # Green
            elif risk_score < self.HIGH_RISK_SCORE:
                color = (0, 255, 255)  # Yellow
            else:
                color = (0, 0, 255)  # Red
            
            # Draw bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            
            # Draw label
            label = f"Zone {det['zone']} | {det['duration']:.1f}s | Risk {risk_score:.2f}"
            cv2.putText(frame, label, (x1, y1 - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        return frame


# Global detector instance
detector = None


def get_detector(hall_name: str = None):
    """Get or create the global detector instance"""
    global detector
    if detector is None:
        detector = PhoneDetector(hall_name or os.getenv("HALL_NAME", "Cinema Hall 1"))
    return detector
