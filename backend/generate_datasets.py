"""
Run this script once to generate the built-in dataset CSV files.
Usage:  python generate_datasets.py
"""
import os
from sklearn.datasets import load_iris, load_breast_cancer

OUT_DIR = os.path.join(os.path.dirname(__file__), "datasets")
os.makedirs(OUT_DIR, exist_ok=True)

# ── Iris ──────────────────────────────────────────────────────────────────────
iris = load_iris(as_frame=True)
df_iris = iris.frame.copy()
df_iris["species"] = df_iris["target"].map(dict(enumerate(iris.target_names)))
df_iris.drop(columns=["target"], inplace=True)
df_iris.columns = [c.replace(" (cm)", "").replace(" ", "_") for c in df_iris.columns]
df_iris.to_csv(os.path.join(OUT_DIR, "iris.csv"), index=False)
print(f"OK  iris.csv  ->  {df_iris.shape}")

# ── Breast Cancer ─────────────────────────────────────────────────────────────
bc = load_breast_cancer(as_frame=True)
df_bc = bc.frame.copy()
df_bc.columns = [c.replace(" ", "_") for c in df_bc.columns]
df_bc.to_csv(os.path.join(OUT_DIR, "breast_cancer.csv"), index=False)
print(f"OK  breast_cancer.csv  ->  {df_bc.shape}")

print("Done.")
