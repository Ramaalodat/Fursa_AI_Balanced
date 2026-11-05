"""Reproducible reporting from the saved Fursa AI artifacts.

These results describe the saved test split, which was reviewed during
project development. They are not independent external validation.
"""
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score, balanced_accuracy_score, confusion_matrix,
    f1_score, recall_score, roc_auc_score,
)


def evaluate_saved_split(root_dir: str, threshold: float) -> dict:
    root = Path(root_dir)
    output = root / "milestone3_outputs"
    x = pd.read_csv(output / "X_test.csv")
    y = pd.read_csv(output / "y_test.csv").iloc[:, 0]
    model = joblib.load(output / "best_placement_model_monotonic_english.pkl")
    p = model.predict_proba(x)[:, list(model.classes_).index(1)]
    predicted = (p >= threshold).astype(int)
    recalls = recall_score(y, predicted, labels=[0, 1], average=None, zero_division=0)
    return {
        "samples": len(x),
        "accuracy": float(accuracy_score(y, predicted)),
        "balanced_accuracy": float(balanced_accuracy_score(y, predicted)),
        "macro_f1": float(f1_score(y, predicted, average="macro")),
        "roc_auc": float(roc_auc_score(y, p)),
        "cm": confusion_matrix(y, predicted, labels=[0, 1]).tolist(),
        "recall_not_placed": float(recalls[0]),
        "recall_placed": float(recalls[1]),
        "threshold": threshold,
    }
