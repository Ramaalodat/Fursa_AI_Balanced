"""Regression test for English proficiency and saved model consistency."""
from pathlib import Path
import json
import joblib
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"milestone3_outputs"
model=joblib.load(OUT/"best_placement_model_monotonic_english.pkl")
old=joblib.load(OUT/"best_placement_model.pkl")
processor=joblib.load(OUT/"preprocessor.pkl")
columns=processor.get_feature_names_out().tolist()
idx=columns.index("numeric__English_Proficiency")
assert model.coef_[0,idx]>0
assert old.coef_[0,idx]<0
scaler=processor.named_transformers_["numeric"]
mu=float(scaler.mean_[idx]);scale=float(scaler.scale_[idx])
sample=pd.read_csv(OUT/"X_test.csv").head(150)
values=[]
for level in (1,2,3):
    x=sample.copy()
    x["numeric__English_Proficiency"]=(level-mu)/scale
    values.append(model.predict_proba(x)[:,1])
assert np.all(values[0] < values[1]) and np.all(values[1] < values[2])
print("CHECK 150 PROFILES: Basic < Intermediate < Advanced -- PASS")
print("EXAMPLE PROBABILITIES (%)", [round(float(v[0])*100,2) for v in values])
meta=json.loads((ROOT/"english_monotonicity_audit.json").read_text(encoding="utf-8"))
assert meta["training_split_only"]
assert meta["coefficient_lower_bound_standardized"]==0.06
print("AUDIT",meta["model_comparison"])
