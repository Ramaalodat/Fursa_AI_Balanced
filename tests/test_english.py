from pathlib import Path
from streamlit.testing.v1 import AppTest
import sys
sys.stdout.reconfigure(encoding="utf-8")
app=str(Path(__file__).resolve().parents[1]/"app.py")
a=AppTest.from_file(app,default_timeout=45).run()
print([(x.key,x.value) for x in a.selectbox],flush=True)
lang=next(x for x in a.selectbox if x.key=="ui_lang")
lang.set_value("English").run()
print("ENGLISH EXCEPTIONS:",[(x.message or "")[:250] for x in a.exception],flush=True)
print("ENGLISH TABS:",[x.label for x in a.tabs],flush=True)
submit=next(x for x in a.button if "View assessment" in x.label)
submit.click().run()
print("ENGLISH SUBMITTED EXCEPTIONS:",[(x.message or "")[:250] for x in a.exception],flush=True)
print("ENGLISH OUTPUT:",[(x.label,x.value) for x in a.metric][:3],flush=True)
if a.exception:
    raise SystemExit("Failed bilingual test")
