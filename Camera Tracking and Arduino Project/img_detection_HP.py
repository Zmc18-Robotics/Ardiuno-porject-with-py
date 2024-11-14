import cv2
import numpy as np
import mediapipe as mp

# Inisialisasi MediaPipe untuk deteksi tangan
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Buka kamera
cap = cv2.VideoCapture(0)

# Fungsi untuk menghitung bounding box sekitar jari telunjuk dan ibu jari
def estimate_phone_bbox(landmarks, frame_width, frame_height):
    index_tip = landmarks[8]
    thumb_tip = landmarks[4]
    x_min = int(min(index_tip.x, thumb_tip.x) * frame_width) - 30
    x_max = int(max(index_tip.x, thumb_tip.x) * frame_width) + 30
    y_min = int(min(index_tip.y, thumb_tip.y) * frame_height) - 30
    y_max = int(max(index_tip.y, thumb_tip.y) * frame_height) + 30
    return (x_min, y_min, x_max - x_min, y_max - y_min)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    frame_height, frame_width, _ = frame.shape
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Deteksi tangan
    hand_results = hands.process(rgb_frame)
    phone_detected = False

    if hand_results.multi_hand_landmarks:
        for hand_landmarks in hand_results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Hitung bounding box untuk HP berdasarkan posisi jari telunjuk dan ibu jari
            bbox = estimate_phone_bbox(hand_landmarks.landmark, frame_width, frame_height)

            # Deteksi HP berdasarkan warna hitam di dalam bounding box
            x, y, w, h = bbox
            phone_area = frame[y:y+h, x:x+w]
            hsv_phone_area = cv2.cvtColor(phone_area, cv2.COLOR_BGR2HSV)

            # Mask untuk warna hitam (HP)
            lower_black = np.array([0, 0, 0])
            upper_black = np.array([180, 255, 50])
            mask_black = cv2.inRange(hsv_phone_area, lower_black, upper_black)

            # Jika ada cukup area hitam, anggap sebagai HP
            if cv2.countNonZero(mask_black) > 500:
                phone_detected = True
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, "HP Terdeteksi", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                break

    # Tampilkan hasil deteksi
    cv2.imshow("Deteksi HP", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
