import cv2
import face_recognition
import os
import csv
from datetime import datetime
from flask import Flask, render_template, Response, jsonify

app = Flask(__name__)

# ---------- LOAD FACES ----------
IMAGE_FOLDER = "images"
known_encodings = []
known_names = []

for file in os.listdir(IMAGE_FOLDER):
    path = os.path.join(IMAGE_FOLDER, file)
    img = face_recognition.load_image_file(path)
    enc = face_recognition.face_encodings(img)

    if len(enc) > 0:
        known_encodings.append(enc[0])
        known_names.append(os.path.splitext(file)[0])

print("✅ Faces Loaded")

# ---------- ATTENDANCE ----------
marked = set()

def mark_attendance(name):
    if name not in marked:
        with open("attendance.csv", "a", newline="") as f:
            writer = csv.writer(f)
            time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            writer.writerow([name, time_now])
            marked.add(name)

        print(f"✅ Attendance saved: {name}")

# ---------- CAMERA ----------
camera = cv2.VideoCapture(0)

def gen_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        faces = face_recognition.face_locations(rgb)
        encodings = face_recognition.face_encodings(rgb, faces)

        for enc, face in zip(encodings, faces):
            face_distances = face_recognition.face_distance(known_encodings, enc)
            name = "Unknown"

            if len(face_distances) > 0:
                best_match_index = face_distances.argmin()

                if face_distances[best_match_index] < 0.5:
                    name = known_names[best_match_index]
                    mark_attendance(name)

            top, right, bottom, left = face

            cv2.rectangle(frame, (left, top), (right, bottom), (0,255,0), 2)
            cv2.putText(frame, name, (left, top-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# ---------- ROUTES ----------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video')
def video():
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/attendance')
def attendance():
    data = []
    if os.path.exists("attendance.csv"):
        with open("attendance.csv", "r") as f:
            reader = csv.reader(f)
            data = list(reader)
    return jsonify({"data": data})

@app.route('/reset')
def reset():
    open("attendance.csv", "w").close()
    marked.clear()
    return jsonify({"status": "cleared"})

# ---------- RUN ----------
if __name__ == "__main__":
    app.run(debug=True)