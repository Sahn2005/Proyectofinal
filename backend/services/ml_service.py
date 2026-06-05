import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix, roc_curve

def train_logistic_regression(df, target_column, test_size=0.2):
    X = df.drop(columns=[target_column])
    y = df[target_column]
    if y.dtype == 'object' or y.dtype.name == 'category':
        le = LabelEncoder()
        y = le.fit_transform(y)
    numeric_features = X.select_dtypes(include=['int64', 'float64']).columns.tolist()
    categorical_features = X.select_dtypes(include=['object', 'category']).columns.tolist()
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numeric_features),
            ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
        ])
    X_processed = preprocessor.fit_transform(X)
    if categorical_features:
        ohe = preprocessor.named_transformers_['cat']
        cat_feature_names = ohe.get_feature_names_out(categorical_features)
        feature_names = numeric_features + list(cat_feature_names)
    else:
        feature_names = numeric_features
    X_train, X_test, y_train, y_test = train_test_split(X_processed, y, test_size=test_size, random_state=42, stratify=y)
    model = LogisticRegression(max_iter=1000, class_weight='balanced')
    model.fit(X_train, y_train)
    return model, X_test, y_test, feature_names, preprocessor

def evaluate_model(model, X_test, y_test):
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
    recall = recall_score(y_test, y_pred, average='weighted', zero_division=0)
    f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
    if len(model.classes_) == 2:
        auc = roc_auc_score(y_test, y_proba[:, 1])
    else:
        auc = roc_auc_score(y_test, y_proba, multi_class='ovr', average='weighted')
    return {'accuracy': round(accuracy, 4), 'precision': round(precision, 4),
            'recall': round(recall, 4), 'f1': round(f1, 4), 'auc': round(auc, 4)}

def get_roc_data(model, X_test, y_test):
    if len(model.classes_) != 2:
        return None
    y_proba = model.predict_proba(X_test)[:, 1]
    fpr, tpr, _ = roc_curve(y_test, y_proba)
    return {'fpr': fpr.tolist(), 'tpr': tpr.tolist()}

def get_confusion_matrix(model, X_test, y_test):
    y_pred = model.predict(X_test)
    return confusion_matrix(y_test, y_pred).tolist()
