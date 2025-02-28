import cv2

# Singleton camera instance
_camera_instance = None

def get_camera():
    """Get a shared camera instance. Creates the camera if it doesn't exist yet."""
    global _camera_instance
    
    if _camera_instance is None or not _camera_instance.isOpened():
        try:
            # Try default device
            _camera_instance = cv2.VideoCapture(0)
            if not _camera_instance.isOpened():
                # Try specific device path as fallback
                _camera_instance = cv2.VideoCapture('/dev/video0')
        except Exception as e:
            print(f"Error initializing camera: {e}")
    
    return _camera_instance

def release_camera():
    """Release the camera when the application is closing."""
    global _camera_instance
    
    if _camera_instance is not None:
        _camera_instance.release()
        _camera_instance = None 