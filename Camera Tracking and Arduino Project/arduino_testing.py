import time
import pyfirmata2

# Konfigurasi pin dan port
PORT = pyfirmata2.Arduino.AUTODETECT
buzzer_pin = 10

# Frekuensi nada untuk lagu "Selamat Ulang Tahun" (Do, Re, Mi dan seterusnya)
C4 = 261   # Do rendah
D4 = 294   # Re
E4 = 329   # Mi
F4 = 349   # Fa
G4 = 392   # Sol
A4_ = 440  # La
B4 = 494   # Si
C5 = 523   # Do tinggi
D5 = 587   # Re tinggi
E5 = 659   # Mi tinggi
F5 = 698   # Fa tinggi
G5 = 784   # Sol tinggi

# Melodi lagu "Selamat Ulang Tahun"
melody = [
    G4, G4, A4_, G4, C5, B4,  # "Happy birthday to you"
    G4, G4, A4_, G4, D5, C5,  # "Happy birthday to you"
    G4, G4, G5, E5, C5, B4, A4_,  # "Happy birthday, dear [name]"
    F5, F5, E5, C5, D5, C5   # "Happy birthday to you"
]

# Durasi untuk masing-masing not dalam lagu (semakin kecil nilainya, semakin cepat nadanya)
note_durations = [
    4, 4, 4, 4, 2, 2,  # Baris pertama
    4, 4, 4, 4, 2, 2,  # Baris kedua
    4, 4, 4, 4, 4, 4, 4,  # Baris ketiga
    2, 2, 4, 4, 4, 2   # Baris keempat
]

# Inisialisasi koneksi ke Arduino
board = pyfirmata2.Arduino(PORT)
print("Memulai lagu 'Selamat Ulang Tahun'...")

# Fungsi untuk memainkan nada
def play_tone(frequency, duration_s):
    period = 1.0 / frequency  # Periode waktu per siklus
    cycles = int(duration_s / (period * 2))  # Jumlah siklus ON/OFF
    for _ in range(cycles):
        board.digital[buzzer_pin].write(1)  # ON
        time.sleep(period / 2)
        board.digital[buzzer_pin].write(0)  # OFF
        time.sleep(period / 2)

# Fungsi untuk memainkan lagu
def play_song():
    for i in range(len(melody)):
        duration = note_durations[i] / 4  # Durasi nada dalam detik
        play_tone(melody[i], duration)  # Mainkan nada
        time.sleep(0.1)  # Jeda antar nada

    print("Lagu selesai.")

# Mainkan lagu sekali
play_song()

# Tutup koneksi
board.exit()
