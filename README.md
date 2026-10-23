# KOLOS: listening for pests inside stored grain

KOLOS is a low-cost acoustic probe that listens for insect activity inside stored grain. We built it for grain warehouses in Orenburg, Russia.

**Project page:** https://k5nty.github.io/Kolos/

## What's here

| Path | What it is |
|---|---|
| `index.html`, `images/` | The project web page |
| `docs/KOLOS_research_paper_RU.pdf` | Full research paper (Russian, 31 pages) |
| `code/firmware_v1/` | ESP32 firmware v1: amplitude in 100 ms windows |
| `code/firmware_v2/` | ESP32 firmware v2: calibration, event counting, Normal / Attention / Alert status |
| `code/kolos_log.py` | Records the probe's serial output into labelled files |
| `code/kolos_ai.py` | Random Forest classifier: training and live recognition |

## Hardware

1 m aluminium tube, 3D-printed PLA chamber, nose cone and electronics box (Autodesk Fusion 360, OrcaSlicer, Creality K1C), MAX9814 microphone, ESP32. Parts cost about 1,000–1,200 RUB.

## Classifier

```bash
pip install pyserial scikit-learn matplotlib joblib numpy
python3 code/kolos_ai.py train          # trains on logs/*.txt
python3 code/kolos_ai.py live PORT      # live recognition from the board
```

93.4% accuracy on held-out data (4 classes: silence, single knocks, repeated impulses, airborne noise).

Authors: Vladimir Nazarov, Andrey Makarovsky, Amir Safin, Letovo School, Moscow.
Website: Vladimir Nazarov.
