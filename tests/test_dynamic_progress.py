from pathlib import Path
import sys
sys.stdout.reconfigure(encoding="utf-8")
from streamlit.testing.v1 import AppTest

root=Path(__file__).resolve().parents[1]
at=AppTest.from_file(str(root/"app.py"),default_timeout=50).run()
button=next(b for b in at.button if "عرض التقييم" in b.label)
button.click().run()
def html():
    return "\n".join(str(m.value) for m in at.markdown if not str(m.value).lstrip().startswith("<style>"))
checks=list(at.checkbox)
print("CHECKBOXES",len(checks),[c.label for c in checks],flush=True)
assert len(checks)>0
assert "f-completion-card" not in html()
assert "f-progress-message" not in html()
checks[0].check().run()
assert not at.exception, [e.message for e in at.exception]
if len(checks)>1:
    assert "f-progress-message" in html()
    assert "f-completion-card" not in html()
for checkbox in at.checkbox:
    if not checkbox.value:
        checkbox.check().run()
assert not at.exception, [e.message for e in at.exception]
assert "f-completion-card" in html()
print("COMPLETED STATE",len(at.checkbox),"tasks; text and illustration visible",flush=True)
at.checkbox[0].uncheck().run()
assert "f-completion-card" not in html()
assert "f-progress-message" in html()
print("UNCHECK HIDES CELEBRATION -- PASSED",flush=True)

# A profile with no skill gaps uses two illustrative development actions.
at=AppTest.from_file(str(root/"app.py"),default_timeout=50).run()
for key,target in {
    "Programming_Skill":8,"Problem_Solving":8,"Communication_Skills":8,
    "Projects_Completed":4,"Internships":2,"Certifications":2,
    "Resume_Score":85,"Interview_Score":85
}.items():
    widget=next((w for w in at.number_input if w.label.startswith({
       "Programming_Skill":"البرمجة","Problem_Solving":"حل المشكلات",
       "Communication_Skills":"التواصل","Projects_Completed":"عدد المشاريع",
       "Internships":"عدد التدريبات","Certifications":"عدد الشهادات",
       "Resume_Score":"تقييم السيرة","Interview_Score":"تقييم مهارات المقابلة"
    }[key])),None)
    if widget:widget.set_value(target)
next(b for b in at.button if "عرض التقييم" in b.label).click().run()
print("NO-GAP PLAN ITEMS",len(at.checkbox),flush=True)
assert len(at.checkbox)==2
for cb in at.checkbox:
    cb.check().run()
assert "f-completion-card" in "\n".join(str(m.value) for m in at.markdown)
print("DYNAMIC 2-TASK PLAN COMPLETION -- PASSED",flush=True)
