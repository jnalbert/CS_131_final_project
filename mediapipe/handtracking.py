import cv2
import mediapipe as mp
import numpy as np

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils


## REPLACE WITH JETSON NANO CAMERA or maybe this works idk
cap = cv2.VideoCapture(0)


def normalize_landmarks(landmarks):
    """Convert absolute hand landmarks into relative distances to minimize ambiguity."""
    if not landmarks or len(landmarks) < 21:  # Ensure we have all 21 landmarks
        return np.zeros(63)  # Return a zero array if data is missing

    base_x, base_y, base_z = landmarks[0]  # Use wrist as reference
    normalized = []

    for lm in landmarks:
        norm_x = lm[0] - base_x
        norm_y = lm[1] - base_y
        norm_z = lm[2] - base_z
        normalized.append([norm_x, norm_y, norm_z])

    return np.array(normalized, dtype=np.float32).flatten() # Flatten to a 1D array

with mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.8, min_tracking_confidence=0.8) as hands:
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            print("Ignoring empty frame.")
            continue

        # invert camera
        #frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)

        hand_data = []
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                for idx, hand_landmark in enumerate(hand_landmarks.landmark):
                    hand_data.append({
                        'x': hand_landmark.x,
                        'y': hand_landmark.y,
                        'z': hand_landmark.z,
                    })
                    h, w, _ = frame.shape
                    cx, cy = int(hand_landmark.x * w), int(hand_landmark.y * h)
                    cv2.putText(frame, f'{idx}', (cx, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)

                #normalized_data = normalize_landmarks(hand_data)

        cv2.imshow('MediaPipe Hands', frame)

        if cv2.waitKey(5) & 0xFF == ord('c'):
            if hand_data:
                print("Normalized landmarks:")
                #print(normalized_data)


        if cv2.waitKey(5) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()