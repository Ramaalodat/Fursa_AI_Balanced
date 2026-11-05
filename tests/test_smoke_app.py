from pathlib import Path
import sys
from streamlit.testing.v1 import AppTest

sys.stdout.reconfigure(encoding="utf-8")
app = str(Path(__file__).resolve().parents[1] / "app.py")
at = AppTest.from_file(app, default_timeout=50).run()
print("START", "tabs", [x.label for x in at.tabs], "exceptions", [e.message for e in at.exception],flush=True)
assert len(at.exception) == 0, "Initial render"
assert len(at.number_input) >= 9, "Assessment must use typed numeric inputs"
assert not at.slider, "Unexpected sliders in form"
button = next(b for b in at.button if "عرض التقييم" in b.label)
button.click().run()
print("RESULT", [(x.label, x.value) for x in at.metric][:4], "exceptions", [e.message for e in at.exception],flush=True)
assert len(at.exception) == 0, "Assessment render"
assert len(at.metric) >= 7, "Evaluation metrics missing"
assert len(at.checkbox) == 3, "Plan checklist missing"
assert at.get("image"), "Mascots and saved charts expected"
print("OK AR", flush=True)
at.selectbox(key="ui_lang").set_value("English").run()
print("EN", [x.label for x in at.tabs], "exceptions", [e.message for e in at.exception],flush=True)
assert len(at.exception) == 0
assert any("Model performance" in x.label for x in at.tabs)
print("ALL PASSED",flush=True)
