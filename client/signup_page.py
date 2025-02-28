from PySide6.QtCore import QTimer

from hands.hand_tracker import process_image_with_frame
from .auth_page import AuthPage
from db.handle_db import get_user, insert_user

class SignupPage(AuthPage):
    def __init__(self, main_window):
        super().__init__(main_window, page_title="Sign Up")
            
    def submit_image(self):
        username = self.username_edit.text().strip()
        if not username:
            self.show_error("ERROR: Please enter a username before continuing.")
            print("Showing error: Username empty")
            return

        # Disable the submit button to prevent duplicate submissions
        self.submit_button.setEnabled(False)
        print(f"Starting login processing for: {username}")
        
        user = get_user(username)
        if user:
            self.show_error(f"ERROR: User '{username}' already exists. Please use a different username.")
            print(f"Showing error: User {username} already exists")
            self.reset_capture()
            return
        
        # Check if frame exists using numpy array check
        if self.frame is None or not hasattr(self.frame, 'shape'):
            self.show_error("ERROR: Please capture your hand gesture first.")
            print("Showing error: No frame captured")
            self.submit_button.setEnabled(True)
            return
            
        password_hash = process_image_with_frame(self.frame, username)
        
        print(username, password_hash['gesture_hash'])

        insert_user(username, password_hash['gesture_hash'])
        self.finish_signup(username)

        # QTimer.singleShot(2000, lambda: self.finish_login(username))

    def finish_signup(self, username):
        print(f"Finished processing sign up for: {username}")
        # For demonstration, simulate a successful signup by passing dummy data.
        self.main_window.go_to_passwords(username)