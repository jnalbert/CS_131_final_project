import cv2
import mediapipe as mp
import numpy as np
import json
import os
from .gesture_conversions import (
    get_gesture_hash,
)

# Initialize MediaPipe Hands and Drawing modules
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils


def classify_gesture(landmarks):
    """
    Classify the gesture based on the relative positions of hand landmarks.
    Uses a simple heuristic:
      - Thumb: considered extended if tip is to the left of the IP joint (for right hand).
      - Other fingers: considered extended if tip is above (smaller y) than the PIP joint.
    """
    # Thumb: landmarks[4] is the tip, landmarks[3] is the IP joint.
    thumb_extended = landmarks[4].x < landmarks[3].x

    # For fingers: if the tip is above the PIP joint, consider the finger extended.
    # Index finger: tip is landmarks[8], PIP is landmarks[6]
    index_extended = landmarks[8].y < landmarks[6].y
    # Middle finger: tip is landmarks[12], PIP is landmarks[10]
    middle_extended = landmarks[12].y < landmarks[10].y
    # Ring finger: tip is landmarks[16], PIP is landmarks[14]
    ring_extended = landmarks[16].y < landmarks[14].y
    # Pinky: tip is landmarks[20], PIP is landmarks[18]
    pinky_extended = landmarks[20].y < landmarks[18].y

    fingers = [
        thumb_extended,
        index_extended,
        middle_extended,
        ring_extended,
        pinky_extended,
    ]
    count = sum(fingers)

    # Classify gesture based on the number of extended fingers
    if count == 0:
        return "Fist"
    elif count == 5:
        return "Open Hand"
    elif count == 1 and index_extended:
        return "Pointing"
    elif count == 2 and index_extended and middle_extended:
        return "Peace Sign"
    elif count == 3:
        return "Three Fingers"
    elif count == 4:
        return "Four Fingers"
    else:
        return "Custom Gesture"


# Function to save and load gestures from a file
def save_gestures(gestures, filename="saved_gestures.json"):
    with open(filename, "w") as f:
        json.dump(gestures, f)
    print(f"Gestures saved to {filename}")


def load_gestures(filename="saved_gestures.json"):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return json.load(f)
    return {}


def process_image_with_frame(frame, user_name):
    # Load gestures
    registered_gestures = load_gestures()
    print(f"Loaded {len(registered_gestures)} gestures")

    # Initialize the hand detector
    with mp_hands.Hands(
        static_image_mode=True,  # Set to True for image processing
        max_num_hands=1,
        min_detection_confidence=0.7,
    ) as hands:
        # Mirror the image for more intuitive display
        frame = cv2.flip(frame, 1)

        # Convert to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process the image
        results = hands.process(rgb_frame)
        gesture_hash = None

        # Check if hand landmarks are detected
        if results.multi_hand_landmarks:
          for hand_landmarks in results.multi_hand_landmarks:
              # Draw hand landmarks on the frame
              mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

              landmarks = hand_landmarks.landmark

              # Generate hash for the current gesture
              gesture_hash = get_gesture_hash(landmarks, salt=user_name)
                    
   # Show hash for reference
    short_hash = gesture_hash if gesture_hash else "None"
    cv2.putText(
        frame,
        f"Hash: {short_hash}",
        (10, 100),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 0),
        2,
        cv2.LINE_AA,
    )
    
    return {
        "gesture_hash": gesture_hash,
    }


def process_image(image_path=None):
    # Load gestures
    registered_gestures = load_gestures()
    print(f"Loaded {len(registered_gestures)} gestures")

    # Initialize the hand detector
    with mp_hands.Hands(
        static_image_mode=True,  # Set to True for image processing
        max_num_hands=1,
        min_detection_confidence=0.7,
    ) as hands:

        # Capture image from camera if no path provided
        if image_path is None:
            cap = cv2.VideoCapture("/dev/video0")
            print("Press SPACE to capture an image...")

            while True:
                success, frame = cap.read()
                if not success:
                    print("Failed to capture image from camera.")
                    return

                # Display preview
                cv2.imshow("Press SPACE to capture", frame)
                key = cv2.waitKey(1) & 0xFF

                if key == 32:  # SPACE key
                    print("Image captured!")
                    cap.release()
                    cv2.destroyAllWindows()
                    break
                elif key == ord("q"):
                    print("Cancelled.")
                    cap.release()
                    cv2.destroyAllWindows()
                    return
        else:
            # Load image from file
            frame = cv2.imread(image_path)
            if frame is None:
                print(f"Failed to load image from {image_path}")
                return

        # Mirror the image for more intuitive display
        frame = cv2.flip(frame, 1)

        # Convert to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process the image
        results = hands.process(rgb_frame)

        gesture = "No Hand Detected"
        gesture_hash = None
        matched_gesture = None

        # Check if hand landmarks are detected
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw hand landmarks on the frame
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                # Get landmarks
                landmarks = hand_landmarks.landmark

                # Classify the gesture
                gesture = classify_gesture(landmarks)

                # Generate hash for the current gesture
                gesture_hash = get_gesture_hash(landmarks, salt="user1")

                # Check if the hash matches any registered gestures
                for name, registered_hash in registered_gestures.items():
                    if gesture_hash == registered_hash:
                        matched_gesture = name
                        break

        # Display results on the image
        cv2.putText(
            frame,
            f"Gesture: {gesture}",
            (10, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2,
            cv2.LINE_AA,
        )

        if matched_gesture:
            cv2.putText(
                frame,
                f"Matched: {matched_gesture}",
                (10, 70),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2,
                cv2.LINE_AA,
            )

        # Show hash for reference
        short_hash = gesture_hash if gesture_hash else "None"
        cv2.putText(
            frame,
            f"Hash: {short_hash}",
            (10, 100),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2,
            cv2.LINE_AA,
        )

        # Display instructions
        cv2.putText(
            frame,
            "S: Save as registered gesture | Q: Quit",
            (10, frame.shape[0] - 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            1,
            cv2.LINE_AA,
        )

        # Show the result
        cv2.imshow("Hand Gesture Analysis", frame)

        # Wait for user input
        while True:
            key = cv2.waitKey(0) & 0xFF

            if key == ord("s") and gesture_hash:
                # Save the current gesture
                gesture_name = input("Enter a name for this gesture: ")
                if gesture_name:
                    registered_gestures[gesture_name] = gesture_hash
                    save_gestures(registered_gestures)
                    print(
                        f"Gesture '{gesture_name}' registered with hash: {gesture_hash}"
                    )

            elif key == ord("q"):
                break

        cv2.destroyAllWindows()

        return {
            "gesture": gesture,
            "matched_gesture": matched_gesture,
            "gesture_hash": gesture_hash,
        }


def main():
    print("Hand Gesture Image Analyzer")
    print("1. Capture from camera")
    print("2. Load from file")

    choice = input("Enter your choice (1/2): ")

    if choice == "1":
        result = process_image()
    elif choice == "2":
        image_path = input("Enter the path to the image file: ")
        result = process_image(image_path)
    else:
        print("Invalid choice")
        return

    if result:
        print("\nAnalysis Results:")
        print(f"Detected Gesture: {result['gesture']}")
        if result["matched_gesture"]:
            print(f"Matched Registered Gesture: {result['matched_gesture']}")
        print(f"Gesture Hash: {result['gesture_hash']}")


if __name__ == "__main__":
    main()
