# main.py
# ESP32-C3 Wi-Fi Spotify Controller (OLED + Buttons + Encoder)
# Target: Seeed Studio XIAO ESP32-C3

import time
import board
import digitalio
import wifi
import socketpool
import adafruit_requests
import busio
from rotaryio import IncrementalEncoder
import adafruit_ssd1306

# =========================
# USER CONFIG (FILLED IN)
# =========================

WIFI_SSID = "JLJBW"
WIFI_PASSWORD = "Wilsonfam1428!"

# ---- PIN MAP ----
BUTTON_PINS = [
    board.GP2,
    board.GP3,
    board.GP4,
    board.GP5,
    board.GP6,
    board.GP7,
    board.GP8,
    board.GP9,
]

ENC_A = board.GP8
ENC_B = board.GP9
ENC_SW = board.GP10

I2C_SCL = board.GP21
I2C_SDA = board.GP20

# =========================
# SETUP
# =========================

# Buttons
buttons = []
for p in BUTTON_PINS:
    b = digitalio.DigitalInOut(p)
    b.direction = digitalio.Direction.INPUT
    b.pull = digitalio.Pull.UP
    buttons.append(b)

# Encoder
encoder = IncrementalEncoder(ENC_A, ENC_B)
last_position = encoder.position

enc_sw = digitalio.DigitalInOut(ENC_SW)
enc_sw.direction = digitalio.Direction.INPUT
enc_sw.pull = digitalio.Pull.UP

# OLED
i2c = busio.I2C(I2C_SCL, I2C_SDA)
oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)
oled.fill(0)
oled.text("Spotify Controller", 0, 0, 1)
oled.show()

# Wi-Fi
oled.text("WiFi...", 0, 12, 1)
oled.show()
wifi.radio.connect(WIFI_SSID, WIFI_PASSWORD)
oled.text("Connected", 0, 22, 1)
oled.show()

pool = socketpool.SocketPool(wifi.radio)
requests = adafruit_requests.Session(pool, ssl_context=wifi.radio.ssl_context)

# =========================
# SPOTIFY PLACEHOLDERS
# =========================

def oled_status(msg):
    oled.fill_rect(0, 40, 128, 24, 0)
    oled.text(msg, 0, 40, 1)
    oled.show()

def spotify_play_pause():
    oled_status("Play/Pause")

def spotify_next():
    oled_status("Next")

def spotify_prev():
    oled_status("Prev")

def spotify_vol_up():
    oled_status("Vol +")

def spotify_vol_down():
    oled_status("Vol -")

# =========================
# MAIN LOOP
# =========================

last_btn_states = [b.value for b in buttons]

while True:
    # Buttons
    for i, b in enumerate(buttons):
        if last_btn_states[i] and not b.value:
            if i == 0:
                spotify_play_pause()
            elif i == 1:
                spotify_next()
            elif i == 2:
                spotify_prev()
        last_btn_states[i] = b.value

    # Encoder rotation
    pos = encoder.position
    if pos != last_position:
        if pos > last_position:
            spotify_vol_up()
        else:
            spotify_vol_down()
        last_position = pos

    # Encoder press
    if not enc_sw.value:
        spotify_play_pause()
        time.sleep(0.3)

    time.sleep(0.01)
