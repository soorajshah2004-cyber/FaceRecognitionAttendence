# ---------- IMPORTS ----------
import cv2
import face_recognition
import os
import csv
from datetime import datetime
from flask import Flask, render_template, Response, jsonify

app = Flask(__name__)

# ---------- LOAD KNOWN FACES ----------
IMAGE_FOLDER = "images"
known_faces = []   # stores face encodings
known_names = []   # stores names

def load_faces():
    for file in os.listdir(IMAGE_FOLDER):
        path = os.path.join(IMAGE_FOLDER, file)

        image = face_recognition.load_image_file(path)
        encodings = face_recognition.face_encodings(image)

        if encodings:
            known_faces.append(encodings[0])
            name = os.path.splitext(file)[0]
            known_names.append(name)

    print("✅ Faces Loaded")

load_faces()


# ---------- ATTENDANCE SYSTEM ----------
marked_names = set()

def mark_attendance(name):
    if name not in marked_names:
        with open("attendance.csv", "a", newline="") as file:
            writer = csv.writer(file)
            time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            writer.writerow([name, time_now])

        marked_names.add(name)
        print(f"✅ Marked: {name}")


# ---------- CAMERA ----------
camera = cv2.VideoCapture(0)

def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break

        # Convert to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Detect faces
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for encoding, location in zip(face_encodings, face_locations):
            name = "Unknown"

            # Compare with known faces
            if known_faces:
                distances = face_recognition.face_distance(known_faces, encoding)
                best_match = distances.argmin()

                if distances[best_match] < 0.5:
                    name = known_names[best_match]
                    mark_attendance(name)

            # Draw rectangle and name
            top, right, bottom, left = location
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(frame, name, (left, top - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Convert frame to bytes
        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')


# ---------- ROUTES ----------
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/video')
def video():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/attendance')
def get_attendance():
    data = []

    if os.path.exists("attendance.csv"):
        with open("attendance.csv", "r") as file:
            data = list(csv.reader(file))

    return jsonify({"data": data})


@app.route('/reset')
def reset_attendance():
    open("attendance.csv", "w").close()
    marked_names.clear()
    return jsonify({"status": "cleared"})


# ---------- RUN APP ----------
if __name__ == "__main__":
    app.run(debug=True)
