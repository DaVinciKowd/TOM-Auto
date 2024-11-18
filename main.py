import cv2
import cvzone
import winsound
import time
import threading
import mediapipe as mp
import numpy as np
from cvzone.FaceMeshModule import FaceMeshDetector
from cvzone.PlotModule import LivePlot

def play_beep():
    winsound.Beep(1000, 500)
    print("Beep Initiated")

cap = cv2.VideoCapture(0)
detector = FaceMeshDetector(maxFaces=1)
plotY = LivePlot(640, 360, [20, 50], invert=True)

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Eye landmarks for left and right eyes
leftEyeIDs = [159, 23, 130, 243]
rightEyeIDs = [386, 374, 263, 362]
ratioList = []
eye_closed_threshold = 30

left_eye_state = "Open"
right_eye_state = "Open"
color = (0, 255, 0)

# Counter for closed eyes
last_time = time.time()
closed_counter = 0
eye_closed_reset = False

while True:
    success, img = cap.read()
    if not success:
        break

    img, faces = detector.findFaceMesh(img, draw=False)
    image_h, image_w, _ = img.shape

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(img_rgb)

    if faces:
        face = faces[0]

        def calculate_ear(eyeIDs):
            upper = face[eyeIDs[0]]
            lower = face[eyeIDs[1]]
            left = face[eyeIDs[2]]
            right = face[eyeIDs[3]]

            verLength, _ = detector.findDistance(upper, lower)
            horLength, _ = detector.findDistance(left, right)
            ratio = int((verLength / horLength) * 100)
            return ratio, upper, lower, left, right

        left_ratio, left_up, left_down, left_left, left_right = calculate_ear(leftEyeIDs)
        right_ratio, right_up, right_down, right_left, right_right = calculate_ear(rightEyeIDs)
        average_ratio = (left_ratio + right_ratio) // 2
        ratioList.append(average_ratio)

        if len(ratioList) > 3:
            ratioList.pop(0)
        ratioAverage = sum(ratioList) / len(ratioList)

        # Check eye state
        if left_ratio < eye_closed_threshold:
            left_eye_state = "Closed"
            colorLeft = (0, 0, 255)
        else:
            left_eye_state = "Open"
            colorLeft = (0, 255, 0)

        if right_ratio < eye_closed_threshold:
            right_eye_state = "Closed"
            colorRight = (0, 0, 255)
        else:
            right_eye_state = "Open"
            colorRight = (0, 255, 0)

        if left_eye_state == "Closed" or right_eye_state == "Closed":
            if not eye_closed_reset:
                print("Eyes are now closed")
                eye_closed_reset = True
            elif time.time() - last_time >= 1:
                closed_counter += 1
                last_time = time.time()
                if closed_counter >= 10:
                    threading.Thread(target=play_beep).start()
        else:
            if eye_closed_reset:
                print("Eyes are now open")
                eye_closed_reset = False
                closed_counter = 0

       
        marker_size = 2
        for (up, down, left, right) in [(left_up, left_down, left_left, left_right),
                                        (right_up, right_down, right_left, right_right)]:
            cv2.circle(img, up, marker_size, color, cv2.FILLED)
            cv2.circle(img, down, marker_size, color, cv2.FILLED)
            cv2.circle(img, left, marker_size, color, cv2.FILLED)
            cv2.circle(img, right, marker_size, color, cv2.FILLED)
            cv2.line(img, up, down, (0, 200, 0), 2)
            cv2.line(img, left, right, (0, 200, 0), 2)

        cvzone.putTextRect(img, f'Left Eye: {left_eye_state}', (20, 50), colorR=colorLeft)
        cvzone.putTextRect(img, f'Right Eye: {right_eye_state}', (20, 100), colorR=colorRight)
        cvzone.putTextRect(img, f'Time: {closed_counter}', (50, 150), colorR=(255, 255, 0))


    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            face_2D = []
            face_3D = []

            for idx in [33, 263, 1, 61, 199]:
                x, y = int(face_landmarks.landmark[idx].x * image_w), int(face_landmarks.landmark[idx].y * image_h)
                z = face_landmarks.landmark[idx].z
                face_2D.append([x, y])
                face_3D.append([x, y, z])

            face_2D = np.array(face_2D, dtype=np.float64)
            face_3D = np.array(face_3D, dtype=np.float64)

            focal_length = 1 * image_w
            cam_matrix = np.array([[focal_length, 0, image_w / 2],
                                [0, focal_length, image_h / 2],
                                [0, 0, 1]])
            dist_matrix = np.zeros((4, 1), dtype=np.float64)

            success, rot_vec, trans_vec = cv2.solvePnP(face_3D, face_2D, cam_matrix, dist_matrix)
            rmat, _ = cv2.Rodrigues(rot_vec)
            angles, _, _, _, _, _ = cv2.RQDecomp3x3(rmat)
            x_angle, y_angle, z_angle = angles[0] * 360, angles[1] * 360, angles[2] * 360


            if y_angle < -10:
                text = "Looking Left"
                print("Looking Left    ", end="\r")

            elif y_angle > 10:
                text = "Looking Right"
                print("Looking Right   ", end="\r")

            else:
                text = "Looking Forward"
                print("Looking Forward", end="\r")

            cv2.putText(img, text, (20, 200), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)

            # Draw a line to indicate head pose direction
            nose_3D = (face_landmarks.landmark[1].x * image_w, face_landmarks.landmark[1].y * image_h, face_landmarks.landmark[1].z)
            nose_2D = (int(nose_3D[0]), int(nose_3D[1]))

            # Adjust line length and downward factor for left-right direction
            line_length_factor = 8  # The scaling factor for the line length
            p1 = nose_2D
            p2 = (int(nose_3D[0] + y_angle * line_length_factor), int(nose_3D[1]))

            cv2.line(img, p1, p2, (255, 0, 0), 3)


    # Show the final output
    imgPlot = plotY.update(ratioAverage, color)
    img = cv2.resize(img, (640, 360))
    imgStack = cvzone.stackImages([img, imgPlot], 1, 2)

    cv2.imshow("Eye and Head Pose Detection", imgStack)

    if cv2.waitKey(25) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
