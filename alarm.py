import cv2
import mediapipe as mp
import numpy as np
import time
from scipy.spatial import distance
import winsound

def eye_aspect_ratio(eye):
    A = distance.euclidean(eye[1], eye[5])
    B = distance.euclidean(eye[2], eye[4])
    C = distance.euclidean(eye[0], eye[3])
    ear = (A + B) / (2.0 * C)
    return ear

eye_threshold = 0.2
consec_frames = 20
counter = 0

mp_face_detection = mp.solutions.face_detection
mp_face_mesh = mp.solutions.face_mesh

cap = cv2.VideoCapture(0)
with mp_face_detection.FaceDetection(min_detection_confidence=0.2) as face_detection, \
     mp_face_mesh.FaceMesh(min_detection_confidence=0.2, min_tracking_confidence=0.2) as face_mesh:

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_detection.process(frame_rgb)

        if results.detections:
            for detection in results.detections:
                bboxC = detection.location_data.relative_bounding_box
                ih, iw, _ = frame.shape
                x, y, w, h = int(bboxC.xmin * iw), int(bboxC.ymin * ih), int(bboxC.width * iw), int(bboxC.height * ih)
                face = frame[y:y+h, x:x+w]
                gray_face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)

                eyes = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml').detectMultiScale(gray_face)
                if len(eyes) >= 2:
                    left_eye, right_eye = eyes[0], eyes[1]
                    left_eye_points = np.array([[x + left_eye[0], y + left_eye[1]],
                                                [x + left_eye[0] + left_eye[2], y + left_eye[1]],
                                                [x + left_eye[0] + left_eye[2], y + left_eye[1] + left_eye[3]],
                                                [x + left_eye[0], y + left_eye[1] + left_eye[3]]])
                    right_eye_points = np.array([[x + right_eye[0], y + right_eye[1]],
                                                  [x + right_eye[0] + right_eye[2], y + right_eye[1]],
                                                  [x + right_eye[0] + right_eye[2], y + right_eye[1] + right_eye[3]],
                                                  [x + right_eye[0], y + right_eye[1] + right_eye[3]]])
                    left_ear = eye_aspect_ratio(left_eye_points)
                    right_ear = eye_aspect_ratio(right_eye_points)
                    ear = (left_ear + right_ear) / 2.0

                    if ear < eye_threshold:
                        counter += 1
                        if counter >= consec_frames:
                            winsound.Beep(1000, 1000)
                    else:
                        counter = 0

        cv2.imshow("Frame", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()