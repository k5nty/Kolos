#!/usr/bin/env python3
"""КОЛОС: классификатор акустических сигналов макета (машинное обучение).

Обучение на записях из папки logs (имя файла начинается с класса):
    python3 kolos_ai.py train
Распознавание в реальном времени с платы:
    python3 kolos_ai.py live ПОРТ
"""
import glob
import os
import re
import sys
from collections import deque

import numpy as np

CLASSES = {"fon": "тишина", "stuk": "одиночные стуки", "metronom": "повторяющиеся импульсы", "shum": "шум в воздухе"}
WIN, STEP = 20, 5        # окно из 20 измерений амплитуды, сдвиг 5
AMP_RE = re.compile(r"AMP(?:LITUDE)?:\s*(\d+)")


def features(a):
    a = np.asarray(a, float)
    base = np.median(a) + 1e-9
    d = a - a.mean()
    ac = [np.corrcoef(d[:-k], d[k:])[0, 1] if d.std() > 0 else 0 for k in (1, 2, 3, 4)]
    peaks = np.sum((a[1:-1] > a[:-2]) & (a[1:-1] > a[2:]) & (a[1:-1] > 1.5 * base))
    return [a.mean(), a.std(), a.max(), a.min(), np.percentile(a, 90), a.max() / base,
            np.mean(a > 1.5 * base), peaks, *np.nan_to_num(ac)]


def load():
    X, y = {"train": [], "test": []}, {"train": [], "test": []}
    for path in sorted(glob.glob("logs/*.txt")):
        name = os.path.basename(path).split("_")[0]
        if name not in CLASSES:
            continue
        amps = [int(m.group(1)) for line in open(path) if (m := AMP_RE.search(line))]
        wins = [amps[i:i + WIN] for i in range(0, len(amps) - WIN + 1, STEP)]
        cut = int(len(wins) * 0.7)  # первые 70% записи на обучение, последние 30% на проверку
        for part, ws in (("train", wins[:cut]), ("test", wins[cut + WIN // STEP:])):
            X[part] += [features(w) for w in ws]
            y[part] += [name] * len(ws)
    return X, y


def train():
    from joblib import dump
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import ConfusionMatrixDisplay, accuracy_score, classification_report
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    X, y = load()
    print("окон для обучения:", len(y["train"]), " для проверки:", len(y["test"]))
    model = RandomForestClassifier(n_estimators=200, random_state=0).fit(X["train"], y["train"])
    pred = model.predict(X["test"])
    print(f"точность на проверочных данных: {accuracy_score(y['test'], pred) * 100:.1f}%")
    print(classification_report(y["test"], pred, digits=3))
    labels = [c for c in CLASSES if c in set(y["test"])]
    ConfusionMatrixDisplay.from_predictions(y["test"], pred, labels=labels,
                                            display_labels=[CLASSES[c] for c in labels],
                                            xticks_rotation=30, cmap="Blues", colorbar=False)
    plt.title("Матрица ошибок классификатора «КОЛОС»")
    plt.tight_layout()
    plt.savefig("kolos_ai_matrix.png", dpi=200)
    dump(model, "kolos_ai_model.joblib")
    print("сохранено: kolos_ai_model.joblib, kolos_ai_matrix.png")


def live(port):
    import serial
    from joblib import load as jload
    model = jload("kolos_ai_model.joblib")
    ser = serial.Serial(port, 115200, timeout=1)
    buf, n = deque(maxlen=WIN), 0
    print("Распознавание запущено, Ctrl+C для остановки.")
    try:
        while True:
            m = AMP_RE.search(ser.readline().decode("utf-8", "replace"))
            if not m:
                continue
            buf.append(int(m.group(1)))
            n += 1
            if len(buf) == WIN and n % STEP == 0:
                proba = model.predict_proba([features(buf)])[0]
                k = int(np.argmax(proba))
                print(f"{CLASSES[model.classes_[k]]:>24}  уверенность {proba[k] * 100:.0f}%")
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    if sys.argv[1:2] == ["train"]:
        train()
    elif sys.argv[1:2] == ["live"] and len(sys.argv) > 2:
        live(sys.argv[2])
    else:
        print(__doc__)
