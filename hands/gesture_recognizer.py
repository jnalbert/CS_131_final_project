import cv2
import mediapipe as mp

# Initialize MediaPipe Gesture Recognizer
BaseOptions = mp.tasks.BaseOptions
GestureRecognizer = mp.tasks.vision.GestureRecognizer
GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

# Callback function for processing results
def print_recognition_result(result, unused_output_image, timestamp_ms):
    if result.gestures:
        detected_gesture = result.gestures[0][0].category_name  # Get top gesture
        print(f"Detected Gesture: {detected_gesture}")

# Load Gesture Recognizer model
options = GestureRecognizerOptions(
    base_options=BaseOptions(model_asset_path="gesture_recognizer.task"),
    running_mode=VisionRunningMode.LIVE_STREAM,
    result_callback=print_recognition_result,
)

# Start Webcam
cap = cv2.VideoCapture(0)
timestamp = 0

with GestureRecognizer.create_from_options(options) as recognizer:
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            print("Ignoring empty frame.")
            continue

        # Convert frame to RGB (MediaPipe expects RGB format)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process frame
        timestamp += 33  # Get timestamp
        recognizer.recognize_async(mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame), timestamp)

        # Display camera feed
        cv2.imshow("Gesture Recognition", frame)

        # Capture a recognized gesture when 'c' is pressed
        if cv2.waitKey(1) & 0xFF == ord("c"):
            print("Captured Gesture!")

        # Exit on 'q' key
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

# Cleanup
cap.release()
cv2.destroyAllWindows()