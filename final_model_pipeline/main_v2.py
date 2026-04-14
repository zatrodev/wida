import csv
import os
import socket
import time
from datetime import datetime

import numpy as np
import requests
import torch
import torch.nn as nn
from dotenv import load_dotenv
from scipy.fft import fft, fftfreq
from supabase import Client, create_client

try:
    import smbus2 as smbus
except ImportError:
    import smbus

# ── DESCRIPTION ───────────────────────────────────────────────────────
# This script uses the original FFT script.

# ── LCD2004 CONFIG ─────────────────────────────────────────────────────
LCD_ADDR = 0x27
LCD_WIDTH = 20
LCD_CHR = 1
LCD_CMD = 0
LCD_LINE_1 = 0x80
LCD_LINE_2 = 0xC0
LCD_LINE_3 = 0x94
LCD_LINE_4 = 0xD4
LCD_BACKLIGHT = 0x08
ENABLE = 0b00000100


def lcd_init():
    try:
        lcd_byte(0x33, LCD_CMD)
        lcd_byte(0x32, LCD_CMD)
        lcd_byte(0x06, LCD_CMD)
        lcd_byte(0x0C, LCD_CMD)
        lcd_byte(0x28, LCD_CMD)
        lcd_byte(0x01, LCD_CMD)
        time.sleep(0.005)
    except:
        pass


def lcd_byte(bits, mode):
    try:
        bits_high = mode | (bits & 0xF0) | LCD_BACKLIGHT
        bits_low = mode | ((bits << 4) & 0xF0) | LCD_BACKLIGHT
        bus.write_byte(LCD_ADDR, bits_high)
        lcd_toggle_enable(bits_high)
        bus.write_byte(LCD_ADDR, bits_low)
        lcd_toggle_enable(bits_low)
    except:
        pass


def lcd_toggle_enable(bits):
    time.sleep(0.0005)
    try:
        bus.write_byte(LCD_ADDR, (bits | ENABLE))
        time.sleep(0.0005)
        bus.write_byte(LCD_ADDR, (bits & ~ENABLE))
        time.sleep(0.0005)
    except:
        pass


def lcd_string(message, line):
    try:
        message = message.ljust(LCD_WIDTH, " ")
        lcd_byte(line, LCD_CMD)
        for i in range(LCD_WIDTH):
            lcd_byte(ord(message[i]), LCD_CHR)
    except:
        pass


def lcd_display(freq, severity, temp, timestamp):
    try:
        lcd_string(f"Freq: {freq:.2f} Hz", LCD_LINE_1)
        lcd_string(f"Severity: {severity}", LCD_LINE_2)
        lcd_string(f"Temp: {temp:.1f}C", LCD_LINE_3)
        lcd_string(timestamp[:19], LCD_LINE_4)
    except:
        pass


# ── SUPABASE CONFIG ─────────────────────────────────────────────────────
load_dotenv()
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except:
    supabase = None

# ── TELEGRAM CONFIG ────────────────────────────────────────────────────
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")


# ── MPU6050 CONFIG ─────────────────────────────────────────────────────
def init_mpu6050():
    try:
        bus = smbus.SMBus(1)
        addr = 0x68
        bus.write_byte_data(addr, 0x6B, 0)
        return bus, addr
    except:
        return None, None


bus, addr = init_mpu6050()


def read_word(reg):
    if bus is None:
        return 0
    try:
        h = bus.read_byte_data(addr, reg)
        l = bus.read_byte_data(addr, reg + 1)
        val = (h << 8) + l
        return val - 65536 if val > 32767 else val
    except:
        return 0


def read_temperature():
    if bus is None:
        return 30.0
    try:
        h = bus.read_byte_data(addr, 0x41)
        l = bus.read_byte_data(addr, 0x42)
        val = (h << 8) + l
        val = val - 65536 if val > 32767 else val
        return round((val / 340.0) + 36.53, 2)
    except:
        return 0.0


# ── CONSTANTS ─────────────────────────────────────────────────────────
Fs = 500
N = 2500
SEQ_LENGTH = 10
DEVICE_ID = "wida-01"
OFFLINE_FILE = "pending_alerts.csv"

# ── GPIOZero SOCKET CLIENT ─────────────────────────────────────────────
SOCKET_PATH = "/tmp/gpiozero_socket"


def gpio_command(cmd):
    try:
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client.connect(SOCKET_PATH)
        client.send(cmd.encode())
        response = client.recv(1024).decode()
        client.close()
        return response
    except Exception as e:
        return f"ERROR: {e}"


