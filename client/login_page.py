from PySide6.QtCore import QTimer
from .auth_page import AuthPage

class LoginPage(AuthPage):
    def __init__(self, main_window):
        super().__init__(main_window, page_title="Login")

    def submit_image(self):
        username = self.username_edit.text().strip()
        if not username:
            print("Please enter a username.")
            return

        # Disable the submit button to prevent duplicate submissions
        self.submit_button.setEnabled(False)
        print(f"Starting login processing for: {username}")

        # Simulate time-consuming login processing (e.g., checking credentials)
        QTimer.singleShot(2000, lambda: self.finish_login(username))

    def finish_login(self, username):
        print(f"Finished processing login for: {username}")
        # For demonstration, we simulate a successful login by passing dummy data.
        self.main_window.go_to_passwords(username)