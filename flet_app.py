import flet as ft
import cv2
import base64

def main(page: ft.Page):
    image = ft.Image(src="alarm.py", error_content=ft.Text("Click capture"))

    def record(event):
        page.session.set("state", True)
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            raise Exception("Could not open camera")

        while page.session.get("state"):
        # Step 2: Capture a frame
            ret, frame = cap.read()
            if not ret:
                break

            # Step 3: Encode the frame as a binary buffer
            _, buffer = cv2.imencode('.jpg', frame)  # Encoding the frame as a JPG image

            # Step 4: Convert the binary buffer to a Base64 string
            frame_base64 = base64.b64encode(buffer).decode('utf-8')

            # Print the Base64 string (or use it in your application)
            image.src_base64 = frame_base64
            image.update()
    
    def close(event):
        page.session.set("state", False)

    button = ft.ElevatedButton("Capture")
    button.on_click = record

    off = ft.ElevatedButton("OFF")
    off.on_click = close
    
    page.controls.append(image)
    page.controls.append(button)
    page.controls.append(off)
    page.update()

ft.app(target = main)