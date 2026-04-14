# WIDA Earthquake Model Pipeline

This directory contains the finalized scripts and assets used to construct, evaluate, and deploy the WIDA Supervised LSTM univariate earthquake detection model from start to finish.

## Pipeline Steps

### 1. Data Merging and Preprocessing: `merge_xlsx.py`
This script parses the raw earthquake catalogues obtained from the DOST-PHIVOLCS (specifically for Marikina and Rizal vicinities). It aggregates and unifies the timestamps across varying source data structures, aligns the relevant timezone offsets (GMT to PST), removes invalid or duplicate events, and prepares a unified chronological timeline outputting `phivolcs_master_catalogue.csv`.

### 2. Synthetic Data Generation: `generate_data.py`
Using the `phivolcs_master_catalogue.csv`, this scripts maps real historical earthquake timestamps and magnitude labels and structures them into continuous 15-minute sequences to simulate real-world IoT sensor outputs over time. It relies on empirical calibration thresholds (25Hz to 100Hz vibration peaks based on corresponding Richter magnitude scaling). It integrates the simulated earthquake windows against standard machine wind-downs and isolation pad noise thresholds to output an extensive, robust, continuous label-and-frequency table as `wida_calibrated_hybrid_data.csv`.

### 3. Model Training & Evaluation: `train_and_evaluate.py`
This core training module loads the simulated hybrid dataset along with validation data recorded directly from physical shake-table evaluations (`phivolcs_shaketable_v2.csv`). The script extracts temporal sequences using a memory-efficient `TimeSeriesDataset` implementation, and converts peak frequency labels via sequential window learning with _majority vote labeling_. After properly scaling inputs, calculating Class Weights parity, and running training passes optimized with Learning Rate Schedulers and automatic Early Stopping, it saves out the final PyTorch tensor weights into `wida_lstm_univariate.pth`.

### 4. Production Inference Component: `main_v2.py`
The final deployment inference file optimized for Raspberry Pi with raw MPU6050 accelerometer sensors. This continuously processes hardware streams using Fast Fourier Transform to map raw mechanical waveforms into frequency data. It immediately feeds overlapping data windows directly into the trained Univariate LSTM inference engine locally. Based on real-time classification, it handles GPIO physical pin statuses for alarming, updates a local LCD 2004 20x4 display, logs events to Supabase offline-ready pools, and shoots an automated SMS payload via Telegram APIs.

---

## Assets Include:
- `wida_lstm_univariate.pth`: Final trained PyTorch model architecture weights.
