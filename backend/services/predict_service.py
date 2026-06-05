import joblib
import numpy as np
import pandas as pd


def predict(model_path, features, inputs):
    bundle   = joblib.load(model_path)
    pipeline = bundle["pipeline"]
    classes  = bundle["classes"]
    le       = bundle.get("label_encoder")

    # Build input dataframe in correct column order
    row = {feat: float(inputs.get(feat, 0)) for feat in features}
    X   = pd.DataFrame([row], columns=features)

    pred_idx   = pipeline.predict(X)[0]
    proba      = pipeline.predict_proba(X)[0].tolist()

    # Decode label
    if le is not None:
        prediction = le.inverse_transform([pred_idx])[0]
    else:
        prediction = str(pred_idx)

    probabilities = {str(cls): round(float(p), 6) for cls, p in zip(classes, proba)}

    return {
        "prediction":    prediction,
        "probabilities": probabilities,
        "classes":       [str(c) for c in classes],
    }
