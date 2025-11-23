"""
Camera module for CinemaGuard
Handles video capture and MJPEG streaming
"""
import cv2
import os
from dotenv import load_dotenv
import threading
import time

load_dotenv()


class VideoCamera:
    """Video camera handler with MJPEG streaming support"""
    
    def __init__(self):
        self.camera_source = os.getenv("CAMERA_SOURCE", "0")
        
        # Convert to int if it's a webcam index
        try:
            self.camera_source = int(self.camera_source)
        except ValueError:
            pass  # It's an RTSP URL string
        
        self.video = None
        self.frame = None
        self.lock = threading.Lock()
        self.running = False
        
        self.connect()
    
    def connect(self):
        """Connect to camera source"""
        try:
            self.video = cv2.VideoCapture(self.camera_source)
            if self.video.isOpened():
                print(f"✓ Camera connected: {self.camera_source}")
                self.running = True
                # Start background thread for continuous frame capture
                threading.Thread(target=self._update_frame, daemon=True).start()
            else:
                print(f"✗ Failed to open camera: {self.camera_source}")
        except Exception as e:
            print(f"✗ Camera connection error: {e}")
    
    def _update_frame(self):
        """Background thread to continuously update frames"""
        while self.running:
            if self.video and self.video.isOpened():
                success, frame = self.video.read()
                if success:
                    with self.lock:
                        self.frame = frame
            time.sleep(0.03)  # ~30 FPS
    
    def get_frame(self):
        """Get the current frame"""
        with self.lock:
            if self.frame is not None:
                return self.frame.copy()
        return None
    
    def get_jpeg_frame(self):
        """Get current frame as JPEG bytes for MJPEG streaming"""
        frame = self.get_frame()
        if frame is None:
            # Return a black frame if no camera
            import numpy as np
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Encode frame to JPEG
        ret, jpeg = cv2.imencode('.jpg', frame)
        if ret:
            return jpeg.tobytes()
        return None
    
    def release(self):
        """Release camera resources"""
        self.running = False
        if self.video:
            self.video.release()
            print("✓ Camera released")


# Global camera instance
camera = VideoCamera()


def generate_mjpeg_stream():
    """Generator for MJPEG streaming"""
    while True:
        frame_bytes = camera.get_jpeg_frame()
        if frame_bytes:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        else:
            time.sleep(0.1)


def get_camera_instance():
    """Get the global camera instance"""
    return camera
