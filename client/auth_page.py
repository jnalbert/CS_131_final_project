import cv2
from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QLabel, QPushButton, QScrollArea
from PySide6.QtGui import QImage, QPixmap
from .camera_manager import get_camera

class AuthPage(QWidget):
    def __init__(self, main_window, page_title="Auth"):
        super().__init__()
        self.main_window = main_window
        self.setWindowTitle(page_title)
        self.setFixedSize(700, 450)
        self.page_title = page_title
        self.frame = None

        self.capturing = True  # Flag to track if video is running

        # Create Scroll Area
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)

        # Create Content Widget (This holds all UI elements)
        self.content_widget = QWidget()
        self.setup_ui()

        # Set the content widget inside the scroll area
        scroll_area.setWidget(self.content_widget)

        # Layout for this page (only contains scroll area)
        layout = QVBoxLayout(self)
        layout.addWidget(scroll_area)
        self.setLayout(layout)

        # Use the shared camera instance instead of creating a new one
        self.capture = get_camera()
        if not self.capture.isOpened():
            self.video_label.setText("Unable to access camera.")
            print("Camera failed to open in", page_title)
        else:
            print("Camera successfully opened in", page_title)
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.update_frame)
            self.timer.start(30)

    def setup_ui(self):
        content_layout = QVBoxLayout()
        content_layout.setSpacing(15)
        content_layout.setContentsMargins(10, 10, 10, 10)  # Add some margins

        # Add error message label at the very top with extra spacing
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: red; font-weight: bold; font-size: 16px; background-color: #FFEEEE; padding: 8px; border: 1px solid red; border-radius: 4px; margin: 5px;")
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.setFixedHeight(40)  # Ensure it has enough height to be visible
        self.error_label.setVisible(False)  # Initially hidden
        content_layout.addWidget(self.error_label)
        
        # Add a little spacing after the error message
        content_layout.addSpacing(10)

        username_label = QLabel("Username:")
        username_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        content_layout.addWidget(username_label)

        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Enter your username")
        content_layout.addWidget(self.username_edit)

        self.video_label = QLabel("Camera feed will appear here")
        self.video_label.setFixedSize(480, 320)
        self.video_label.setStyleSheet("background-color: black;")
        self.video_label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(self.video_label)

        self.capture_button = QPushButton("Capture Image")
        self.capture_button.clicked.connect(self.capture_image)
        content_layout.addWidget(self.capture_button)
        
        # Add restart button (initially disabled)
        self.restart_button = QPushButton("Retake Image")
        self.restart_button.clicked.connect(self.reset_capture)
        self.restart_button.setEnabled(False)
        content_layout.addWidget(self.restart_button)
        
        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.submit_image)
        content_layout.addWidget(self.submit_button)

        self.content_widget.setLayout(content_layout)
  
    def capture_frame(self, frame):
        self.frame = frame
        local_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = local_frame.shape
        bytes_per_line = ch * w
        q_image = QImage(local_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        self.video_label.setPixmap(pixmap.scaled(
                self.video_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            ))

    def update_frame(self):
        if not self.capturing:
            return

        ret, frame = self.capture.read()
        if ret:
            self.capture_frame(frame)
        else:
            print(f"Failed to capture frame in {self.page_title}")

    def capture_image(self):
        self.hide_error()
        ret, frame = self.capture.read()
        if ret:
            self.capturing = False  # Stop updating the video
            self.capture_frame(frame)
            print(f"Image captured: frame shape = {self.frame.shape if self.frame is not None else 'None'}")

            # Disable capture button, enable restart button
            self.capture_button.setEnabled(False)
            self.restart_button.setEnabled(True)
        else:
            print(f"Failed to capture image in {self.page_title}")
            self.show_error("ERROR: Failed to capture image. Check your camera.")
            
    def reset_capture(self):
        """Reset the camera capture to allow taking a new image"""
        self.capturing = True
        self.capture_button.setEnabled(True)
        self.restart_button.setEnabled(False)
        self.submit_button.setEnabled(True)
        
    def show_error(self, message):
        """Display an error message in red at the top of the page"""
        print(f"SHOW_ERROR CALLED: {message}")
        self.error_label.setText(message)
        self.error_label.setVisible(True)
        # Make sure the error is brought to the front
        self.error_label.raise_()
        # Keep the error visible for at least 5 seconds
        if hasattr(self, 'error_timer') and self.error_timer.isActive():
            self.error_timer.stop()
        self.error_timer = QTimer(self)
        self.error_timer.timeout.connect(lambda: None)  # Do nothing on timeout, keep visible
        self.error_timer.start(5000)
        
    def hide_error(self):
        self.error_label.setVisible(False)
        
    def submit_image(self):
        # TODO: Implement this in the sub class
        pass

    def closeEvent(self, event):
        """ Cleanup when the window is closed. """
        if hasattr(self, 'timer'):
            self.timer.stop()
        # Don't release the camera here anymore - it's managed by camera_manager
        event.accept()