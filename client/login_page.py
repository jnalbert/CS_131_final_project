from PySide6.QtCore import QTimer

from hands.hand_tracker import process_image_with_frame
from .auth_page import AuthPage
from db.handle_db import insert_user, get_user

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
        
        user = get_user(username)
        if user:
            print(user)
            print(f"User {username} already exists.")
            return
        
        password_hash = process_image_with_frame(self.frame, username)
        
        print(username, password_hash['gesture_hash'])

        insert_user(username, password_hash['gesture_hash'])
        self.finish_login(username)

        # QTimer.singleShot(2000, lambda: self.finish_login(username))

    def finish_login(self, username):
        print(f"Finished processing login for: {username}")
        # For demonstration, we simulate a successful login by passing dummy data.
        self.main_window.go_to_passwords(username)

