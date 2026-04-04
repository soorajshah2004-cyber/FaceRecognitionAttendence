import face_recognition
import cv2
import os
import csv
from datetime import datetime

# ---------- ATTENDANCE ----------
marked = set()

def mark_attendance(name):
    if name not in marked:
        with open("attendance.csv", "a", newline="") as f:
            writer = csv.writer(f)
            time_now = datetime.now().strftime("%H:%M:%S")
            writer.writerow([name, time_now])
            marked.add(name)

        print(f"✅ Attendance saved: {name}")

# ---------- SETTINGS ----------
IMAGE_FOLDER = "images"

# ---------- LOAD IMAGES ----------
known_images = []
known_names = []

if not os.path.exists(IMAGE_FOLDER):
    print("❌ 'images' folder not found")
    exit()

for file in os.listdir(IMAGE_FOLDER):
    file_path = os.path.join(IMAGE_FOLDER, file)

    try:
        img = face_recognition.load_image_file(file_path)
        known_images.append(img)
        known_names.append(os.path.splitext(file)[0])
    except Exception as e:
        print(f"Error loading {file}: {e}")

print(f"✅ Loaded {len(known_images)} images")

# ---------- ENCODE FACES ----------
known_encodings = []

for img in known_images:
    try:
        enc = face_recognition.face_encodings(img)

        if len(enc) > 0:
            known_encodings.append(enc[0])
        else:
            print("⚠ No face found in one image")

    except Exception as e:
        print("Encoding error:", e)

print("✅ Encoding complete")

# ---------- START WEBCAM ----------
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("❌ Cannot access camera")
    exit()

print("🎥 Camera started... Press Q to exit")

while True:
    success, frame = cap.read()

    if not success:
        print("❌ Failed to read frame")
        break

    # Convert to RGB
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Detect faces
    face_locations = face_recognition.face_locations(rgb)
    face_encodings = face_recognition.face_encodings(rgb, face_locations)

    for face_encoding, face_location in zip(face_encodings, face_locations):
        matches = face_recognition.compare_faces(known_encodings, face_encoding)

        name = "Unknown"

        # ✅ FIXED INDENTATION
        if True in matches:
            match_index = matches.index(True)
            name = known_names[match_index]
            mark_attendance(name)


        top, right, bottom, left = face_location

        # Draw rectangle
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

        # Show name
        cv2.putText(frame, name, (left, top - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow("Face Recognition", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# ---------- CLEANUP ----------
cap.release()
cv2.destroyAllWindows()