import joblib
import pandas as pd
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, confusion_matrix, roc_curve, auc,
    classification_report
)
from sklearn.preprocessing import label_binarize


def evaluate_model(model_path, df, features, target):
    bundle = joblib.load(model_path)
    pipeline = bundle["pipeline"]
    classes = bundle["classes"]
    le = bundle.get("label_encoder")
    preprocessing_version = bundle.get("preprocessing_version", 1)

    # Drop rows where target is NaN
    df = df.dropna(subset=[target]).copy()

    X = df[features].copy()
    
    if preprocessing_version == 1:
        for col in X.columns:
            if X[col].dtype == object:
                X[col] = X[col].str.replace(',', '.', regex=False)
            X[col] = pd.to_numeric(X[col], errors='coerce').fillna(0.0)
    else:
        for col in X.columns:
            if X[col].dtype == object:
                cleaned = X[col].astype(str).str.replace(',', '.', regex=False)
                X[col] = pd.to_numeric(cleaned, errors='ignore')
                if X[col].dtype == object:
                    X[col] = X[col].astype(str)

    y = df[target].copy()

    # Discretize continuous targets ONLY if the model was trained with it
    from sklearn.utils.multiclass import type_of_target
    if le is not None and type_of_target(y) == 'continuous':
        try:
            y = pd.qcut(y, q=3, labels=["Low", "Medium", "High"])
        except ValueError:
            y = pd.cut(y, bins=3, labels=["Low", "Medium", "High"])

    if le is not None:
        y = le.transform(y)

    y_pred = pipeline.predict(X)
    y_proba = pipeline.predict_proba(X)

    y_classes = list(range(len(classes))) if le is not None else classes

    acc = float(accuracy_score(y, y_pred))
    prec = float(precision_score(y, y_pred, average="weighted", zero_division=0))
    rec = float(recall_score(y, y_pred, average="weighted", zero_division=0))
    f1 = float(f1_score(y, y_pred, average="weighted", zero_division=0))

    cm = confusion_matrix(y, y_pred, labels=y_classes).tolist()

    report = classification_report(
        y, y_pred,
        labels=y_classes,
        target_names=[str(c) for c in classes],
        output_dict=True,
        zero_division=0
    )

    # ROC — one-vs-rest for multiclass
    pipeline_classes = pipeline.classes_
    n_classes_pipeline = len(pipeline_classes)
    roc_data = {}
    if n_classes_pipeline == 2:
        pos_class = pipeline_classes[1]
        fpr, tpr, _ = roc_curve(y, y_proba[:, 1], pos_label=pos_class)
        roc_data["binary"] = {
            "fpr": fpr.tolist(),
            "tpr": tpr.tolist(),
            "auc": float(auc(fpr, tpr)),
        }
    else:
        y_bin = label_binarize(y, classes=pipeline_classes)
        for i, p_cls in enumerate(pipeline_classes):
            fpr, tpr, _ = roc_curve(y_bin[:, i], y_proba[:, i])
            cls_name = str(classes[int(p_cls)]) if le is not None else str(p_cls)
            roc_data[cls_name] = {
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
