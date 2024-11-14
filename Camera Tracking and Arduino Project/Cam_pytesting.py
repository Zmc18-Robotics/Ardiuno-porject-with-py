import cv2
import mediapipe as mp
import numpy as np

# Inisialisasi deteksi wajah, tangan, dan gambar
mp_face = mp.solutions.face_detection
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Inisialisasi deteksi wajah dan tangan
face_detector = mp_face.FaceDetection(min_detection_confidence=0.5)
hand_detector = mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Inisialisasi video capture
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Tidak bisa membuka kamera")
    exit()

# Fungsi untuk menghitung jumlah jari yang terangkat
def count_fingers(hand_landmarks):
    tips_ids = [4, 8, 12, 16, 20]  # ID untuk ujung jari (ibu jari, telunjuk, tengah, manis, kelingking)
    fingers = []

    if hand_landmarks.landmark[tips_ids[0]].x < hand_landmarks.landmark[tips_ids[0] - 1].x:
        fingers.append(1)  # Jari terangkat
    else:
        fingers.append(0)  # Jari tidak terangkat

    for i in range(1, 5):
        if hand_landmarks.landmark[tips_ids[i]].y < hand_landmarks.landmark[tips_ids[i] - 2].y:
            fingers.append(1)  # Jari terangkat
        else:
            fingers.append(0)  # Jari tidak terangkat

    return fingers.count(1)  # Menghitung jumlah jari terangkat

# Fungsi untuk memeriksa apakah jari telunjuk dan jempol sedang memegang objek
def is_thumb_and_index_touching(hand_landmarks):
    # Menggunakan titik 4 (telunjuk) dan 2 (jempol) dari tangan
    index_tip = hand_landmarks.landmark[8]
    thumb_tip = hand_landmarks.landmark[4]
    
    # Menghitung jarak antara ujung telunjuk dan jempol
    distance = np.sqrt((index_tip.x - thumb_tip.x) ** 2 + (index_tip.y - thumb_tip.y) ** 2)
    
    return distance < 0.05  # Misalnya, jika jarak kurang dari nilai ini, kita anggap mereka sedang memegang sesuatu

while True:
    ret, frame = cap.read()
    if not ret:
        print("Tidak bisa menerima frame")
        break

    # Membalikkan frame agar seperti melihat cermin
    frame = cv2.flip(frame, 1)

    # Mengubah gambar ke RGB untuk pemrosesan MediaPipe
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Deteksi wajah menggunakan MediaPipe
    faces = face_detector.process(rgb_frame)
    if faces.detections:
        for i, detection in enumerate(faces.detections):
            # Menggambar landmark wajah pada frame
            mp_drawing.draw_detection(frame, detection)
            # Menambahkan teks untuk objek manusia
            text = f"Objek manusia {i+1}"
            cv2.putText(frame, text, (int(detection.location_data.relative_bounding_box.xmin * frame.shape[1]),
                                      int(detection.location_data.relative_bounding_box.ymin * frame.shape[0]) - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

    # Deteksi tangan menggunakan MediaPipe
    results = hand_detector.process(rgb_frame)
    if results.multi_hand_landmarks:
        for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
            # Menggambar landmark tangan di frame
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Menghitung jumlah jari yang terangkat
            fingers_up = count_fingers(hand_landmarks)

            # Menambahkan teks untuk jumlah jari terangkat
            cv2.putText(frame, f'Objek Manusia {idx+1}: Jari Terangkat: {fingers_up}', (10, 50 + idx * 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # Cek jika jempol dan telunjuk sedang memegang sesuatu
            if is_thumb_and_index_touching(hand_landmarks):
                # Jika tangan memegang gunting, lanjutkan ke deteksi gunting
                print(f"Tangan {idx+1} sedang memegang gunting!")

                # Deteksi objek gunting menggunakan OpenCV
                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

                # Filter untuk warna hitam (gagang gunting)
                lower_black = np.array([0, 0, 0])
                upper_black = np.array([180, 255, 80])  # Menurunkan batas saturasi untuk filter lebih ketat
                mask_black = cv2.inRange(hsv, lower_black, upper_black)

                # Filter untuk warna silver (besi gunting)
                lower_silver = np.array([0, 0, 100])
                upper_silver = np.array([180, 50, 255])  # Menurunkan batas saturasi untuk filter lebih ketat
                mask_silver = cv2.inRange(hsv, lower_silver, upper_silver)

                # Gabungkan kedua mask
                combined_mask = cv2.bitwise_or(mask_black, mask_silver)
                result = cv2.bitwise_and(frame, frame, mask=combined_mask)

                # Meningkatkan deteksi tepi dengan filter tambahan (GaussianBlur)
                blurred_result = cv2.GaussianBlur(result, (5, 5), 0)
                edges = cv2.Canny(blurred_result, 50, 150)

                # Temukan kontur dalam hasil deteksi tepi
                contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                stable_box = None

                for cnt in contours:
                    area = cv2.contourArea(cnt)
                    if 1500 < area < 5000:  # Sesuaikan ukuran gunting (kurangi ukuran minimum jika perlu)
                        approx = cv2.approxPolyDP(cnt, 0.02 * cv2.arcLength(cnt, True), True)
                        x, y, w, h = cv2.boundingRect(approx)

                        # Cek bahwa objek gunting memiliki dimensi yang lebih tinggi dari lebar dan cukup besar
                        if h > w and area > 1500:  # Meningkatkan deteksi objek besar
                            # Inisialisasi tracker dengan bounding box pertama kali ditemukan
                            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                            cv2.putText(frame, "Gunting", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                # Deteksi HP hanya jika jari-jari memegang
                hsv_hp = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                lower_black_hp = np.array([0, 0, 0])  # Untuk warna gelap
                upper_black_hp = np.array([180, 255, 80])
                mask_hp = cv2.inRange(hsv_hp, lower_black_hp, upper_black_hp)

                # Menambahkan filter bentuk untuk menghindari deteksi jari
                contours_hp, _ = cv2.findContours(mask_hp, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                for cnt in contours_hp:
                    area_hp = cv2.contourArea(cnt)
                    x_hp, y_hp, w_hp, h_hp = cv2.boundingRect(cnt)
                    
                    # Sesuaikan batasan ukuran dan bentuk HP
                    if area_hp > 10000 and h_hp > w_hp * 1.5:  # HP lebih tinggi daripada lebar dan cukup besar
                        # Periksa posisi objek lebih dekat ke kamera
                        if y_hp < frame.shape[0] // 2:  # Objek harus lebih dekat dengan kamera (posisi lebih tinggi di frame)
                            cv2.rectangle(frame, (x_hp, y_hp), (x_hp + w_hp, y_hp + h_hp), (0, 0, 255), 2)
                            cv2.putText(frame, "HP", (x_hp, y_hp - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

    # Tampilkan frame hasil deteksi
    cv2.imshow("Deteksi Objek dan Tangan", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()