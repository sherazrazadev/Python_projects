from flask import Flask, render_template, Response
import cv2
import cvzone

app = Flask(__name__)

# Load the face detection model
cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Initialize overlay counter
num = 1
max_overlay = 29

def gen_frames():
    global num
    # Open the webcam
    cap = cv2.VideoCapture(0)

    while True:
        # Capture frame-by-frame
        success, frame = cap.read()
        if not success:
            break

        # Convert to grayscale for face detection
        gray_scale = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = cascade.detectMultiScale(gray_scale, scaleFactor=1.1, minNeighbors=5)

        # Load the current overlay image
        overlay = cv2.imread(f'static/Glasses/glass{num}.png', cv2.IMREAD_UNCHANGED)

        # Apply overlay for each detected face
        for (x, y, w, h) in faces:
            overlay_resize = cv2.resize(overlay, (w, int(h * 0.8)))
            frame = cvzone.overlayPNG(frame, overlay_resize, [x, y])

        # Encode frame as JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()

@app.route('/')
def index():
    # Render the index page
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    # Video streaming route
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/next_overlay')
def next_overlay():
    global num
    num += 1
    if num > max_overlay:
        num = 1
    return "Overlay switched"

if __name__ == '__main__':
    app.run(debug=True)
