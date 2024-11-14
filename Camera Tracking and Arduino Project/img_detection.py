import cv2
import numpy as np
from collections import deque

# Buka kamera
cap = cv2.VideoCapture(0)

# Cek apakah kamera terbuka dengan benar
if not cap.isOpened():
    print("Gagal membuka kamera.")
    exit()

# Inisialisasi detektor wajah Haar Cascade
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Menggunakan deque untuk menyimpan beberapa posisi bounding box terakhir
buffer_size = 5
recent_boxes = deque(maxlen=buffer_size)

# Inisialisasi tracker
tracker = cv2.TrackerKCF_create()

# Variabel untuk pelacakan pertama kali
is_tracking = False

# Variabel untuk melacak frame yang hilang
frame_counter = 0
max_lost_frames = 30  # Maksimal frame tanpa deteksi sebelum kembali ke deteksi ulang

while True:
    try:
        # Ambil frame dari kamera
        ret, frame = cap.read()

        # Cek apakah frame berhasil diambil
        if not ret:
            print("Gagal mengambil frame, mencoba lagi...")
            continue  # Lewati loop jika frame tidak valid

        # Cek apakah frame kosong
        if frame is None:
            print("Frame kosong, coba lagi...")
            continue

        # Ubah gambar ke dalam warna HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Filter untuk warna hitam (gagang gunting)
        lower_black = np.array([0, 0, 0])
        upper_black = np.array([180, 255, 80])  # Lebih ketat agar tidak menangkap wajah
        mask_black = cv2.inRange(hsv, lower_black, upper_black)

        # Filter untuk warna silver (besi gunting)
        lower_silver = np.array([0, 0, 100])
        upper_silver = np.array([180, 50, 255])  # Lebih ketat agar tidak menangkap wajah
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

        # Deteksi wajah pada frame untuk menghindari deteksi wajah sebagai gunting
        faces = face_cascade.detectMultiScale(frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if 1500 < area < 5000:  # Sesuaikan ukuran gunting
                approx = cv2.approxPolyDP(cnt, 0.02 * cv2.arcLength(cnt, True), True)
                x, y, w, h = cv2.boundingRect(approx)

                # Hanya tampilkan jika objek cukup tinggi
                if h > w * 1.5:  # Mencegah deteksi lubang tangan atau bentuk persegi kecil
                    # Cek apakah bagian dari kontur berada dalam area wajah yang terdeteksi
                    for (fx, fy, fw, fh) in faces:
                        if (fx < x + w and fx + fw > x and fy < y + h and fy + fh > y):
                            # Jika kontur tumpang tindih dengan wajah, abaikan kontur ini
                            break
                    else:
                        # Inisialisasi tracker dengan bounding box pertama kali ditemukan
                        if not is_tracking and w > 50 and h > 50:  # Pastikan ukuran box cukup besar
                            tracker.init(frame, (x, y, w, h))
                            is_tracking = True

                        # Simpan bounding box di buffer untuk stabilisasi
                        recent_boxes.append((x, y, w, h))

                        # Hitung rata-rata bounding box dari beberapa frame terakhir
                        avg_x = int(np.mean([box[0] for box in recent_boxes]))
                        avg_y = int(np.mean([box[1] for box in recent_boxes]))
                        avg_w = int(np.mean([box[2] for box in recent_boxes]))
                        avg_h = int(np.mean([box[3] for box in recent_boxes]))

                        # Membatasi ukuran bounding box agar tidak terlalu besar
                        max_width = 200  # Maksimal lebar box (perkecil dari 250)
                        max_height = 100  # Maksimal tinggi box (perkecil dari 120)
                        avg_w = min(avg_w, max_width)
                        avg_h = min(avg_h, max_height)

                        # Tampilkan bounding box yang stabil
                        stable_box = (avg_x, avg_y, avg_w, avg_h)
                        cv2.rectangle(frame, (avg_x, avg_y), (avg_x + avg_w, avg_y + avg_h), (0, 255, 0), 2)
                        cv2.putText(frame, "Gunting", (avg_x, avg_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                        break

        if is_tracking:
            # Update posisi tracker jika sudah terdeteksi
            success, bbox = tracker.update(frame)
            if success:
                x, y, w, h = [int(v) for v in bbox]

                # Pastikan bounding box tetap berada dalam batas frame
                h, w, _ = frame.shape
                x = max(0, min(x, w - 1))
                y = max(0, min(y, h - 1))
                w = min(w - x, w - 1)
                h = min(h - y, h - 1)

                # Membatasi ukuran bounding box agar tidak terlalu besar
                max_width = 200  # Lebar box maksimum (perkecil dari 250)
                max_height = 100  # Tinggi box maksimum (perkecil dari 120)
                w = min(w, max_width)
                h = min(h, max_height)

                # Simpan bounding box di buffer untuk stabilisasi
                recent_boxes.append((x, y, w, h))

                # Hitung rata-rata bounding box dari beberapa frame terakhir
                avg_x = int(np.mean([box[0] for box in recent_boxes]))
                avg_y = int(np.mean([box[1] for box in recent_boxes]))
                avg_w = int(np.mean([box[2] for box in recent_boxes]))
                avg_h = int(np.mean([box[3] for box in recent_boxes]))

                # Tampilkan bounding box yang stabil
                cv2.rectangle(frame, (avg_x, avg_y), (avg_x + avg_w, avg_y + avg_h), (0, 255, 0), 2)
                cv2.putText(frame, "Gunting", (avg_x, avg_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            else:
                # Jika tracking gagal, reset dan mulai deteksi ulang
                frame_counter += 1
                print(f"Pelacakan gagal. Frame hilang: {frame_counter}")
                
                if frame_counter > max_lost_frames:  # Jika sudah terlalu lama tanpa deteksi, reset tracker
                    print("Tracker hilang terlalu lama. Beralih ke deteksi ulang.")
                    is_tracking = False
                    tracker.clear()  # Clear tracker untuk menghindari error saat update selanjutnya
                    frame_counter = 0  # Reset counter
                    continue  # Melanjutkan ke deteksi objek

        # Menampilkan frame dengan hasil deteksi
        cv2.imshow("Deteksi Gunting Stabil dengan Pelacakan", frame)

        # Tekan 'q' untuk keluar secara manual
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    except cv2.error as e:
        print(f"Terjadi kesalahan dengan OpenCV: {e}")
        break
    except Exception as e:
        print(f"Kesalahan tak terduga: {e}")
        break

# Lepaskan kamera dan tutup semua jendela
cap.release()
cv2.destroyAllWindows()