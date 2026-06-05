import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, confusion_matrix, roc_curve, auc,
    classification_report
)
from sklearn.preprocessing import label_binarize


def evaluate_model(model_path, df, features, target):
    bundle   = joblib.load(model_path)
    pipeline = bundle["pipeline"]
    classes  = bundle["classes"]
    le       = bundle.get("label_encoder")

    X = df[features].copy()
    y = df[target].copy()

    if le is not None:
        y = le.transform(y)

    y_pred  = pipeline.predict(X)
    y_proba = pipeline.predict_proba(X)

    acc  = float(accuracy_score(y, y_pred))
    prec = float(precision_score(y, y_pred, average="weighted", zero_division=0))
    rec  = float(recall_score(y, y_pred, average="weighted", zero_division=0))
    f1   = float(f1_score(y, y_pred, average="weighted", zero_division=0))

    cm = confusion_matrix(y, y_pred).tolist()

    report = classification_report(
        y, y_pred,
        target_names=[str(c) for c in classes],
        output_dict=True,
        zero_division=0
    )

    # ROC — one-vs-rest for multiclass
    n_classes = len(classes)
    roc_data  = {}
    if n_classes == 2:
        fpr, tpr, _ = roc_curve(y, y_proba[:, 1])
        roc_data["binary"] = {
            "fpr": fpr.tolist(),
            "tpr": tpr.tolist(),
            "auc": float(auc(fpr, tpr)),
        }
    else:
        y_bin = label_binarize(y, classes=list(range(n_classes)))
        for i, cls in enumerate(classes):
            fpr, tpr, _ = roc_curve(y_bin[:, i], y_proba[:, i])
            roc_data[str(cls)] = {
                "fpr": fpr.tolist(),
                "tpr": tpr.tolist(),
                "auc": float(auc(fpr, tpr)),
            }

    return {
        "accuracy":          acc,
        "precision":         prec,
        "recall":            rec,
        "f1_score":          f1,
        "confusion_matrix":  cm,
        "classes":           [str(c) for c in classes],
        "roc":               roc_data,
        "classification_report": report,
    }
