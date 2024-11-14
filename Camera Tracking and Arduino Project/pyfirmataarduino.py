import pyfirmata2
import time

# Tentukan port yang digunakan oleh Arduino
port = pyfirmata2.Arduino.AUTODETECT  # Mendeteksi port Arduino secara otomatis
board = pyfirmata2.Arduino(port)

# Tentukan pin LED
led_pin_1 = 2  # Pin untuk LED pertama
led_pin_2 = 3  # Pin untuk LED kedua

# Loop untuk menyalakan dan mematikan kedua LED setiap 1 detik
try:
    while True:
        # Menyalakan LED pertama dan mematikan LED kedua
        board.digital[led_pin_1].write(1)  # Menyalakan LED pertama
        board.digital[led_pin_2].write(0)  # Mematikan LED kedua
        print("LED 1 ON, LED 2 OFF")
        time.sleep(1)  # Tunggu 1 detik

        # Menyalakan LED kedua dan mematikan LED pertama
        board.digital[led_pin_1].write(0)  # Mematikan LED pertama
        board.digital[led_pin_2].write(1)  # Menyalakan LED kedua
        print("LED 1 OFF, LED 2 ON")
        time.sleep(1)  # Tunggu 1 detik

except KeyboardInterrupt:
    print("Program dihentikan")
finally:
    board.close()  # Menutup koneksi dengan Arduino
