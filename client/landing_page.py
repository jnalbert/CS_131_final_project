# ui/landing_page.py
from PySide6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout
from PySide6.QtCore import Qt

class LandingPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setup_ui()

    def setup_ui(self):
        self.setStyleSheet("background-color: #00008B;")
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        title_label = QLabel("Welcome to Your Password Manager")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        login_button = QPushButton("Login")
        login_button.setFixedHeight(40)
        login_button.setStyleSheet("background-color: red; color: white;")
        login_button.clicked.connect(self.on_login_clicked)
        
        signup_button = QPushButton("Sign Up")  
        signup_button.setFixedHeight(40)
        signup_button.setStyleSheet("background-color: red; color: white;")
        signup_button.clicked.connect(self.on_signup_clicked)
        
        layout.addWidget(title_label)
        layout.addStretch()
        layout.addWidget(login_button)
        layout.addWidget(signup_button)
        layout.addStretch()
        
        self.setLayout(layout)

    def on_login_clicked(self):
        self.main_window.go_to_login()

    def on_signup_clicked(self):
        self.main_window.go_to_signup()
