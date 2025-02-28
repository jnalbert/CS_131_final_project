import cv2
import mediapipe as mp
import numpy as np
import json
import os
from gesture_conversions import get_gesture_hash

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

    fingers = [thumb_extended, index_extended, middle_extended, ring_extended, pinky_extended]
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
    with open(filename, 'w') as f:
        json.dump(gestures, f)
    print(f"Gestures saved to {filename}")

def load_gestures(filename="saved_gestures.json"):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return json.load(f)
    return {}

def main():
    cap = cv2.VideoCapture(0)
    
    # Dictionary to store registered gesture hashes
    registered_gestures = load_gestures()
    current_mode = "recognition"  # Modes: "recognition", "registration"
    current_user = "user1"  # Default user
    
    # Dynamic calibration data
    last_gestures = []  # Store the last few gesture hashes for the same gesture
    calibration_gesture = None  # Current gesture being calibrated
    
    print(f"Loaded {len(registered_gestures)} gestures")
    
    # Optionally flip the frame to act like a mirror.
    with mp_hands.Hands(max_num_hands=1, 
                       min_detection_confidence=0.7, 
                       min_tracking_confidence=0.7) as hands:
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                print("Ignoring empty frame.")
                continue

            frame = cv2.flip(frame, 1)  # Mirror image for user-friendliness
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb_frame)

            gesture = "No Hand Detected"
            gesture_hash = None
            matched_gesture = None

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    # Draw hand landmarks on the frame
                    mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                    
                    # Get landmarks
                    landmarks = hand_landmarks.landmark
                    
                    # Classify the gesture using the original method
                    gesture = classify_gesture(landmarks)
                    
                    # Generate hash for the current gesture
                    gesture_hash = get_gesture_hash(landmarks, salt=current_user)
                    
                    # Check if the hash exactly matches any registered gestures
                    matched_gesture = None
                    for name, registered_hash in registered_gestures.items():
                        if gesture_hash == registered_hash:
                            matched_gesture = name
                            break
                    
                    # Display information on the frame
                    cv2.putText(frame, f"Gesture: {gesture}", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 
                                0.8, (0, 255, 0), 2, cv2.LINE_AA)
                    
                    if matched_gesture:
                        cv2.putText(frame, f"Matched: {matched_gesture}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 
                                   0.8, (0, 255, 0), 2, cv2.LINE_AA)
                    
                    # Show hash for reference
                    short_hash = gesture_hash if gesture_hash else "None"
                    cv2.putText(frame, f"Hash: {short_hash}", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 
                               0.8, (0, 255, 0), 2, cv2.LINE_AA)
                    
                    # Store last gesture hash in calibration mode
                    if current_mode == "calibration" and calibration_gesture:
                        cv2.putText(frame, f"Calibrating: {calibration_gesture} ({len(last_gestures)}/5)", 
                                  (10, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2, cv2.LINE_AA)

            # Display mode and instructions
            mode_color = (0, 255, 255) if current_mode == "registration" else (255, 255, 255)
            mode_color = (0, 165, 255) if current_mode == "calibration" else mode_color
            
            cv2.putText(frame, f"Mode: {current_mode}", (10, frame.shape[0] - 100), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, mode_color, 2, cv2.LINE_AA)
            
            cv2.putText(frame, "R: Register | V: Verify | C: Calibrate | S: Save", 
                       (10, frame.shape[0] - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)
            cv2.putText(frame, "L: Load gestures | Q: Quit", (10, frame.shape[0] - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)

            cv2.imshow("Gesture Recognition", frame)

            key = cv2.waitKey(1) & 0xFF
            
            if key == ord("r"):
                # Switch to registration mode
                current_mode = "registration"
                print("Registration mode: Create a gesture and press 'S' to save")
                
            elif key == ord("v"):
                # Switch to verification mode
                current_mode = "recognition"
                print("Verification mode: Make a gesture to check matches")
                
            elif key == ord("c"):
                # Switch to calibration mode
                current_mode = "calibration"
                last_gestures = []
                calibration_gesture = input("Enter gesture name to calibrate: ")
                print(f"Calibrating gesture '{calibration_gesture}'. Hold the gesture and press Space 5 times.")
                
            elif key == 32 and current_mode == "calibration" and gesture_hash and calibration_gesture:
                # Space bar pressed during calibration - capture current gesture
                last_gestures.append(gesture_hash)
                print(f"Captured sample {len(last_gestures)}/5 for {calibration_gesture}")
                
                if len(last_gestures) >= 5:
                    # Use the most common hash as the registered one
                    from collections import Counter
                    most_common_hash = Counter(last_gestures).most_common(1)[0][0]
                    registered_gestures[calibration_gesture] = most_common_hash
                    print(f"Calibration complete: Registered '{calibration_gesture}' with hash: {most_common_hash}")
                    current_mode = "recognition"
                    last_gestures = []
                    calibration_gesture = None
                
            elif key == ord("s") and current_mode == "registration" and gesture_hash:
                # Save the current gesture hash with a name
                gesture_name = input("Enter a name for this gesture: ")
                if gesture_name:
                    registered_gestures[gesture_name] = gesture_hash
                    print(f"Gesture '{gesture_name}' registered with hash: {gesture_hash}")
                    save_gestures(registered_gestures)
                    
            elif key == ord("l"):
                # Load gestures from file
                registered_gestures = load_gestures()
                print(f"Loaded {len(registered_gestures)} gestures")
                
            elif key == ord("q"):
                # Save gestures before quitting
                save_gestures(registered_gestures)
                break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()