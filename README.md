# 👋 Gesture Authentication System

A biometric authentication system that uses hand gestures as passwords, providing a novel approach to secure access without traditional text-based passwords.

![Authentication Demo](https://via.placeholder.com/800x400?text=Gesture+Authentication+Demo)

## ✨ Features

- **Biometric Authentication**: Use hand gestures as a secure alternative to text passwords
- **Real-time Hand Tracking**: Track hand position and movements with MediaPipe and OpenCV
- **Gesture Recognition**: Identify and classify different hand poses and gestures
- **Secure Storage**: Encrypted gesture hash storage using SQLite
- **Cross-platform GUI**: Modern user interface built with PySide6
- **Multiple Authentication Modes**: Support for registration, verification, and calibration

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Webcam or camera device
- Required Python packages:
  - PySide6
  - OpenCV
  - MediaPipe
  - NumPy
  - SQLite3

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/gesture-auth-system.git
   cd gesture-auth-system
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python main.py
   ```

## 💻 Usage

### Registration
1. Click "Sign Up" on the landing page
2. Enter a username
3. Position your hand in front of the camera
4. Make a gesture you want to use as your password
5. Click "Capture Image" followed by "Submit"

### Login
1. Click "Login" on the landing page
2. Enter your username
3. Position your hand in front of the camera
4. Make the same gesture you registered with
5. Click "Capture Image" followed by "Submit"

### Gesture Calibration
For advanced users, the hand_tracker.py module provides additional calibration options:
- Press 'C' to enter calibration mode
- Enter the gesture name when prompted
- Make the gesture and press Space 5 times to capture samples
- The system will automatically select the most consistent hash

## 🛡️ Security Features

The system employs multiple security features:
- **Gesture Hash Generation**: Converts 3D hand landmark positions into stable hashes
- **Normalization**: Adjusts for differences in hand size and position
- **Feature Quantization**: Reduces sensitivity to small variations in gesture performance
- **Salt-based Hashing**: Associates gestures with specific usernames for additional security

## 🙏 Acknowledgments

- [MediaPipe](https://google.github.io/mediapipe/) for the hand tracking technology
- [PySide6](https://doc.qt.io/qtforpython-6/) for the GUI framework
- [OpenCV](https://opencv.org/) for computer vision capabilities