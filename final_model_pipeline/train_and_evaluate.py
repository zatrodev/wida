import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import torch
import torch.nn as nn
import torch.optim as optim
import torch.optim.lr_scheduler as lr_scheduler
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import StandardScaler
from sklearn.utils.class_weight import compute_class_weight
from torch.utils.data import DataLoader, Dataset


# ==========================================
# 1. THE UNIVARIATE LSTM MODEL
# ==========================================
class WIDASupervisedLSTM(nn.Module):
    def __init__(self, input_dim, hidden_dim, num_layers, num_classes):
        super(WIDASupervisedLSTM, self).__init__()
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        self.lstm = nn.LSTM(
            input_dim, hidden_dim, num_layers, batch_first=True, dropout=0.2
        )
        self.fc = nn.Linear(hidden_dim, num_classes)

    def forward(self, x):
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_dim).to(x.device)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_dim).to(x.device)
        out, _ = self.lstm(x, (h0, c0))
        out = self.fc(out[:, -1, :])
        return out


# ==========================================
# 2. MEMORY EFFICIENT DATASET CLASS
# ==========================================
class TimeSeriesDataset(Dataset):
    def __init__(self, X, y, seq_length):
        self.X = X
        self.y = y
        self.seq_length = seq_length

    def __len__(self):
        return len(self.X) - self.seq_length + 1

    def __getitem__(self, idx):
        x_seq = self.X[idx : idx + self.seq_length]

        # --- THE FIX: Majority Vote Labeling ---
        # Instead of np.max, we use the most frequent label in the window
        labels_in_window = self.y[idx : idx + self.seq_length]
        y_label = np.bincount(labels_in_window).argmax()
        # ---------------------------------------

        return torch.tensor(x_seq, dtype=torch.float32), torch.tensor(
            y_label, dtype=torch.long
        )


# ==========================================
# 3. DATA PREPARATION (TRAINING & VAL)
# ==========================================
def prepare_training_data(csv_file, seq_length=10, val_split=0.2):
    print(f"Loading training data from {csv_file}...")
    df = pd.read_csv(csv_file)

    df["peak_frequency"] = pd.to_numeric(df["peak_frequency"], errors="coerce")
    df["peak_frequency"] = df["peak_frequency"].interpolate(
        method="linear", limit_direction="both"
    )
    df["label"] = df["label"].ffill().bfill()

    feature_cols = ["peak_frequency"]
    X_raw = df[feature_cols].values
    y_raw = df["label"].values

    split_idx = int(len(X_raw) * (1 - val_split))
    X_train_raw, X_val_raw = X_raw[:split_idx], X_raw[split_idx:]
    y_train_raw, y_val_raw = y_raw[:split_idx], y_raw[split_idx:]

    # --- THE FIX: Absolute Physical Scaling (0 remains 0) ---
    X_train_scaled = X_train_raw / 100.0
    X_val_scaled = X_val_raw / 100.0
    # --------------------------------------------------------

    train_dataset = TimeSeriesDataset(X_train_scaled, y_train_raw, seq_length)
    val_dataset = TimeSeriesDataset(X_val_scaled, y_val_raw, seq_length)

    train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=64, shuffle=False)

    y_train_windows = np.array(
        [
            np.max(y_train_raw[i : i + seq_length])
            for i in range(len(y_train_raw) - seq_length)
        ]
    )

    return train_loader, val_loader, y_train_windows


# ==========================================
# 4. DATA PREPARATION (SHAKE TABLE TEST)
# ==========================================
def prepare_shaketable_data(csv_file, seq_length=10):
    print(f"Loading physical shake table data from {csv_file}...")
    df = pd.read_csv(csv_file)

    df["peak_frequency"] = pd.to_numeric(df["peak_frequency"], errors="coerce")
    df["peak_frequency"] = df["peak_frequency"].interpolate(
        method="linear", limit_direction="both"
    )
    df["label"] = df["label"].ffill().bfill()

    feature_cols = ["peak_frequency"]
    X_raw = df[feature_cols].values
    y_raw = df["label"].values

    # --- THE FIX: Absolute Physical Scaling ---
    X_scaled = X_raw / 100.0
    # ------------------------------------------

    test_dataset = TimeSeriesDataset(X_scaled, y_raw, seq_length)
    test_loader = DataLoader(test_dataset, batch_size=64, shuffle=False)

    y_test_windows = np.array(
        [np.max(y_raw[i : i + seq_length]) for i in range(len(y_raw) - seq_length)]
    )

    return test_loader, y_test_windows


