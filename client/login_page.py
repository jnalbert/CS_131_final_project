from PySide6.QtCore import QTimer

from hands.hand_tracker import process_image_with_frame
from .auth_page import AuthPage
from db.handle_db import retrieve_password

class LoginPage(AuthPage):
    def __init__(self, main_window):
        super().__init__(main_window, page_title="Login")

    def submit_image(self):
        username = self.username_edit.text().strip()
        if not username:
            self.show_error("ERROR: Please enter a username before continuing.")
            print("Showing error: Username empty")
            return

        # Check if frame exists using numpy array check
        if self.frame is None or not hasattr(self.frame, 'shape'):
            self.show_error("ERROR: Please capture your hand gesture first.")
            print("Showing error: No frame captured")
            self.submit_button.setEnabled(True)
            return

        self.submit_button.setEnabled(False)
        print(f"Starting sign up processing for: {username}")
        
        password = retrieve_password(username)
        
        # Check if password exists first
        if not password:
            self.show_error(f"ERROR: No password found for user '{username}'. Please check the username.")
            print(f"Showing error: No password for {username}")
            self.submit_button.setEnabled(True)
            return
            
        # Only access password[0] after checking it exists
        password = password[0]
        
        password_hash = process_image_with_frame(self.frame, username)
        
        if (password_hash['gesture_hash'] == password):
            print('saved pass', password)
            print('input pass', password_hash['gesture_hash'])
            print("Password is correct")
            self.finish_login(username)
        else:
            print('saved pass', password)
            print('input pass', password_hash['gesture_hash'])
            print("Showing error: Password incorrect")
            self.show_error("ERROR: Hand gesture doesn't match. Please try again.")
            self.reset_capture()

    def finish_login(self, username):
        print(f"Finished processing login for: {username}")
        # For demonstration, we simulate a successful login by passing dummy data.
        self.main_window.go_to_passwords(username)

