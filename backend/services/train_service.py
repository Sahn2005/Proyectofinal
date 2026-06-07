import os
import pandas as pd
import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.pipeline import Pipeline


def train_model(df, features, target, test_size, max_iter, model_name, model_dir):
    # Drop rows where target is NaN
    df = df.dropna(subset=[target]).copy()

    X = df[features].copy()
    for col in X.columns:
        if X[col].dtype == object:
            cleaned = X[col].astype(str).str.replace(',', '.', regex=False)
            X[col] = pd.to_numeric(cleaned, errors='ignore')
            if X[col].dtype == object:
                X[col] = X[col].astype(str) # ensure consistent string type

    y = df[target].copy()

    # Discretize continuous targets for Logistic Regression
    from sklearn.utils.multiclass import type_of_target
    if type_of_target(y) == 'continuous':
        try:
            y = pd.qcut(y, q=3, labels=["Low", "Medium", "High"])
        except ValueError:
            y = pd.cut(y, bins=3, labels=["Low", "Medium", "High"])

    # Encode target if categorical
    le = None
    if y.dtype == object or str(y.dtype) == "category":
        le = LabelEncoder()
        y = le.fit_transform(y)
        classes = le.classes_.tolist()
    else:
        classes = sorted(y.unique().tolist())

    try:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )
    except ValueError:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=None
        )

    from sklearn.compose import ColumnTransformer
    from sklearn.impute import SimpleImputer
    from sklearn.preprocessing import OneHotEncoder

    numeric_features = X.select_dtypes(include=['number']).columns.tolist()
    categorical_features = X.select_dtypes(exclude=['number']).columns.tolist()

    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='mean')),
        ('scaler', StandardScaler())
    ])

    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)
        ])

    pipeline = Pipeline([
        ('preprocessor', preprocessor),
        ("clf", LogisticRegression(max_iter=max_iter, random_state=42))
    ])
    
    pipeline.fit(X_train, y_train)

    train_acc = float(pipeline.score(X_train, y_train))
    test_acc = float(pipeline.score(X_test,  y_test))

    # Coefficients from the LR step
    clf = pipeline.named_steps["clf"]
    
    # Scikit-learn >= 1.0 supports get_feature_names_out
    try:
        out_features = preprocessor.get_feature_names_out()
        # Clean the prefix from ColumnTransformer (e.g. 'num__feature' -> 'feature')
        out_features = [f.split('__', 1)[1] if '__' in f else f for f in out_features]
    except AttributeError:
        out_features = features # Fallback

    coef_list = []
    is_binary = len(clf.classes_) == 2
    for i, cls in enumerate(clf.classes_):
        label = classes[cls] if le else str(cls)
        c_idx = 0 if is_binary else i
        multiplier = -1 if is_binary and i == 0 else 1
        for j, feat in enumerate(out_features):
            if j < len(clf.coef_[c_idx]):
                coef_list.append({
                    "class":    label,
                    "feature":  feat,
                    "coef":     round(float(clf.coef_[c_idx][j]) * multiplier, 6),
                })

    intercepts = {}
    for i, cls in enumerate(clf.classes_):
        label = classes[cls] if le else str(cls)
        c_idx = 0 if is_binary else i
        multiplier = -1 if is_binary and i == 0 else 1
        intercepts[label] = round(float(clf.intercept_[c_idx]) * multiplier, 6)

    # Save model bundle
    bundle = {
        "pipeline": pipeline,
        "classes":  classes,
        "features": features,
        "target":   target,
        "label_encoder": le,
        "preprocessing_version": 2,
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
