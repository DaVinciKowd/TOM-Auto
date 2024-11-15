import cv2
import mediapipe as mp

# Initialize MediaPipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# Initialize OpenCV VideoCapture
cap = cv2.VideoCapture(0)

# Set up drawing utilities for OpenCV
mp_drawing = mp.solutions.drawing_utils

# Define the eye landmarks (for left and right eyes)
left_eye_ids = [159, 23, 130, 243, 33, 7]  # Example landmarks for the left eye
right_eye_ids = [386, 374, 263, 362, 466, 359]  # Example landmarks for the right eye

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Flip the frame horizontally for a later mirror effect
    frame = cv2.flip(frame, 1)

    # Convert the frame to RGB (MediaPipe uses RGB images)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process the frame to get the landmarks
    results = face_mesh.process(rgb_frame)

    # Draw the landmarks on the frame (display IDs only)
    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            # Draw the landmarks for the left and right eyes with their ID numbers
            for eye_id in left_eye_ids:
                eye_landmark = face_landmarks.landmark[eye_id]
                eye_x = int(eye_landmark.x * frame.shape[1])
                eye_y = int(eye_landmark.y * frame.shape[0])
                cv2.circle(frame, (eye_x, eye_y), 2, (0, 255, 0), -1)  # Green circles for the left eye landmarks
                
                # Display the ID next to the landmark in green
                cv2.putText(frame, str(eye_id), (eye_x + 5, eye_y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

            for eye_id in right_eye_ids:
                eye_landmark = face_landmarks.landmark[eye_id]
                eye_x = int(eye_landmark.x * frame.shape[1])
                eye_y = int(eye_landmark.y * frame.shape[0])
                cv2.circle(frame, (eye_x, eye_y), 2, (0, 255, 0), -1)  # Green circles for the right eye landmarks
                
                # Display the ID next to the landmark in green
                cv2.putText(frame, str(eye_id), (eye_x + 5, eye_y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

    # Display the image
    cv2.imshow('Eye Landmarks with IDs', frame)

    # Exit the loop if the user presses 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture object and close any OpenCV windows
cap.release()
cv2.destroyAllWindows()
