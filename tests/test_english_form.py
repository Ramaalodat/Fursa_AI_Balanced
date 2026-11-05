from pathlib import Path
from streamlit.testing.v1 import AppTest
import re,sys
sys.stdout.reconfigure(encoding="utf-8")
path=str(Path(__file__).resolve().parents[1]/"app.py")
scores={}
for level in ["Basic","Intermediate","Advanced"]:
    app=AppTest.from_file(path,default_timeout=50).run()
    picker=next(x for x in app.selectbox if "الإنجليزية" in x.label)
    picker.set_value(level)
    next(x for x in app.button if x.label=="عرض التقييم").click().run()
    print("REQUEST", level, "SUBMITTED", app.session_state["fursa_profile"]["English_Proficiency"],flush=True)
    errors=[e.message for e in app.exception]
    if errors: raise RuntimeError(errors)
    html=" ".join(m.value for m in app.markdown)
    m=re.search(r"<strong>([0-9.]+)%</strong><span>MODEL SCORE",html)
    if not m: raise RuntimeError("Can't locate rendered model score")
    scores[level]=float(m.group(1))
print("APP SCORE BY ENGLISH LEVEL",scores)
assert scores["Basic"]<scores["Intermediate"]<scores["Advanced"]
print("FULL UI ENGLISH ORDER PASS")
