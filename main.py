# main.py
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from client.landing_page import LandingPage
from client.login_page import LoginPage
from client.signup_page import SignupPage
from client.passwords_page import PasswordsPage
from client.camera_manager import release_camera
from db.handle_db import init_db


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Password Manager")
        self.setFixedSize(700, 450)
        self.setStyleSheet("background-color: #0FFFF;")

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.landing_page = LandingPage(self)
        self.login_page = None  # Initialize when needed
        self.signup_page = None  # Initialize when needed

        self.stack.addWidget(self.landing_page)
        self.stack.setCurrentIndex(0)

    def go_to_login(self):
        # Create login page when needed
        if self.login_page is None:
            self.login_page = LoginPage(self)
            self.stack.addWidget(self.login_page)
        self.stack.setCurrentWidget(self.login_page)

    def go_to_signup(self):
        # Create signup page when needed
        if self.signup_page is None:
            self.signup_page = SignupPage(self)
            self.stack.addWidget(self.signup_page)
        self.stack.setCurrentWidget(self.signup_page)

    def go_to_landing(self):
        self.stack.setCurrentWidget(self.landing_page)

    def go_to_passwords(self, user_name):
        # Create a new PasswordsPage with the provided user_data and navigate to it
        self.passwords_page = PasswordsPage(self, user_name)
        self.stack.addWidget(self.passwords_page)
        self.stack.setCurrentWidget(self.passwords_page)


def main():
    init_db()
    app = QApplication(sys.argv)
    
    # Make sure to release the camera when the app closes
    app.aboutToQuit.connect(release_camera)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
