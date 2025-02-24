import cv2
import mediapipe as mp
import numpy as np

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

def main():
    cap = cv2.VideoCapture(0)
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

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    # Draw hand landmarks on the frame
                    mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                    # Classify the gesture based on landmark positions
                    gesture = classify_gesture(hand_landmarks.landmark)
                    # Display the gesture label on the frame
                    cv2.putText(frame, gesture, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 
                                1, (0, 255, 0), 2, cv2.LINE_AA)

            cv2.imshow("Gesture Recognition", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()