def trigger_alarm(severity):
    # NOTE: Only turn on the physical alarm for Moderate or Dangerous
    if severity in ["moderate", "dangerous"]:
        gpio_command("ON")
    else:
        gpio_command("OFF")


# ── MODEL ─────────────────────────────────────────────────────────────
class WIDASupervisedLSTM(nn.Module):
    def __init__(self, input_dim, hidden_dim, num_layers, num_classes):
        super().__init__()
        # Added dropout=0.2 to match training architecture
        self.lstm = nn.LSTM(
            input_dim, hidden_dim, num_layers, batch_first=True, dropout=0.2
        )
        self.fc = nn.Linear(hidden_dim, num_classes)

    def forward(self, x):
        out, _ = self.lstm(x)
        return self.fc(out[:, -1, :])


device = torch.device("cpu")
# Changed input dimension from 4 to 1
model = WIDASupervisedLSTM(1, 64, 2, 4)
try:
    # Pointing to the new univariate weights
    model.load_state_dict(
        torch.load(
            "model/wida_lstm_univariate.pth", map_location=device, weights_only=True
        )
    )
    model.eval()
except Exception as e:
    print(f"Model load error: {e}")

SEVERITY_LABELS = {0: "normal", 1: "minor", 2: "moderate", 3: "dangerous"}


# ── FFT FUNCTION ───────────────────────────────────────────────────────
def get_peak_freq(signal, Fs, min_std=0.01, min_freq=0.5, max_freq=200):
    if len(signal) == 0:
        return 0
    signal = signal - np.mean(signal)
    if np.std(signal) < min_std:
        return 0
    windowed = signal * np.hanning(len(signal))
    yf = np.abs(fft(windowed))
    xf = fftfreq(len(signal), 1 / Fs)
    half = len(yf) // 2
    yf = yf[:half]
    xf = xf[:half]
    valid = (xf >= min_freq) & (xf <= max_freq)
    if not np.any(valid):
        return 0
    yf_band = yf[valid]
    xf_band = xf[valid]
    peak_idx = np.argmax(yf_band)
    peak_amp = yf_band[peak_idx]
    if peak_amp < min_std:
        return 0
    return xf_band[peak_idx]


# ── TELEGRAM ALERT ─────────────────────────────────────────────────────
def send_telegram_alert(severity, confidence, freq_hz, fx, fy, fz, temp_c, timestamp):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return
    emoji = "⚠️" if severity != "normal" else ""
    message = (
        f"{emoji} *WIDA ALERT* {emoji}\n"
        f"*Severity:* `{severity}`\n"
        f"*Confidence:* `{confidence:.2f}`\n"
        f"Freq: `{freq_hz:.2f}Hz`\n"
        f"X: `{fx:.2f}Hz`, Y: `{fy:.2f}Hz`, Z: `{fz:.2f}Hz`\n"
        f"Temp: `{temp_c}C`\n"
        f"Time: `{timestamp}`\n"
        f"Device: `{DEVICE_ID}`"
    )
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": message,
                "parse_mode": "Markdown",
            },
            timeout=10,
        )
    except:
        pass


# ── OFFLINE STORAGE ────────────────────────────────────────────────────
if not os.path.isfile(OFFLINE_FILE):
    with open(OFFLINE_FILE, "w", newline="") as f:
        csv.writer(f).writerow(
            [
                "timestamp",
                "frequency_hz",
                "raw_x",
                "raw_y",
                "raw_z",
                "severity",
                "confidence_score",
                "fft_latency_ms",
                "sensor_temperature_c",
            ]
        )


def save_offline(data):
    with open(OFFLINE_FILE, "a", newline="") as f:
        csv.writer(f).writerow(
            [
                data["recorded_at"],
                data["frequency_hz"],
                data["raw_x"],
                data["raw_y"],
                data["raw_z"],
                data["severity"],
                data["confidence_score"],
                data["fft_latency_ms"],
                data["sensor_temperature_c"],
            ]
        )


def resend_offline():
    if not supabase:
        return
    try:
        with open(OFFLINE_FILE, "r") as f:
            rows = list(csv.DictReader(f))
        if not rows:
            return
        payload = []
        for r in rows:
            payload.append(
                {
                    "device_id": DEVICE_ID,
                    "recorded_at": r["timestamp"],
                    "frequency_hz": float(r["frequency_hz"]),
                    "raw_x": float(r["raw_x"]),
                    "raw_y": float(r["raw_y"]),
                    "raw_z": float(r["raw_z"]),
                    "severity": r["severity"],
                    "confidence_score": float(r["confidence_score"]),
                    "fft_latency_ms": float(r.get("fft_latency_ms", 0)),
                    "sensor_temperature_c": float(r.get("sensor_temperature_c", 0)),
                }
            )
        supabase.table("alerts").insert(payload).execute()
        with open(OFFLINE_FILE, "w", newline="") as f:
            csv.writer(f).writerow(
                [
                    "timestamp",
                    "frequency_hz",
                    "raw_x",
                    "raw_y",
                    "raw_z",
                    "severity",
                    "confidence_score",
                    "fft_latency_ms",
                    "sensor_temperature_c",
                ]
            )
    except:
        pass


