import cv2

class MainWindow:
    def __init__(self):
        # ... existing code ...
        
        # Initialize camera at the application level
        self.capture = cv2.VideoCapture(0)
        if not self.capture.isOpened():
            print("ERROR: Failed to open camera")
        
    def go_to_login(self):
        # Pass the camera to login page
        self.login_page = LoginPage(self, capture=self.capture)
        # ... rest of your code ...
        
    def go_to_signup(self):
        # Pass the camera to signup page
        self.signup_page = SignupPage(self, capture=self.capture)
        # ... rest of your code ...
        
    def closeEvent(self, event):
        # Release camera when application closes
        if hasattr(self, 'capture'):
            self.capture.release()
        event.accept() 