from PySide6.QtCore import QTimer

from hands.hand_tracker import process_image_with_frame
from .auth_page import AuthPage
from db.handle_db import retrieve_password

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
        
        password = retrieve_password(username)
        
        if (not password):
            print("No password found for user")
            return
        password = password[0]
        
        password_hash = process_image_with_frame(self.frame, username)
        
        if (password_hash['gesture_hash'] == password):
            print('saved pass', password)
            print('input pass', password_hash['gesture_hash'])
            print("Password is correct")
            self.finish_signup(username)
        else:
            print('saved pass', password)
            print('input pass', password_hash['gesture_hash'])
            print("Password is incorrect")

    def finish_signup(self, username):
        print(f"Finished processing sign up for: {username}")
        # For demonstration, simulate a successful signup by passing dummy data.
        self.main_window.go_to_passwords(username)