"""Train an ordinal-English-constrained logistic model from the saved training split.

Uses existing preprocessing and class-balanced logistic loss. The English
coefficient is constrained to >= 0.06 in standardized units, expressing a
documented product assumption: improving English alone must not reduce
the class score. This is a design constraint, not an observed causal effect.
It is trained ONLY on the saved training split (not the test split).
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import joblib
from scipy.optimize import minimize
from scipy.special import expit
from sklearn.metrics import accuracy_score,balanced_accuracy_score,f1_score,roc_auc_score
root=Path(__file__).resolve().parent
out=root/"milestone3_outputs"
x=pd.read_csv(out/"X_train.csv")
y=pd.read_csv(out/"y_train.csv").iloc[:,0].astype(int).to_numpy()
a=x.to_numpy(dtype=np.float64)
base=joblib.load(out/"best_placement_model.pkl")
feature_names=x.columns.tolist()
idx=feature_names.index("numeric__English_Proficiency")
min_english_coef=0.06  # fixed BEFORE checking performance, standardized-unit scale
n=len(y)
pos=float((y==1).sum())
neg=float((y==0).sum())
sw=np.where(y==1,n/(2*pos),n/(2*neg))
C=float(base.C)
def objective(params):
    weights, intercept=params[:-1],params[-1]
    z=a@weights+intercept
    loss=np.sum(sw*(np.logaddexp(0,z)-y*z))/n + np.dot(weights,weights)/(2*C*n)
    diff=sw*(expit(z)-y)/n
    grad=np.r_[a.T@diff+weights/(C*n), diff.sum()]
    return float(loss),grad
initial=np.r_[base.coef_[0],base.intercept_[0]]
lower_bounds=[(None,None)]*a.shape[1]+[(None,None)]
lower_bounds[idx]=(min_english_coef,None)
r=minimize(objective,initial,jac=True,bounds=lower_bounds,method="L-BFGS-B",
           options={"maxiter":900,"ftol":1e-12,"gtol":1e-8})
if not r.success and r.jac is None:
    raise RuntimeError(r.message)
if r.x[idx]<min_english_coef-1e-9:
    raise RuntimeError("English monotonic constraint not satisfied")
new=joblib.load(out/"best_placement_model.pkl")
new.coef_=r.x[:-1].reshape(1,-1)
new.intercept_=np.array([r.x[-1]])
target=out/"best_placement_model_monotonic_english.pkl"
joblib.dump(new,target)
xtest=pd.read_csv(out/"X_test.csv")
ytest=pd.read_csv(out/"y_test.csv").iloc[:,0].astype(int).to_numpy()
threshold=float(json.loads((root/"metrics.json").read_text())["threshold"])
summary={}
for label,model in [("original",base),("monotonic_english",new)]:
    pred=model.predict_proba(xtest)[:,1]
    cls=(pred>=threshold).astype(int)
    summary[label]={
        "accuracy":float(accuracy_score(ytest,cls)),
        "balanced_accuracy":float(balanced_accuracy_score(ytest,cls)),
        "macro_f1":float(f1_score(ytest,cls,average="macro")),
        "roc_auc":float(roc_auc_score(ytest,pred)),
        "english_coef_std":float(model.coef_[0][idx]),
    }
specimens = xtest.iloc[[0,10,40,80]].copy()
scaler=joblib.load(out/"preprocessor.pkl").named_transformers_["numeric"]
mu=float(scaler.mean_[idx])
scale=float(scaler.scale_[idx])
for row in specimens.to_numpy():
    vals=[]
    for v in [1,2,3]:
        row2=row.copy()
        row2[idx]=(v-mu)/scale
        vals.append(float(new.predict_proba(pd.DataFrame([row2],columns=feature_names))[0,1]))
    if not vals[0]<vals[1]<vals[2]:
        raise RuntimeError(f"Unexpected English predictions {vals}")
report={
    "method":"Class-balanced L2 logistic regression, fitted with L-BFGS-B and an ordinal English coefficient constraint",
    "training_split_only":True,
    "test_split_reused_in_development":True,
    "english_mapping":{"Basic":1,"Intermediate":2,"Advanced":3},
    "coefficient_lower_bound_standardized":min_english_coef,
    "feature":"English_Proficiency",
    "reason":"Documented monotonicity assumption: higher stated English proficiency should never lower model score when all other inputs remain constant",
    "caution":"Monotonicity is a product/domain assumption, not evidence of causality. Model metrics are retrospective on an already-reused holdout.",
    "train_rows":int(n),
    "test_rows":int(len(ytest)),
    "threshold":threshold,
    "optimizer_success":bool(r.success),
    "model_comparison":summary,
}
(root/"english_monotonicity_audit.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print("SAVED",target,"TRAIN",n,"TEST",len(ytest))
print("OPTIMIZER",r.success,r.message)
print(json.dumps(summary,indent=2))
print("SCENARIO CHECK",vals)
