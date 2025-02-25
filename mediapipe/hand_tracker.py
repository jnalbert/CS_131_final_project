import cv2
import mediapipe as mp
import numpy as np
from gesture_conversions import normalize_landmarks, calculate_finger_angles, get_gesture_hash

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
    elif count == 1:
        return "Pointing"
    elif count == 2:
        return "Two Fingers"
    elif count == 3:
        return "Three Fingers"
    elif count == 4:
        return "Four Fingers"
    else:
        return "Unknown Gesture"

def calculate_gesture_similarity(hash1, hash2):
    """
    Calculate similarity between two gesture hashes.
    Returns a value between 0 (completely different) and 1 (identical).
    """
    # Convert hex hashes to binary arrays for comparison
    try:
        # Convert each hex character to a 4-bit binary value
        bin1 = ''.join([bin(int(c, 16))[2:].zfill(4) for c in hash1])
        bin2 = ''.join([bin(int(c, 16))[2:].zfill(4) for c in hash2])
        
        # Count matching bits
        matching_bits = sum(b1 == b2 for b1, b2 in zip(bin1, bin2))
        
        # Calculate similarity as percentage of matching bits
        similarity = matching_bits / len(bin1)
        return similarity
    except:
        # Fallback if hash conversion fails
        return 0.0

def main():
    cap = cv2.VideoCapture(0)
    # Dictionary to store registered gesture hashes
    registered_gestures = {}
    current_mode = "recognition"  # Modes: "recognition", "registration"
    current_user = "user1"  # Default user
    similarity_threshold = 0.85  # Threshold for gesture matching (adjustable)
    
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
            best_similarity = 0.0

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
                    
                    # Check for similar gestures using threshold
                    best_similarity = 0.0
                    matched_gesture = None
                    for name, hash_value in registered_gestures.items():
                        similarity = calculate_gesture_similarity(hash_value, gesture_hash)
                        if similarity > best_similarity:
                            best_similarity = similarity
                            if similarity >= similarity_threshold:
                                matched_gesture = name
                    
                    # Display information on the frame
                    cv2.putText(frame, f"Gesture: {gesture}", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 
                                0.8, (0, 255, 0), 2, cv2.LINE_AA)
                    
                    if matched_gesture:
                        cv2.putText(frame, f"Matched: {matched_gesture} ({best_similarity:.2f})", 
                                   (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 
                                   0.8, (0, 255, 0), 2, cv2.LINE_AA)
                    elif best_similarity > 0:
                        cv2.putText(frame, f"Best match: {best_similarity:.2f}", 
                                   (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 
                                   0.8, (255, 165, 0), 2, cv2.LINE_AA)
                    
                    # Show truncated hash for reference
                    short_hash = gesture_hash[:8] if gesture_hash else "None"
                    cv2.putText(frame, f"Hash: {short_hash}", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 
                               0.8, (0, 255, 0), 2, cv2.LINE_AA)

            # Display mode and instructions
            mode_color = (0, 255, 255) if current_mode == "registration" else (255, 255, 255)
            cv2.putText(frame, f"Mode: {current_mode}", (10, frame.shape[0] - 100), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, mode_color, 2, cv2.LINE_AA)
            cv2.putText(frame, f"Threshold: {similarity_threshold:.2f}", (10, frame.shape[0] - 70), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.putText(frame, "R: Register mode | V: Verify mode | S: Save gesture", 
                       (10, frame.shape[0] - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)
            cv2.putText(frame, "↑/↓: Adjust threshold | Q: Quit", (10, frame.shape[0] - 10), 
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
                
            elif key == ord("s") and current_mode == "registration" and gesture_hash:
                # Save the current gesture hash with a name
                gesture_name = input("Enter a name for this gesture: ")
                if gesture_name:
                    registered_gestures[gesture_name] = gesture_hash
                    print(f"Gesture '{gesture_name}' registered with hash: {gesture_hash}")
                    
            elif key == ord("q"):
                break
                
            elif key == ord("c") and gesture_hash:
                # Print the current gesture hash for debugging
                print(f"Current gesture hash: {gesture_hash}")
                print(f"Registered gestures: {registered_gestures}")
                
            elif key == 82 or key == ord("="): # Up arrow or '='
                # Increase threshold (make matching stricter)
                similarity_threshold = min(0.99, similarity_threshold + 0.01)
                print(f"Similarity threshold increased to: {similarity_threshold:.2f}")
                
            elif key == 84 or key == ord("-"): # Down arrow or '-'
                # Decrease threshold (make matching more lenient)
                similarity_threshold = max(0.50, similarity_threshold - 0.01)
                print(f"Similarity threshold decreased to: {similarity_threshold:.2f}")

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()