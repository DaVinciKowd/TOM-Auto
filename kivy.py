from kivy.app import App
from kivy.uix.image import Image
from kivy.graphics.texture import Texture
from kivy.clock import Clock
from kivy.uix.label import Label
import cv2
from cvzone.FaceMeshModule import FaceMeshDetector
import winsound

class EyeDetectionApp(App):
    def build(self):
        self.cap = cv2.VideoCapture(0)
        self.detector = FaceMeshDetector(maxFaces=1)
        
        # UI elements
        self.img_texture = Image()
        self.left_eye_state = Label(text="Left Eye: Open", size_hint=(0.5, 0.1), pos_hint={"top": 1, "right": 1})
        self.right_eye_state = Label(text="Right Eye: Open", size_hint=(0.5, 0.1), pos_hint={"top": 0.9, "right": 1})
        self.add_widget(self.img_texture)
        self.add_widget(self.left_eye_state)
        self.add_widget(self.right_eye_state)
        
        # Eye state and threshold settings
        self.left_eye_closed = False
        self.right_eye_closed = False
        self.eye_closed_threshold = 30
        self.closed_counter = 0
        self.consec_frames = 400

        Clock.schedule_interval(self.update, 1.0 / 30.0)
        return self.img_texture

    def update(self, dt):
        ret, img = self.cap.read()
        if not ret:
            return
        
        # Detect face mesh and calculate eye aspect ratio
        img, faces = self.detector.findFaceMesh(img, draw=False)
        if faces:
            face = faces[0]

            def calculate_ear(eyeIDs):
                upper = face[eyeIDs[0]]
                lower = face[eyeIDs[1]]
                left = face[eyeIDs[2]]
                right = face[eyeIDs[3]]
                verLength, _ = self.detector.findDistance(upper, lower)
                horLength, _ = self.detector.findDistance(left, right)
                return int((verLength / horLength) * 100)

            left_ratio = calculate_ear([159, 23, 130, 243])
            right_ratio = calculate_ear([386, 374, 263, 362])

            # Determine eye state
            if left_ratio < self.eye_closed_threshold:
                self.left_eye_closed = True
            else:
                self.left_eye_closed = False

            if right_ratio < self.eye_closed_threshold:
                self.right_eye_closed = True
            else:
                self.right_eye_closed = False

            # Update UI
            self.left_eye_state.text = "Left Eye: " + ("Closed" if self.left_eye_closed else "Open")
            self.right_eye_state.text = "Right Eye: " + ("Closed" if self.right_eye_closed else "Open")

            # Sound alert if both eyes closed for consecutive frames
            if self.left_eye_closed and self.right_eye_closed:
                self.closed_counter += 1
                if self.closed_counter >= self.consec_frames:
                    winsound.Beep(1000, 1000)
            else:
                self.closed_counter = 0

        # Convert the image for Kivy
        buf = cv2.flip(img, 0).tostring()
        texture = Texture.create(size=(img.shape[1], img.shape[0]), colorfmt="bgr")
        texture.blit_buffer(buf, colorfmt="bgr", bufferfmt="ubyte")
        self.img_texture.texture = texture

    def on_stop(self):
        self.cap.release()

if __name__ == '__main__':
    EyeDetectionApp().run()
