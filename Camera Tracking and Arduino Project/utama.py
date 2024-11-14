import cv2
import mediapipe as mp
from handDetection import HandDetection  # Pastikan file ini ada dan sesuai dengan nama

# Memuat model Haar Cascade untuk deteksi wajah dan tangan
face_cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
hand_cascade_path = 'haarcascade_hand.xml'  # Ganti dengan path ke file haarcascade_hand.xml

# Periksa apakah file cascade dapat dimuat
if not cv2.CascadeClassifier(face_cascade_path).empty():
    print("Model Haar Cascade untuk wajah berhasil dimuat.")
else:
    print(f"Error: Tidak dapat memuat model Haar Cascade untuk wajah dari {face_cascade_path}")
    exit()

if not cv2.CascadeClassifier(hand_cascade_path).empty():
    print("Model Haar Cascade untuk tangan berhasil dimuat.")
else:
    print(f"Error: Tidak dapat memuat model Haar Cascade untuk tangan dari {hand_cascade_path}")
    exit()

# Inisialisasi MediaPipe untuk deteksi tangan
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

# Inisialisasi objek HandDetection
handDetection = HandDetection(min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Membuka webcam
webcam = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not webcam.isOpened():  # Mengecek apakah kamera terbuka
    print("Kamera tidak dapat dibuka")
    exit()

# Variabel untuk melacak posisi tangan dari frame sebelumnya
previous_hands_positions = {}

while True:
    status, frame = webcam.read()
    if not status:
        print("Tidak bisa menerima frame")
        break

    # Membalikkan frame agar seperti melihat cermin
    frame = cv2.flip(frame, 1)

    # Mengubah gambar ke grayscale untuk deteksi wajah dan tangan dengan Haar Cascade
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Deteksi wajah dengan Haar Cascade
    face_cascade = cv2.CascadeClassifier(face_cascade_path)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    # Deteksi tangan dengan Haar Cascade
    hand_cascade = cv2.CascadeClassifier(hand_cascade_path)
    hands = hand_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(50, 50))

    # Menambahkan kotak dan teks di setiap wajah yang terdeteksi
    for i, (x, y, w, h) in enumerate(faces, 1):  # Mulai menghitung dari 1
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 255), 2)
        text = f"objek manusia {i}"
        cv2.putText(frame, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

    # Deteksi dan pelacakan lambaian tangan dengan Haar Cascade
    for j, (hx, hy, hw, hh) in enumerate(hands, 1):
        hand_position = (hx, hy)

        # Lacak gerakan tangan antar frame
        if j in previous_hands_positions:
            prev_position = previous_hands_positions[j]
            movement_distance = ((hand_position[0] - prev_position[0]) ** 2 + (hand_position[1] - prev_position[1]) ** 2) ** 0.5

            # Jika tangan bergerak cukup jauh dalam waktu singkat, anggap sebagai lambaian
            if movement_distance > 30:
                cv2.rectangle(frame, (hx, hy), (hx + hw, hy + hh), (255, 0, 0), 2)
                text = f"lambaian tangan objek {j}"
                cv2.putText(frame, text, (hx, hy - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

        # Perbarui posisi tangan sebelumnya
        previous_hands_positions[j] = hand_position

    # Deteksi tangan menggunakan MediaPipe (untuk deteksi landmark tangan)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    if results.multi_hand_landmarks:
        for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
            # Menggambar landmark tangan di frame
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Menghitung jari yang diangkat
            fingers_up = handDetection.count_fingers(hand_landmarks)
            cv2.putText(frame, f'Objek Manusia {idx + 1}: Jari Terangkat: {fingers_up}', (10, 50 + idx * 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Menampilkan frame dengan hasil deteksi
    cv2.imshow('Kamera', frame)

    # Tekan 'q' untuk keluar dari loop
    if cv2.waitKey(1) == ord('q'):
        break

# Membersihkan setelah selesai
webcam.release()
cv2.destroyAllWindows()
