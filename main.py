import cv2
import cvzone
import winsound
import time
from cvzone.FaceMeshModule import FaceMeshDetector
from cvzone.PlotModule import LivePlot
# from inputTimer import elapsedTime

cap = cv2.VideoCapture(0)
detector = FaceMeshDetector(maxFaces=1)
plotY = LivePlot(640, 360, [20, 50], invert=True)

leftEyeIDs = [159, 23, 130, 243]  
rightEyeIDs = [386, 374, 263, 362]
ratioList = []
consec_frames = 400

eye_closed_threshold = 30
left_eye_state = "Open"
right_eye_state = "Open"
color = (0, 255, 0)

# Counter for closed eyes
closed_counter = 0
eye_closed_reset = False

while True:
    if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    success, img = cap.read()
    if not success:
        break

    img, faces = detector.findFaceMesh(img, draw=False)

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

        if left_ratio < eye_closed_threshold:
            left_eye_state = "Closed"
        else:
            left_eye_state = "Open"

        if right_ratio < eye_closed_threshold:
            right_eye_state = "Closed"
        else:
            right_eye_state = "Open"

        if left_eye_state == "Closed" or right_eye_state == "Closed":
            closed_counter += 1
            eye_closed_reset = False
        elif not eye_closed_reset:
            eye_closed_reset = True
            closed_counter = 0

        if left_eye_state == "Closed" or right_eye_state == "Closed":
            color = (0, 0, 255)
        else:
            color = (0, 255, 0)


        marker_size = 2
        for (up, down, left, right) in [(left_up, left_down, left_left, left_right),
                                        (right_up, right_down, right_left, right_right)]:
            cv2.circle(img, up, marker_size, color, cv2.FILLED)
            cv2.circle(img, down, marker_size, color, cv2.FILLED)
            cv2.circle(img, left, marker_size, color, cv2.FILLED)
            cv2.circle(img, right, marker_size, color, cv2.FILLED)

            cv2.line(img, up, down, (0, 200, 0), 2)
            cv2.line(img, left, right, (0, 200, 0), 2)

        cvzone.putTextRect(img, f'Left Eye: {left_eye_state}', (50, 50), colorR=color)
        cvzone.putTextRect(img, f'Right Eye: {right_eye_state}', (50, 100), colorR=color)

        cvzone.putTextRect(img, f'Time: {closed_counter}', (50, 150), colorR=(255, 255, 0))

        imgPlot = plotY.update(ratioAverage, color)

        img = cv2.resize(img, (640, 360))
        imgStack = cvzone.stackImages([img, imgPlot], 1, 2)

        if left_ratio < eye_closed_threshold and right_ratio < eye_closed_threshold:
            if closed_counter >= consec_frames:
                winsound.Beep(1000, 1000)

        else:
            counter = 0
    else:
        img = cv2.resize(img, (640, 360))
        imgStack = cvzone.stackImages([img, img], 1, 2)

    cv2.imshow("Eye Open/Closed Detection", imgStack)


    if cv2.waitKey(25) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
