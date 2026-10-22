#!/usr/bin/env python3
"""Запись данных прототипа KOLOS в файл.

Установка (один раз):  pip3 install --user pyserial
Запуск:  python3 kolos_log.py ПОРТ ИМЯ_ОПЫТА
         например: python3 kolos_log.py /dev/cu.usbserial-5C2E0074771 T2_tishina
Во время записи: пустой Enter — «воздействие вкл/выкл», текст + Enter — метка условия.
Остановка: Ctrl+C. Файл сохраняется в папку logs.
"""
import os
import sys
import threading
import time
from datetime import datetime

import serial

port, name = sys.argv[1], sys.argv[2]
state = {"stim": 0, "label": ""}


def keys():
    for line in sys.stdin:
        if line.strip():
            state["label"] = line.strip()
        else:
            state["stim"] ^= 1
        print(f">>> метка: {state['label'] or '—'}, воздействие: {'ВКЛ' if state['stim'] else 'выкл'}")


threading.Thread(target=keys, daemon=True).start()
ser = serial.Serial(port, 115200, timeout=1)
try:  # перезапуск ESP32, чтобы запись началась с калибровки
    ser.dtr, ser.rts = False, True
    time.sleep(0.1)
    ser.rts = False
except OSError:
    print("Нажмите кнопку EN на плате, чтобы она перезапустилась.")

os.makedirs("logs", exist_ok=True)
path = f"logs/{name}_{datetime.now():%Y%m%d_%H%M%S}.txt"
t0 = time.time()
print(f"Запись в {path}. Первые 10 с не трогайте зонд. Остановка — Ctrl+C.")
with open(path, "w") as f:
    try:
        while True:
            line = ser.readline().decode("utf-8", "replace").strip()
            if line:
                f.write(f"{time.time() - t0:.2f}\t{state['stim']}\t{state['label']}\t{line}\n")
                f.flush()
                print(line)
    except KeyboardInterrupt:
        pass
print(f"Сохранено: {path}")
