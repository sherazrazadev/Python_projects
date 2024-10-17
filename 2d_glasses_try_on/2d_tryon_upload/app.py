from flask import Flask, render_template, request, jsonify
import cv2
import numpy as np
import os
import base64
import mediapipe as mp
import requests

app = Flask(__name__)

# Ensure the necessary directories exist
os.makedirs('static/uploads', exist_ok=True)
os.makedirs('static/output', exist_ok=True)

# Initialize Mediapipe face mesh model
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, min_detection_confidence=0.5)
processed_image_path = 'static/output/processed_image.png'
# # Global variable to hold the overlay image
# overlay = cv2.imread(processed_image, cv2.IMREAD_UNCHANGED)  # Pre-load the glasses overlay

@app.route('/')
def index():
    return render_template('index3.html')  # Make sure the file name matches the HTML file

@app.route('/remove_bg', methods=['POST'])
def remove_bg():
    try:
        # Decode the uploaded image from base64
        data = request.json['image']
        encoded_data = data.split(',')[1]
        nparr = np.frombuffer(base64.b64decode(encoded_data), np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # Call remove.bg API to remove the background
        response = requests.post(
            'https://api.remove.bg/v1.0/removebg',
            files={'image_file': cv2.imencode('.png', img)[1].tobytes()},
            data={'size': 'auto'},
            headers={'X-Api-Key': '3Fhi4zizdBrBTiB64Hp92sD7'},  # Replace with your actual API key
        )

        if response.status_code == 200:
            # Read the background-removed image
            nparr = np.frombuffer(response.content, np.uint8)
            bg_removed_img = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)
            cv2.imwrite(processed_image_path, bg_removed_img)

            # Encode processed image to send back
            _, buffer = cv2.imencode('.png', bg_removed_img)
            response_img = base64.b64encode(buffer).decode('utf-8')
            return jsonify({'status': 'success', 'image': 'data:image/png;base64,' + response_img})
        else:
            return jsonify({'status': 'error', 'message': 'Failed to remove background.'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/apply_overlay', methods=['POST'])
def apply_overlay():
    try:
        # Load the processed image dynamically as the overlay
        if not os.path.exists(processed_image_path):
            return jsonify({'status': 'error', 'message': 'No background-removed image available.'})

        overlay = cv2.imread(processed_image_path, cv2.IMREAD_UNCHANGED)
        if overlay is None:
            return jsonify({'status': 'error', 'message': 'Failed to load the overlay image.'})

        # Decode the webcam image from base64
        data = request.json['image']
        encoded_data = data.split(',')[1]
        nparr = np.frombuffer(base64.b64decode(encoded_data), np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # Resize the webcam image for processing
        resized_img = resize_image_for_detection(img)
        landmarks = get_landmarks(resized_img)

        if landmarks:
            processed_img = apply_glasses_overlay(resized_img, landmarks, overlay)
        else:
            processed_img = resized_img

        # Encode processed image to send back
        _, buffer = cv2.imencode('.png', processed_img)
        response_img = base64.b64encode(buffer).decode('utf-8')
        return jsonify({'status': 'success', 'image': 'data:image/png;base64,' + response_img})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

def resize_image_for_detection(image, max_width=800):
    h, w = image.shape[:2]
    if w > max_width:
        scale_ratio = max_width / w
        new_w = int(w * scale_ratio)
        new_h = int(h * scale_ratio)
        resized_image = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
        return resized_image
    return image

def get_landmarks(frame):
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb_frame)

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            landmarks = [(int(landmark.x * frame.shape[1]), int(landmark.y * frame.shape[0])) for landmark in face_landmarks.landmark]
            return landmarks
    return []

def apply_glasses_overlay(frame, landmarks, overlay):
    if len(landmarks) > 263 and overlay is not None:
        left_eye = landmarks[130]
        right_eye = landmarks[359]

        eye_center = ((left_eye[0] + right_eye[0]) // 2, (left_eye[1] + right_eye[1]) // 2)
        eye_width = np.linalg.norm(np.array(right_eye) - np.array(left_eye))

        glasses_width = int(1.5 * eye_width)
        glasses_height = int(overlay.shape[0] * (glasses_width / overlay.shape[1]))

        resized_overlay = cv2.resize(overlay, (glasses_width, glasses_height), interpolation=cv2.INTER_AREA)
        x_offset = eye_center[0] - glasses_width // 2
        y_offset = eye_center[1] - glasses_height // 2

        for i in range(glasses_height):
            for j in range(glasses_width):
                y, x = y_offset + i, x_offset + j
                if 0 <= x < frame.shape[1] and 0 <= y < frame.shape[0]:
                    alpha = resized_overlay[i, j, 3] / 255.0
                    if alpha > 0:
                        frame[y, x] = (1 - alpha) * frame[y, x] + alpha * resized_overlay[i, j, :3]

    return frame

if __name__ == '__main__':
    app.run(debug=True)