# ==========================================
# 5. MASTER TRAINING & EVALUATION LOOP
# ==========================================
def main():
    INPUT_DIM = 1
    HIDDEN_DIM = 64
    NUM_LAYERS = 2
    NUM_CLASSES = 4
    SEQ_LENGTH = 10
    EPOCHS = 50
    LR = 0.001
    DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    TRAIN_CSV = "wida_calibrated_hybrid_data.csv"
    TEST_CSV = "phivolcs_shaketable_v2.csv"

    # Notice we removed 'scaler' from the returns here
    train_loader, val_loader, y_train_windows = prepare_training_data(
        TRAIN_CSV, seq_length=SEQ_LENGTH
    )
    test_loader, y_test_windows = prepare_shaketable_data(
        TEST_CSV, seq_length=SEQ_LENGTH
    )

    # --- THE FIX: Standard Balanced Class Weights (Removed Paranoia Multipliers) ---
    unique_classes = np.unique(y_train_windows)
    computed_weights = compute_class_weight(
        class_weight="balanced", classes=unique_classes, y=y_train_windows
    )
    full_weights = np.ones(NUM_CLASSES, dtype=np.float32)
    for i, cls in enumerate(unique_classes):
        full_weights[int(cls)] = computed_weights[i]

    class_weights_tensor = torch.tensor(full_weights, dtype=torch.float32).to(DEVICE)
    # -------------------------------------------------------------------------------

    # Init Model
    model = WIDASupervisedLSTM(INPUT_DIM, HIDDEN_DIM, NUM_LAYERS, NUM_CLASSES).to(
        DEVICE
    )
    criterion = nn.CrossEntropyLoss(weight=class_weights_tensor)
    optimizer = optim.Adam(model.parameters(), lr=LR, weight_decay=1e-5)
    scheduler = lr_scheduler.StepLR(optimizer, step_size=10, gamma=0.5)

    # Early Stopping Variables
    best_val_loss = float("inf")
    patience = 5
    patience_counter = 0

    print(f"\n--- Training Model on {DEVICE} ---")
    for epoch in range(EPOCHS):
        # Training Pass
        model.train()
        train_loss = 0
        for X_batch, y_batch in train_loader:
            X_batch, y_batch = X_batch.to(DEVICE), y_batch.to(DEVICE)

            optimizer.zero_grad()
            predictions = model(X_batch)
            loss = criterion(predictions, y_batch)
            loss.backward()

            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()
            train_loss += loss.item()

        avg_train_loss = train_loss / len(train_loader)

        # Validation Pass
        model.eval()
        val_loss = 0
        with torch.no_grad():
            for X_batch, y_batch in val_loader:
                X_batch, y_batch = X_batch.to(DEVICE), y_batch.to(DEVICE)
                predictions = model(X_batch)
                loss = criterion(predictions, y_batch)
                val_loss += loss.item()

        avg_val_loss = val_loss / len(val_loader)
        scheduler.step()

        print(
            f"Epoch [{epoch+1}/{EPOCHS}], Train Loss: {avg_train_loss:.4f}, Val Loss: {avg_val_loss:.4f}"
        )

        # Early Stopping Check
        if avg_val_loss < best_val_loss:
            best_val_loss = avg_val_loss
            patience_counter = 0
            # Automatically save the best model state
            torch.save(model.state_dict(), "wida_lstm_univariate.pth")
        else:
            patience_counter += 1
            if patience_counter >= patience:
                print(
                    f"\n[!] Early stopping triggered at epoch {epoch+1}. Restoring best weights."
                )
                break

    # Load the best weights before final evaluation
    model.load_state_dict(torch.load("wida_lstm_univariate.pth"))
    print(
        "\nProduction assets compiled and loaded: 'wida_lstm_univariate.pth' & 'wida_scaler_univariate.save'"
    )

    # Final Shake Table Evaluation
    print("\n--- Final Physical Hardware Validation (Shake Table v2) ---")
    model.eval()
    all_preds = []
    all_targets = []

    with torch.no_grad():
        for X_batch, y_batch in test_loader:
            X_batch = X_batch.to(DEVICE)
            outputs = model(X_batch)
            _, predicted = torch.max(outputs.data, 1)
            all_preds.extend(predicted.cpu().numpy())
            all_targets.extend(y_batch.cpu().numpy())

    present_classes = np.unique(all_targets)
    target_names_full = ["Normal (0)", "Minor (1)", "Moderate (2)", "Dangerous (3)"]
    target_names_present = [target_names_full[int(i)] for i in present_classes]

    print("\n=== Shake Table Classification Report ===")
    print(
        classification_report(
            all_targets,
            all_preds,
            labels=present_classes,
            target_names=target_names_present,
            zero_division=0,
        )
    )

    cm = confusion_matrix(all_targets, all_preds, labels=present_classes)
    plt.figure(figsize=(8, 6))
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=target_names_present,
        yticklabels=target_names_present,
    )
    plt.xlabel("Predicted Label")
    plt.ylabel("True Label")
    plt.title("WIDA LSTM Performance (Physical Shake Table Validation)")
    plt.show()


if __name__ == "__main__":
    main()
