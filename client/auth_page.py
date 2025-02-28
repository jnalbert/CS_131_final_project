import cv2
from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QLabel, QPushButton, QScrollArea
from PySide6.QtGui import QImage, QPixmap

class AuthPage(QWidget):
    def __init__(self, main_window, page_title="Auth"):
        super().__init__()
        self.main_window = main_window
        self.setWindowTitle(page_title)
        self.setFixedSize(500, 450)
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

        # Initialize camera
        self.capture = cv2.VideoCapture(0)
        if not self.capture.isOpened():
            self.video_label.setText("Unable to access camera.")
        else:
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.update_frame)
            self.timer.start(30)

    def setup_ui(self):
        content_layout = QVBoxLayout()
        content_layout.setSpacing(15)

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

    def capture_image(self):
        ret, frame = self.capture.read()
        if ret:
            self.capturing = False  # Stop updating the video
            self.capture_frame(frame)

            # Disable capture button, enable restart button
            self.capture_button.setEnabled(False)
            self.restart_button.setEnabled(True)

        
    def submit_image(self):
        # TODO: Implement this in the sub class
        pass

    def closeEvent(self, event):
        """ Cleanup when the window is closed. """
        if hasattr(self, 'timer'):
            self.timer.stop()
        if hasattr(self, 'capture'):
            self.capture.release()
        event.accept()