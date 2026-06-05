import os
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.pipeline import Pipeline


def train_model(df, features, target, test_size, max_iter, model_name, model_dir):
    X = df[features].copy()
    y = df[target].copy()

    # Encode target if categorical
    le = None
    if y.dtype == object or str(y.dtype) == "category":
        le = LabelEncoder()
        y = le.fit_transform(y)
        classes = le.classes_.tolist()
    else:
        classes = sorted(y.unique().tolist())

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=42, stratify=y
    )

    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("clf",    LogisticRegression(max_iter=max_iter, random_state=42))
    ])
    pipeline.fit(X_train, y_train)

    train_acc = float(pipeline.score(X_train, y_train))
    test_acc  = float(pipeline.score(X_test,  y_test))

    # Coefficients from the LR step
    clf        = pipeline.named_steps["clf"]
    coef_list  = []
    for i, cls in enumerate(clf.classes_):
        label = classes[cls] if le else str(cls)
        for j, feat in enumerate(features):
            coef_list.append({
                "class":    label,
                "feature":  feat,
                "coef":     round(float(clf.coef_[i][j]), 6),
            })
    intercepts = {
        (classes[c] if le else str(c)): round(float(v), 6)
        for c, v in zip(clf.classes_, clf.intercept_)
    }

    # Save model bundle
    bundle = {
        "pipeline": pipeline,
        "classes":  classes,
        "features": features,
        "target":   target,
        "label_encoder": le,
    }
    model_path = os.path.join(model_dir, model_name + ".joblib")
    joblib.dump(bundle, model_path)

    return {
        "model_name":     model_name,
        "model_path":     model_path,
        "classes":        classes,
        "train_accuracy": train_acc,
        "test_accuracy":  test_acc,
        "train_samples":  int(len(X_train)),
        "test_samples":   int(len(X_test)),
        "coefficients":   coef_list,
        "intercepts":     intercepts,
        "features":       features,
        "target":         target,
    }
