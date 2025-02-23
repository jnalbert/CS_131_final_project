from PySide6.QtCore import QTimer
from .auth_page import AuthPage

class SignupPage(AuthPage):
    def __init__(self, main_window):
        super().__init__(main_window, page_title="Sign Up")

    def submit_image(self):
        username = self.username_edit.text().strip()
        if not username:
            print("Please enter a username.")
            return

        self.submit_button.setEnabled(False)
        print(f"Starting sign up processing for: {username}")

        # Simulate time-consuming sign-up processing (e.g., registering the user)
        QTimer.singleShot(2000, lambda: self.finish_signup(username))

    def finish_signup(self, username):
        print(f"Finished processing sign up for: {username}")
        # For demonstration, simulate a successful signup by passing dummy data.
        self.main_window.go_to_passwords(username)