# ── MAIN LOOP ─────────────────────────────────────────────────────────
feature_buffer = []
lcd_init()
prev_nf = 0
print("Monitoring started...")

while True:
    x, y, z = [], [], []
    loop_start = time.time()

    # ---------------- READ SENSOR ----------------
    read_start = time.perf_counter()
    for _ in range(N):
        x.append(read_word(0x3B) / 16384.0)
        y.append(read_word(0x3D) / 16384.0)
        z.append(read_word(0x3F) / 16384.0)
        # if bus:
        #     time.sleep(1 / Fs)
    read_end = time.perf_counter()

    x = np.array(x)
    y = np.array(y)
    z = np.array(z)
    mag = np.sqrt(x**2 + y**2 + z**2)

    # ---------------- FFT ----------------
    actual_Fs = N / (read_end - read_start)

    fft_start = time.perf_counter()
    nf_raw = get_peak_freq(mag, actual_Fs)
    fft_latency = (time.perf_counter() - fft_start) * 1000

    # Smooth frequency
    alpha = 0.5
    nf = alpha * prev_nf + (1 - alpha) * nf_raw
    prev_nf = nf

    # ---------------- SENSOR DATA ----------------
    temp_c = read_temperature()
    iso_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ---------------- FEATURE BUFFER ----------------
    # Apply Absolute Physical Scaling directly to the smoothed frequency
    scaled_freq = nf / 100.0

    # Univariate model only takes 1 feature now
    feature_buffer.append([scaled_freq])
    if len(feature_buffer) > SEQ_LENGTH:
        feature_buffer.pop(0)

    # ---------------- SEVERITY PREDICTION ----------------
    severity_str = "normal"
    # Removed the 'and scaler' condition since we dropped sklearn
    if len(feature_buffer) == SEQ_LENGTH:
        # Buffer is already scaled, convert directly to tensor
        tensor = torch.tensor(feature_buffer, dtype=torch.float32).unsqueeze(0)
        with torch.no_grad():
            out = model(tensor)
            probs = torch.softmax(out, dim=1)[0]
            _, pred = torch.max(probs, 0)
            severity_str = SEVERITY_LABELS[pred.item()]

    # ---------------- LCD DISPLAY ----------------
    lcd_display(nf, severity_str, temp_c, iso_ts)

    # ---------------- GPIO ALARM ----------------
    trigger_alarm(severity_str)
    gpio_status = gpio_command("STATUS")

    # ---------------- TERMINAL LOG ----------------
    print(
        f"{iso_ts} | {nf:.2f}Hz | {severity_str} | {temp_c}C | FFT {fft_latency:.2f}ms | GPIO17: {gpio_status}"
    )

    # ---------------- DATA PAYLOAD ----------------
    data_payload = {
        "device_id": DEVICE_ID,
        "recorded_at": iso_ts,
        "frequency_hz": round(nf, 3),
        "raw_x": round(np.max(np.abs(x)), 3),
        "raw_y": round(np.max(np.abs(y)), 3),
        "raw_z": round(np.max(np.abs(z)), 3),
        "severity": severity_str,
        "confidence_score": float(probs[pred].item()) if "probs" in locals() else 0.0,
        "fft_latency_ms": round(fft_latency, 2),
        "sensor_temperature_c": temp_c,
    }

    # ---------------- UPLOAD TO SUPABASE ----------------
    if supabase:
        resend_offline()
        try:
            supabase.table("alerts").insert(data_payload).execute()
            # Only alert phone for Moderate and Dangerous
            if severity_str in ["moderate", "dangerous"]:
                send_telegram_alert(
                    severity_str,
                    data_payload["confidence_score"],
                    nf,
                    nf_raw,
                    nf_raw,
                    nf_raw,
                    temp_c,
                    iso_ts,
                )
        except:
            save_offline(data_payload)
    else:
        save_offline(data_payload)

    # ---------------- LOOP TIMING ----------------
    elapsed = time.time() - loop_start
    sleep_time = max(0, N / Fs - elapsed)
    time.sleep(sleep_time)
