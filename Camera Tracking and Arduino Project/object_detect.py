import cv2
import numpy as np

# Memuat gambar template (gambar gunting atau botol)
scissors_template = cv2.imread('scissors_template.jpg', 0)  # Gambar template gunting dalam grayscale
bottle_template = cv2.imread('bottle_template.jpg', 0)  # Gambar template botol dalam grayscale

# Membuka kamera
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Kamera tidak dapat dibuka")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Tidak bisa menerima frame (end of stream?)")
        break

    # Mengubah frame menjadi grayscale
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Template Matching untuk deteksi gunting
    res_scissors = cv2.matchTemplate(gray_frame, scissors_template, cv2.TM_CCOEFF_NORMED)
    threshold_scissors = 0.8  # Ambang batas kesamaan (semakin tinggi, semakin akurat)
    loc_scissors = np.where(res_scissors >= threshold_scissors)

    # Template Matching untuk deteksi botol
    res_bottle = cv2.matchTemplate(gray_frame, bottle_template, cv2.TM_CCOEFF_NORMED)
    threshold_bottle = 0.8  # Ambang batas kesamaan
    loc_bottle = np.where(res_bottle >= threshold_bottle)

    # Menambahkan kotak di sekitar objek gunting yang terdeteksi
    for pt in zip(*loc_scissors[::-1]):
        cv2.rectangle(frame, pt, (pt[0] + scissors_template.shape[1], pt[1] + scissors_template.shape[0]), (0, 255, 0), 2)
        cv2.putText(frame, "Gunting Terdeteksi", (pt[0], pt[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    # Menambahkan kotak di sekitar objek botol yang terdeteksi
    for pt in zip(*loc_bottle[::-1]):
        cv2.rectangle(frame, pt, (pt[0] + bottle_template.shape[1], pt[1] + bottle_template.shape[0]), (0, 0, 255), 2)
        cv2.putText(frame, "Botol Terdeteksi", (pt[0], pt[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    # Menampilkan frame dengan deteksi objek
    cv2.imshow('Kamera', frame)

    # Tekan 'q' untuk keluar dari loop
    if cv2.waitKey(1) == ord('q'):
        break

# Melepaskan objek VideoCapture dan menutup jendela
cap.release()
cv2.destroyAllWindows()
