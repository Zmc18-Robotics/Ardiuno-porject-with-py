import pyfirmata2
import time
import tkinter as tk

# Tentukan port yang digunakan oleh Arduino
port = pyfirmata2.Arduino.AUTODETECT  # Mendeteksi port Arduino secara otomatis
board = pyfirmata2.Arduino(port)

# Tentukan pin LED dan buzzer
led_pin_1 = 2  # Pin untuk LED pertama
led_pin_2 = 3  # Pin untuk LED kedua
buzzer_pin = 10  # Pin untuk buzzer (PWM)

# Set pin LED dan buzzer sebagai output
board.digital[led_pin_1].mode = pyfirmata2.OUTPUT
board.digital[led_pin_2].mode = pyfirmata2.OUTPUT
board.digital[buzzer_pin].mode = pyfirmata2.PWM  # Set buzzer pin sebagai PWM

# Variabel untuk mengatur kecepatan dan status
blinking_speed = 1  # Kecepatan awal (1 detik)
alternating = False  # Status mode bergantian LED
max_speed_active = False  # Status apakah tombol "Max Speed" diaktifkan
max_speed_reached = False  # Status apakah kecepatan maksimum telah tercapai

# Fungsi untuk membuat LED berkedip dan beep dengan delay tertentu
def blink_leds(delay):
    # Kedipan dan beep untuk LED 1
    board.digital[led_pin_1].write(1)  # Menyalakan LED pertama
    board.digital[buzzer_pin].write(0.5)  # Suara beep
    time.sleep(delay)  # Tunggu sesuai delay
    board.digital[led_pin_1].write(0)  # Mematikan LED pertama
    board.digital[buzzer_pin].write(0)  # Mematikan beep
    time.sleep(delay)  # Delay sebelum LED kedua
    
    # Kedipan dan beep untuk LED 2
    board.digital[led_pin_2].write(1)  # Menyalakan LED kedua
    board.digital[buzzer_pin].write(0.5)  # Suara beep untuk LED kedua
    time.sleep(delay)  # Tunggu sesuai delay
    board.digital[led_pin_2].write(0)  # Mematikan LED kedua
    board.digital[buzzer_pin].write(0)  # Mematikan beep
    time.sleep(delay)  # Delay setelah LED kedua

# Fungsi untuk mode lambat atau cepat
def toggle_blinking_speed():
    global blinking_speed
    if blinking_speed == 1:
        blinking_speed = 0.3
        status_label.config(text="Speed: Fast")
    else:
        blinking_speed = 1
        status_label.config(text="Speed: Slow")

# Fungsi untuk mode bergantian LED
def alternate_led_blinking():
    global alternating
    alternating = not alternating
    if alternating:
        status_label.config(text="Mode: Alternating")
    else:
        status_label.config(text="Mode: Normal")

# Fungsi untuk mempercepat kedipan setiap 5 detik
def activate_max_speed():
    global max_speed_active
    max_speed_active = True
    status_label.config(text="Mode: Max Speed")
    root.after(5000, increase_speed)  # Mulai interval 5 detik pertama

# Fungsi untuk mengontrol tampilan
def control_leds():
    global blinking_speed, max_speed_active, max_speed_reached

    if max_speed_reached:
        # Jika kecepatan maksimum tercapai, beep terus menyala tanpa delay
        board.digital[led_pin_1].write(1)
        board.digital[led_pin_2].write(1)
        board.digital[buzzer_pin].write(0.5)  # Beep terus-menerus
    elif alternating:
        # Jika mode bergantian LED
        board.digital[led_pin_1].write(1)  # Menyalakan LED pertama
        board.digital[led_pin_2].write(0)  # Mematikan LED kedua
        board.digital[buzzer_pin].write(0.5)  # Suara beep dengan duty cycle 50%
        time.sleep(blinking_speed)  # Tunggu sesuai kecepatan kedipan
        board.digital[led_pin_1].write(0)  # Mematikan LED pertama
        board.digital[led_pin_2].write(1)  # Menyalakan LED kedua
        board.digital[buzzer_pin].write(0.5)  # Suara beep untuk LED kedua
        time.sleep(blinking_speed)  # Tunggu sesuai kecepatan kedipan
        board.digital[buzzer_pin].write(0)  # Matikan buzzer
    else:
        # Jika mode normal (kecepatan bergantung pada tombol)
        blink_leds(blinking_speed)

# Fungsi untuk mempercepat kedipan
def increase_speed():
    global blinking_speed, max_speed_active, max_speed_reached
    if max_speed_active and not max_speed_reached:
        if blinking_speed > 0.01:
            blinking_speed /= 2  # Percepat 2 kali lipat
            status_label.config(text=f"Speed: {blinking_speed:.2f} seconds")
            # Jadwalkan pemanggilan berikutnya setelah 5 detik
            root.after(5000, increase_speed)
        else:
            # Jika sudah mencapai kecepatan maksimum, set status max_speed_reached
            max_speed_reached = True
            max_speed_active = False  # Nonaktifkan max speed jika sudah di kecepatan maksimum

# GUI untuk mengontrol
root = tk.Tk()
root.title("LED Control")

# Tombol untuk mengubah kecepatan kedip
speed_button = tk.Button(root, text="Toggle Speed", command=toggle_blinking_speed)
speed_button.pack(pady=10)

# Tombol untuk mode bergantian LED
alternate_button = tk.Button(root, text="Alternate LEDs", command=alternate_led_blinking)
alternate_button.pack(pady=10)

# Tombol untuk mengaktifkan kecepatan maksimal
max_speed_button = tk.Button(root, text="Max Speed", command=activate_max_speed)
max_speed_button.pack(pady=10)

# Label status
status_label = tk.Label(root, text="Speed: Slow")
status_label.pack(pady=10)

# Loop utama untuk menjalankan GUI
def run_gui():
    control_leds()
    root.after(100, run_gui)  # Memanggil lagi setelah 100ms untuk update LED

# Mulai GUI
run_gui()
root.mainloop()

# Tutup koneksi ke board setelah GUI ditutup
board.exit()
