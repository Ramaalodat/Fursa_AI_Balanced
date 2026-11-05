from pathlib import Path
import json

import joblib
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="فرصة AI | Fursa AI",
    page_icon=":material/assessment:",
    layout="wide",
    initial_sidebar_state="collapsed",
)
ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"

if "ui_lang" not in st.session_state:
    st.session_state.ui_lang = "العربية"
for setting, initial in [("reduce_motion", False), ("compact_layout", False)]:
    if setting not in st.session_state:
        st.session_state[setting] = initial

ar = st.session_state.ui_lang == "العربية"

def t(arabic, english):
    return arabic if ar else english

def mascot(mood, width=240):
    path = ASSETS / f"duck_{mood}.webp"
    if path.exists():
        st.image(str(path), width=width)
    else:
        st.caption("Fursa AI")

def panel(title, body, kicker="FURSA AI"):
    st.markdown(
        f'<div class="f-panel"><span class="f-kicker">{kicker}</span>'
        f'<h3>{title}</h3><p>{body}</p></div>',
        unsafe_allow_html=True,
    )

css = (ASSETS / "fursa_theme.css").read_text(encoding="utf-8")
css = css.replace("__COMPACT__", (
    "[data-testid='stForm']{padding:14px 17px!important}"
    ".f-section{margin:14px 0 10px!important}"
    ".f-panel{padding:16px!important}" if st.session_state["compact_layout"] else ""
))
css = css.replace("__REDUCED_MOTION__", (
    "*,*::before,*::after{scroll-behavior:auto!important;animation:none!important;transition:none!important}"
    if st.session_state["reduce_motion"] else ""
))
css = css.replace("__DIR__", "rtl" if ar else "ltr")
css = css.replace("__ALIGN__", "right" if ar else "left")
css = css.replace("__ROW__", "row-reverse" if ar else "row")
css = css.replace("__BRAND_ALIGN__", "flex-end" if ar else "flex-start")
st.markdown("<style>" + css + "</style>", unsafe_allow_html=True)

brand, change_lang, preferences = st.columns([5.3, 1.5, 1.5], vertical_alignment="center")
with brand:
    # Official FURSA AI wordmark supplied by the project owner, without redrawing.
    st.image(str(ASSETS / "fursa_logo.png"), width=222)
with change_lang:
    st.selectbox("Language / اللغة", ["العربية", "English"],
                 key="ui_lang", label_visibility="collapsed")
with preferences:
    with st.popover(t("الإعدادات", "Settings")):
        st.markdown("#### " + t("تفضيلات العرض", "Display preferences"))
        st.toggle(t("تقليل الحركة", "Reduce motion"), key="reduce_motion")
        st.toggle(t("عرض مدمج", "Compact layout"), key="compact_layout")
        st.divider()
        if st.button(t("بدء تقييم جديد", "Start a new assessment"), key="reset_all"):
            st.session_state.pop("fursa_profile", None)
            for key in list(st.session_state.keys()):
                if key.startswith(("task_done_", "sim_")):
                    del st.session_state[key]
            st.rerun()
        st.caption(t("هذه التفضيلات محفوظة خلال الجلسة فقط.",
                     "Preferences are saved for this session only."))

hero_text, hero_mascot = st.columns([1.75, 1], vertical_alignment="center")
with hero_text:
    st.markdown(
        f'<div class="f-hero"><span class="f-eyebrow">{t("مسارك المهني، بوضوح أكبر", "MAKE INFORMED CAREER DECISIONS")}</span>'
        f'<h1>{t("افهم مهاراتك. وخطّط لخطوتك القادمة.", "Understand your skills. Plan what comes next.")}</h1>'
        f'<p>{t("تقييم تفاعلي يجمع بياناتك المهنية في صورة واضحة، ويحدد أولويات تعلم عملية، ويتيح لك مقارنة سيناريوهات التطوير باستخدام نموذج تعلم آلة.",
                   "Explore your professional profile, identify practical development priorities and compare learning scenarios with a machine-learning model.")}</p>'
        f'<div class="f-tags"><span>{t("تقييم المهارات", "Skills assessment")}</span>'
        f'<span>{t("خطة تطوير", "Development plan")}</span>'
        f'<span>{t("محاكاة السيناريوهات", "Scenario simulator")}</span></div></div>',
        unsafe_allow_html=True,
    )
with hero_mascot:
    mascot("graduate", 320)

st.markdown(
    f'<div class="f-stepstrip">'
    f'<div class="f-step"><i>01</i>{t("إدخال البيانات", "Profile inputs")}</div>'
    f'<div class="f-step"><i>02</i>{t("التقييم", "Assessment")}</div>'
    f'<div class="f-step"><i>03</i>{t("خطة التطوير", "Action plan")}</div>'
    f'<div class="f-step"><i>04</i>{t("المحاكاة", "Simulation")}</div>'
    f'</div>', unsafe_allow_html=True,
)

FEATURES = [
    "CGPA", "Programming_Skill", "Problem_Solving", "Projects_Completed",
    "Internships", "Certifications", "Communication_Skills",
    "English_Proficiency", "Resume_Score", "Interview_Score"
]
LABELS = {
    "CGPA": ("المعدل الجامعي (من 4)", "CGPA (out of 4)"),
    "Programming_Skill": ("البرمجة (من 10)", "Programming (out of 10)"),
    "Problem_Solving": ("حل المشكلات (من 10)", "Problem solving (out of 10)"),
    "Projects_Completed": ("عدد المشاريع المنجزة", "Completed projects"),
    "Internships": ("عدد التدريبات العملية", "Internships"),
    "Certifications": ("عدد الشهادات", "Certificates"),
    "Communication_Skills": ("التواصل (من 10)", "Communication (out of 10)"),
    "English_Proficiency": ("مستوى اللغة الإنجليزية", "English proficiency"),
    "Resume_Score": ("تقييم السيرة الذاتية ذاتيًا (0–100)", "Self-rated CV quality (0–100)"),
    "Interview_Score": ("تقييم مهارات المقابلة ذاتيًا (0–100)", "Self-rated interview skills (0–100)"),
}
TARGETS = {
    "Programming_Skill": 7, "Problem_Solving": 7,
    "Communication_Skills": 7, "Projects_Completed": 3,
    "Internships": 1, "Certifications": 1,
    "Resume_Score": 70, "Interview_Score": 70,
}
ADVICE = {
    "Programming_Skill": ("خصص 30 دقيقة يوميًا لحل مسائل Python، وختمها بمشروع صغير.", "Practice Python for 30 minutes a day and finish with a small project."),
    "Problem_Solving": ("حل مشكلتين عمليتين هذا الأسبوع واكتب خطوات التفكير والحل.", "Solve two practical problems this week and explain your steps."),
    "Communication_Skills": ("سجل فيديو مدته دقيقتين تشرح فيه أحد مشاريعك.", "Record a two-minute explanation of one of your projects."),
    "Projects_Completed": ("نفذ مشروعًا يوضح مهارة واحدة، وارفعه على GitHub مع README واضح.", "Ship a small project demonstrating one skill and publish a clear GitHub README."),
    "Internships": ("حدّث سيرتك وقدم على ثلاث فرص تدريب مناسبة لمجالك.", "Update your CV and apply to three relevant internships."),
    "Certifications": ("اختر دورة تخدم هدفك وأنجز مهمة عملية منها قبل الشهادة.", "Pick a relevant course and do a practical assignment before earning the certificate."),
    "Resume_Score": ("راجع CV: خلي المشاريع والأدوات والنتائج واضحة ومختصرة.", "Refresh your CV with clear projects, tools and measurable outcomes."),
    "Interview_Score": ("جرب مقابلة تدريبية وسجل أجوبتك على ثلاثة أسئلة شائعة.", "Do a mock interview and record answers to three common questions."),
}

CAREER_GOALS = {
    "explore": ("استكشاف الخيارات المهنية", "Exploring career options"),
    "ai": ("الذكاء الاصطناعي وتعلم الآلة", "AI & Machine Learning"),
    "data": ("تحليل البيانات", "Data Analytics"),
    "software": ("تطوير البرمجيات", "Software Development"),
}
PROJECT_IDEAS = {
    "explore": ("اعمل مشروعًا صغيرًا مرتبطًا باهتمامك وانشر خطواته ونتائجه.",
                "Build a small project in an area of interest and document the process."),
    "ai": ("اعمل نموذج ML صغير، قارنه بخط أساس، واعرض المقاييس ونتائج الاختبار على GitHub.",
           "Build a small ML model, compare against a baseline, and publish evaluation metrics."),
    "data": ("جهّز Dashboard من بيانات مفتوحة: تنظيف، رسوم، وثلاث ملاحظات قابلة للتنفيذ.",
             "Build an open-data dashboard with cleaning, visualizations, and three useful insights."),
    "software": ("ابنِ تطبيق ويب صغير مع قاعدة بيانات وتوثيق واضح وتجربة مستخدم مرتبة.",
                 "Ship a small web application with storage, clear docs, and a thoughtful UX."),
}

def label(key):
    return t(*LABELS[key])

@st.cache_resource
def load_artifacts(model_path, model_stamp, processor_path, processor_stamp):
    return joblib.load(model_path), joblib.load(processor_path)

model_path = ROOT / "milestone3_outputs" / "best_placement_model_monotonic_english.pkl"
processor_path = ROOT / "milestone3_outputs" / "preprocessor.pkl"
if not model_path.exists() or not processor_path.exists():
    st.error(t("ملفات النموذج مش موجودة داخل milestone3_outputs.", "Model artifacts were not found in milestone3_outputs."))
    st.stop()

try:
    model, processor = load_artifacts(
        str(model_path), model_path.stat().st_mtime_ns,
        str(processor_path), processor_path.stat().st_mtime_ns,
    )
except Exception as exc:
    st.error(t("تعذر تحميل النموذج. راجع إصدارات المكتبات.", "Failed to load the model. Check dependency versions."))
    st.exception(exc)
    st.stop()

def predict_score(values):
    frame = pd.DataFrame([values], columns=FEATURES)
    frame["English_Proficiency"] = frame["English_Proficiency"].map(
        {"Basic": 1, "Intermediate": 2, "Advanced": 3}
    ).astype(int)
    # Same derived fields and transformer as the training notebook.
    frame["Soft_Skills_Average"] = frame[
        ["Communication_Skills", "Problem_Solving"]
    ].mean(axis=1)
    frame["Practical_Exposure_Score"] = frame[
        ["Projects_Completed", "Internships"]
    ].sum(axis=1)
    transformed = processor.transform(frame)
    transformed = pd.DataFrame(transformed, columns=processor.get_feature_names_out())
    classes = list(model.classes_)
    positive_index = classes.index(1) if 1 in classes else classes.index("Placed")
    return float(model.predict_proba(transformed)[0, positive_index] * 100)

def analyze_skills(profile):
    strengths = [key for key in TARGETS if profile[key] >= TARGETS[key]]
    gaps = [key for key in TARGETS if profile[key] < TARGETS[key]]
    gaps.sort(key=lambda key: profile[key] / TARGETS[key])
    return strengths, gaps

def section(number, title, subtitle):
    st.markdown(
        f'<div class="f-section"><span class="f-num">{number}</span>'
        f'<h2>{title}</h2><p>{subtitle}</p></div>',
        unsafe_allow_html=True,
    )

profile_tab, plan_tab, simulation_tab, science_tab = st.tabs([
    t("تقييم المهارات", "Assessment"),
    t("خطة التطوير", "Development plan"),
    t("محاكاة التحسين", "Simulation"),
    t("أداء النموذج", "Model performance"),
])

with profile_tab:
    section("01", t("ابدأ بتقييم ملفك المهني", "Assess your professional profile"),
            t("أدخل قيمًا تعكس مستواك الحالي. كل المدخلات قابلة للتعديل وإعادة التقييم.",
              "Enter realistic values that reflect your current experience. You can update your profile anytime."))
    intro, intro_pic = st.columns([3.4, 1], vertical_alignment="center")
    with intro:
        panel(
            t("بطوط جاهز يساعدك!", "Your duck buddy is ready to help!"),
            t("عبّي المعلومات، وبعدها رح تشوف مؤشر النموذج، ونقاط القوة، والأشياء اللي ممكن تطورها.",
              "Fill in your details, then explore your model score, strengths, and skills you could improve."),
            t("رسالة من بطوط", "A NOTE FROM YOUR DUCK BUDDY")
        )
    with intro_pic:
        mascot("assessment", 200)

    with st.form("career_form"):
        career_goal = st.selectbox(
            t("المجال المهني المستهدف", "Target career area"),
            list(CAREER_GOALS),
            format_func=lambda goal: t(*CAREER_GOALS[goal]),
            help=t("يُستخدم فقط لتخصيص اقتراحات المشاريع، وليس للتنبؤ.",
                   "Personalizes project suggestions only; not used for prediction."),
        )
        st.markdown('<div class="f-form-subheading">' +
                    t("البيانات الأكاديمية والمهنية", "Academic and professional information") +
                    '</div>', unsafe_allow_html=True)
        academics, experience, professional = st.columns(3)
        inputs = {"Career_Goal": career_goal}
        with academics:
            st.markdown("#### " + t("المؤهلات والمهارات التقنية", "Academic & technical skills"))
            inputs["CGPA"] = st.number_input(
                label("CGPA"), min_value=2.0, max_value=4.0,
                value=3.10, step=0.05, format="%.2f",
                help=t("أدخل معدلك على مقياس من 4.", "Enter GPA on a 4-point scale."),
            )
            inputs["Programming_Skill"] = st.number_input(
                label("Programming_Skill"), min_value=1, max_value=10,
                value=6, step=1,
                help=t("تقييم ذاتي من 1 للمبتدئ إلى 10 للمتقدم.",
                       "Self-rating from 1 (beginner) to 10 (advanced)."),
            )
            inputs["Problem_Solving"] = st.number_input(
                label("Problem_Solving"), min_value=1, max_value=10, value=6, step=1)
            inputs["English_Proficiency"] = st.selectbox(
                label("English_Proficiency"),
                ["Basic", "Intermediate", "Advanced"], index=1,
                format_func=lambda x: {"Basic": t("أساسي", "Basic"),
                                       "Intermediate": t("متوسط", "Intermediate"),
                                       "Advanced": t("متقدم", "Advanced")}[x]
            )
        with experience:
            st.markdown("#### " + t("المشاريع والخبرة العملية", "Projects & experience"))
            inputs["Projects_Completed"] = st.number_input(
                label("Projects_Completed"), min_value=0, max_value=15, value=2, step=1)
            inputs["Internships"] = st.number_input(
                label("Internships"), min_value=0, max_value=5, value=0, step=1)
            inputs["Certifications"] = st.number_input(
                label("Certifications"), min_value=0, max_value=10, value=1, step=1)
            st.caption(t("استخدم عدد المشاريع المكتملة والتدريبات الفعلية فقط.",
                         "Count completed projects and actual internships only."))
        with professional:
            st.markdown("#### " + t("المهارات المهنية", "Professional skills"))
            inputs["Communication_Skills"] = st.number_input(
                label("Communication_Skills"), min_value=1, max_value=10, value=6, step=1)
            inputs["Resume_Score"] = st.number_input(
                label("Resume_Score"), min_value=0, max_value=100,
                value=65, step=5,
                help=t("تقييم ذاتي تقريبي؛ التطبيق لا يفحص ملف السيرة الذاتية.",
                       "A self-rating; the app does not inspect a CV file."),
            )
            inputs["Interview_Score"] = st.number_input(
                label("Interview_Score"), min_value=0, max_value=100,
                value=65, step=5,
                help=t("تقييم ذاتي لمهارات المقابلة وليس اختبارًا فعليًا.",
                       "A self-rating, not a formal interview assessment."),
            )
        st.caption(t("تُستخدم هذه المعلومات خلال جلسة الموقع الحالية فقط.",
                     "These inputs remain within the current session."))
        submitted = st.form_submit_button(t("عرض التقييم", "View assessment"),
                                          type="primary", width="stretch")
    if submitted:
        st.session_state["fursa_profile"] = inputs.copy()
        for key in list(st.session_state.keys()):
            if key.startswith("task_done_"):
                del st.session_state[key]

    if "fursa_profile" in st.session_state:
        profile = st.session_state["fursa_profile"]
        try:
            result = predict_score(profile)
        except Exception as exc:
            st.error(t("صار عدم توافق مع النموذج المحفوظ. تأكدي من الملفات.", "The saved model could not process this profile."))
            st.exception(exc)
            st.stop()
        strengths, gaps = analyze_skills(profile)
        if result >= 70:
            tone = t("مؤشر إيجابي نسبيًا وفق أنماط بيانات التدريب", "A relatively positive model score on the training patterns")
            mood = "success"
        elif result >= 45:
            tone = t("ملفك يتضمن نقاط قوة ومجالات قابلة للتطوير", "Your profile has strengths and development opportunities")
            mood = "assessment"
        else:
            tone = t("يوصى بالتركيز على تطوير المهارات الأساسية", "Prioritize foundational skill development")
            mood = "tea"

        section("02", t("نتيجة التقييم", "Assessment result"),
                t("المؤشر يستخدم النموذج المحدّث مع ترتيب منطقي لمستويات الإنجليزية، وليس احتمال توظيف مؤكّدًا.", "The model uses a monotonic English-level constraint; its score is not a verified hiring probability."))
        result_text, result_mascot = st.columns([2.8, 1], vertical_alignment="center")
        with result_text:
            st.markdown(
                f'<div class="f-result"><div><span class="f-chip">{t("مؤشر فئة التوظيف التجريبي","EXPERIMENTAL PLACED-CLASS SCORE")}</span>'
                f'<h2>{tone}</h2><p>{t("هذا الرقم يعبّر عن استجابة النموذج لمدخلاتك بناءً على بيانات التدريب. لا يُعدّ قياسًا معتمدًا لجاهزيتك، أو احتمال توظيف مُعايرًا، أو ضمانًا للحصول على وظيفة.",
                                    "This number is the model response to your inputs based on its dataset. It is not validated readiness, a calibrated job probability, or a job guarantee.")}</p></div>'
                f'<div class="f-result-value"><strong>{result:.1f}%</strong><span>MODEL SCORE</span></div></div>',
                unsafe_allow_html=True,
            )
            st.progress(min(1., max(0., result / 100)))
        with result_mascot:
            mascot(mood, 265)
        start_here = label(gaps[0]) if gaps else t("ابنِ مشروعًا جديدًا", "Build a new project")
        st.markdown(
            f'<div class="f-grid"><div class="f-stat"><span>{t("مهارات وصلت للهدف","Targets reached")}</span><strong><span dir="ltr">{len(strengths)} / {len(TARGETS)}</span></strong><small>{t("أهداف تعليمية توضيحية","Illustrative learning targets")}</small></div>'
            f'<div class="f-stat"><span>{t("مهارات ممكن نطورها","Areas to develop")}</span><strong>{len(gaps)}</strong><small>{t("حسب القيم اللي أدخلتها","Based on entered values")}</small></div>'
            f'<div class="f-stat"><span>{t("خلينا نبدأ بـ","Recommended first step")}</span><strong style="font-size:17px">{start_here}</strong><small>{t("من خطة مهاراتك","From your learning plan")}</small></div></div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="f-note">' +
            t("شوف أولوياتك في تبويب «خطة التطوير»، وبعدها جرّب تغيير المدخلات في «محاكاة التحسين». الأهداف التعليمية مقترحة وليست معايير توظيف رسمية.",
              "Explore your priorities in Development plan, then try new scenarios in Simulation. Learning targets are illustrative, not hiring standards.") +
            '</div>', unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<div class="f-note">' +
            t("أول ما نحلّل بياناتك، رح تلاقي هون نتيجتك وخطوات التطوير المناسبة إلك.", "Once you submit your details, your model result and next steps will appear here.") +
            '</div>', unsafe_allow_html=True,
        )

with plan_tab:
    if "fursa_profile" not in st.session_state:
        section("02", t("أكمل التقييم أولًا", "Complete your assessment first"),
                t("عبّي البيانات أولاً بتبويب التقييم حتى نقدر نجهز خطة خاصة بملفك.", "Fill in the assessment first to see your learning plan."))
        mascot("detective", 285)
    else:
        profile = st.session_state["fursa_profile"]
        strengths, gaps = analyze_skills(profile)
        section("03", t("تحليل المهارات", "Skills breakdown"),
                t("مقارنة مع أهداف تعليمية مقترحة، وليست تفسيرًا سببيًا من النموذج.",
                  "A comparison with illustrative learning targets, not a causal explanation from the model."))
        info, pic = st.columns([3, 1], vertical_alignment="center")
        with info:
            panel(
                t("بطوط اكتشف نقاط قوتك!", "Your duck buddy spotted your strengths!"),
                t("خليني أفرجيك الأشياء اللي أنت شاطر فيها، ونشوف شو ممكن نطوّر مع بعض.",
                  "Here are the things you do well, plus a few skills we can work on together."),
                "SKILLS & GROWTH"
            )
        with pic:
            mascot("detective", 240)
        good_col, next_col = st.columns(2)
        with good_col:
            with st.container(border=True):
                st.markdown("#### " + t(" جوانب قوية", " Targets you meet"))
                if not strengths:
                    st.write(t("يمكن البدء بالمهارات الأعلى أولوية.", "Start with the highest-priority skills."))
                for key in strengths:
                    st.markdown(f'<div class="f-skill f-skill-good"><span>{label(key)}</span><b>{profile[key]} / {TARGETS[key]}</b></div>', unsafe_allow_html=True)
        with next_col:
            with st.container(border=True):
                st.markdown("#### " + t(" أولويات التطوير", " Areas to work on"))
                if not gaps:
                    st.write(t("جميع الأهداف التعليمية المقترحة متحققة.", "All proposed learning targets are met."))
                for key in gaps:
                    st.markdown(f'<div class="f-skill"><span>{label(key)}</span><b>{profile[key]} / {TARGETS[key]}</b></div>', unsafe_allow_html=True)

        section("04", t("خطة التطوير المقترحة", "Recommended development plan"),
                t("ابدأ بأول ثلاث أولويات، وكل خطوة معها تطبيق عملي.",
                  "Focus on up to three priorities, each with a concrete action."))
        priority_keys = gaps[:3] if gaps else ["Projects_Completed", "Interview_Score"]
        for i, key in enumerate(priority_keys, 1):
            st.markdown(
                f'<div class="f-action"><div class="f-index">{i:02d}</div><div><strong>{label(key)}</strong>'
                f'<p>{t(*ADVICE[key])}</p><small>{t(" خطوة قابلة للتطبيق"," Practical next step")}</small></div></div>',
                unsafe_allow_html=True,
            )
        st.markdown("#### " + t(" فكرة مشروع تناسب هدفك", " A portfolio idea for your direction"))
        chosen_goal = profile.get("Career_Goal", "explore")
        panel(t(*CAREER_GOALS.get(chosen_goal, CAREER_GOALS["explore"])),
              t(*PROJECT_IDEAS.get(chosen_goal, PROJECT_IDEAS["explore"])),
              "PORTFOLIO STARTER")
        st.markdown("#### " + t("تابع تقدمك", "Track your progress"))
        with st.container(border=True):
            done = 0
            for key in priority_keys:
                finished = st.checkbox(
                    t("أنجزت: ", "Completed: ") + label(key),
                    key="task_done_" + key,
                )
                done += int(finished)
            total_steps = len(priority_keys)
            st.markdown(
                f'<div class="f-progress-label"><strong>{t("إنجاز خطتك", "Your progress")}</strong>'
                f'<span dir="ltr">{done} / {total_steps}</span></div>',
                unsafe_allow_html=True,
            )
            st.progress(done / total_steps)
            st.caption(t("تُحفظ متابعة الخطوات خلال جلسة الموقع فقط.",
                         "Checklist progress is saved only during this session."))

        # All celebration copy and counts are generated by the UI, not baked into
        # artwork. The illustration appears ONLY when the current checklist is complete.
        if done == total_steps:
            completed_text, completed_duck = st.columns(
                [2.6, 1], gap="small", vertical_alignment="center"
            )
            with completed_text:
                st.markdown(
                    '<div class="f-completion-card">'
                    f'<span class="f-completion-kicker">{t("الخطة مكتملة", "PLAN COMPLETED")}</span>'
                    f'<h3>{t("يا سلام عليك! كملت خطتك كلها.", "Great work! You completed your plan.")}</h3>'
                    f'<p>{t("بطوط فخور فيك! الخطوات اللي حددناها صارت مكتملة، وهسا تقدر تختار هدف جديد وتكمل تطوير مهاراتك.",
                              "Your duck buddy is proud of you! Every action in this plan is checked off. You can set a new goal and keep growing.")}</p>'
                    f'<span class="f-completion-count">{t("الخطوات المنجزة", "Completed actions")}: '
                    f'<b dir="ltr">{done} / {total_steps}</b></span></div>',
                    unsafe_allow_html=True,
                )
            with completed_duck:
                mascot("success", 195)
        elif done > 0:
            st.markdown(
                '<div class="f-progress-message">'
                f'<strong>{t("ممتاز! كمّل بنفس الحماس.", "Nice progress. Keep going.")}</strong> '
                f'{t("خلصت", "You have completed")} '
                f'<b dir="ltr">{done} / {total_steps}</b> '
                f'{t("من خطوات خطتك.", "of your plan actions.")}</div>',
                unsafe_allow_html=True,
            )
        report_lines = [
            t("فرصة AI — خطة تطوير شخصية", "FURSA AI — Personal Learning Plan"),
            t("مؤشر النموذج: ", "Model score: ") + f"{predict_score(profile):.1f}%",
            t("تم تدريب النموذج مع شرط ألا يؤدي تحسين مستوى الإنجليزية وحده إلى خفض المؤشر. الرقم لا يمثل احتمال توظيف معايرًا أو ضمانًا بوظيفة.",
              "This is not a calibrated hiring probability or a guarantee."),
            "",
            t("مجال الاهتمام: ", "Career direction: ") +
                t(*CAREER_GOALS.get(profile.get("Career_Goal", "explore"), CAREER_GOALS["explore"])),
            t("فكرة مشروع: ", "Portfolio idea: ") +
                t(*PROJECT_IDEAS.get(profile.get("Career_Goal", "explore"), PROJECT_IDEAS["explore"])),
            "",
            t("أولويات التطوير:", "Growth priorities:"),
        ]
        report_lines += [f"- {label(key)}: {t(*ADVICE[key])}" for key in priority_keys]
        report_lines += ["", t("إرشاد تعليمي تقريبي فقط.", "Illustrative educational guidance only.")]
        st.download_button(
            t(" نزّل خطتك كملف نصي", " Download your learning plan"),
            "\n".join(report_lines).encode("utf-8"),
            file_name="fursa_learning_plan.txt",
            mime="text/plain",
        )

with simulation_tab:
    if "fursa_profile" not in st.session_state:
        section("05", t("المحاكاة متاحة بعد التقييم", "Simulation follows the assessment"),
                t("ابدأ بتقييم ملفك حتى نقدر نقارن المؤشر قبل وبعد.", "First assess your profile so we can compare before and after."))
        mascot("coder", 290)
    else:
        profile = st.session_state["fursa_profile"]
        before_score = predict_score(profile)
        section("05", t("محاكاة تطوير المهارات", "Skill development simulation"),
                t("جرّب قيم افتراضية بدون ما تغيّر ملفك الأصلي.", "Try hypothetical changes without modifying your original profile."))
        expl, pic = st.columns([3, 1], vertical_alignment="center")
        with expl:
            panel(
                t("يلا نجرب مع بعض!", "Let’s explore your next step!"),
                t("جرّب تضيف مشروع أو تدريب أو تطوّر البرمجة، وشوف كيف بيتغير مؤشر النموذج.",
                  "Try adding a project, internship or programming skill and see how the model score changes."),
                "WHAT-IF LAB"
            )
        with pic:
            mascot("coder", 245)
        x, y, z = st.columns(3)
        with x:
            add_projects = st.number_input(
                t("مشاريع إضافية", "Additional projects"), min_value=0,
                max_value=3, value=0, step=1, key="sim_projects")
        with y:
            add_internships = st.number_input(
                t("تدريبات إضافية", "Additional internships"), min_value=0,
                max_value=2, value=0, step=1, key="sim_internships")
        with z:
            add_programming = st.number_input(
                t("زيادة مستوى البرمجة", "Programming improvement"), min_value=0,
                max_value=3, value=0, step=1, key="sim_programming")
        scenario = profile.copy()
        scenario["Projects_Completed"] = min(15, profile["Projects_Completed"] + add_projects)
        scenario["Internships"] = min(5, profile["Internships"] + add_internships)
        scenario["Programming_Skill"] = min(10, profile["Programming_Skill"] + add_programming)
        after_score = predict_score(scenario)
        m1, m2, m3 = st.columns(3)
        m1.metric(t("المؤشر الأصلي", "Original score"), f"{before_score:.1f}%")
        m2.metric(t("المؤشر الافتراضي", "Simulated score"), f"{after_score:.1f}%")
        m3.metric(t("التغير بالنقاط المئوية", "Percentage-point change"), f"{after_score-before_score:+.1f}")
        plot_data = pd.DataFrame(
            {"Stage": [t("الأصلي", "Original"), t("السيناريو", "Scenario")],
             "Model score": [before_score, after_score]}
        ).set_index("Stage")
        st.bar_chart(plot_data, horizontal=True, color="#6168c5", height=180)
        if not (add_projects or add_internships or add_programming):
            st.info(t("عدّل إحدى القيم أعلاه لعرض مقارنة السيناريو.", "Change a value above to compare outcomes."))
        else:
            st.markdown(
                '<div class="f-note">' +
                t("هاي محاكاة لنفس النموذج، مش وعد إنه التدريبات أو المشاريع رح ترفع فرص التوظيف فعليًا. ممكن المؤشر ما يرتفع حتى لو زادت بعض المهارات.",
                  "This is an exploratory model simulation, not evidence that adding a project or internship causes employment. The score may not always increase.") +
                '</div>', unsafe_allow_html=True
            )
        export_original, export_scenario = st.columns(2)
        with export_original:
            st.download_button(
                t(" نزّل ملفك الأصلي CSV", " Download original profile"),
                pd.DataFrame([profile]).to_csv(index=False).encode("utf-8-sig"),
                file_name="fursa_profile.csv", mime="text/csv",
                key="original_export", width="stretch",
            )
        with export_scenario:
            st.download_button(
                t(" نزّل السيناريو CSV", " Download scenario CSV"),
                pd.DataFrame([scenario]).to_csv(index=False).encode("utf-8-sig"),
                file_name="fursa_scenario.csv", mime="text/csv",
                key="scenario_export", width="stretch",
            )


with science_tab:
    section("04", t("أداء النموذج والتحليل", "Model performance & evaluation"),
            t("نتائج محسوبة من ملفات التجربة الفعلية، مع مخططات التدريب التي تم حفظها أثناء تطوير المشروع.",
              "Results computed from the saved experiment artifacts, together with original training visualizations."))

    metrics_path = ROOT / "metrics.json"
    try:
        archived_metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        archived_metrics = {}
    threshold = float(archived_metrics.get("threshold", 0.5))

    from model_report import evaluate_saved_split

    @st.cache_data(show_spinner=False)
    def report_from_artifacts(root_dir, threshold_value, artifact_signature):
        return evaluate_saved_split(root_dir, threshold_value)

    files_to_check = [
        ROOT / "milestone3_outputs" / filename
        for filename in ["X_test.csv", "y_test.csv", "best_placement_model_monotonic_english.pkl"]
    ]
    report = None
    if all(f.exists() for f in files_to_check):
        signature = tuple((f.stat().st_size, f.stat().st_mtime_ns) for f in files_to_check)
        try:
            report = report_from_artifacts(str(ROOT), threshold, signature)
        except (ValueError, OSError, KeyError) as exc:
            st.warning(t("تعذر حساب بعض مقاييس الاختبار من الملفات المحفوظة.",
                         "Some evaluation metrics could not be calculated from the saved files."))
    else:
        st.warning(t("ملفات الاختبار المحفوظة غير مكتملة.", "The stored evaluation files are incomplete."))

    model_name = archived_metrics.get("model", "LogisticRegression")
    monotonic_meta_path = ROOT / "english_monotonicity_audit.json"
    monotonic_meta = {}
    if monotonic_meta_path.exists():
        try:
            monotonic_meta = json.loads(monotonic_meta_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            monotonic_meta = {}
    st.markdown(
        f'<div class="f-report-head"><div><span class="f-report-eyebrow">MODEL EVALUATION</span>'
        f'<h3>{model_name.replace("LogisticRegression", "Logistic Regression")}</h3>'
        f'<p>{t("نموذج التصنيف المستخدم في الموقع", "Classifier used for application predictions")}</p></div>'
        f'<div class="f-report-data"><strong>{threshold:.2f}</strong>'
        f'<span>{t("عتبة التصنيف", "Decision threshold")}</span></div></div>',
        unsafe_allow_html=True,
    )

    if report:
        a, b, c, e = st.columns(4)
        a.metric("Accuracy", f"{report['accuracy']:.1%}")
        b.metric("Balanced Accuracy", f"{report['balanced_accuracy']:.1%}")
        c.metric("Macro F1", f"{report['macro_f1']:.1%}")
        e.metric("ROC AUC", f"{report['roc_auc']:.1%}")
        st.caption(
            t(f"إعادة حساب مباشرة من النموذج المحفوظ وبيانات الاختبار المتوفرة ({report['samples']:,} سجل). "
              "هذه المجموعة استخدمت خلال تطوير المشروع وليست تقييمًا خارجيًا مستقلًا.",
              f"Recomputed from the saved classifier and available test files ({report['samples']:,} records). "
              "This split was used during development and is not independent external validation.")
        )

        st.markdown("### " + t("مصفوفة الالتباس", "Confusion matrix"))
        matrix_col, explanation_col = st.columns([1.45, 1], gap="large", vertical_alignment="center")
        with matrix_col:
            cm = report["cm"]
            fig, ax = plt.subplots(figsize=(6.2, 4.1))
            fig.patch.set_facecolor("#ffffff")
            im = ax.imshow(cm, cmap="Blues")
            max_count = max(max(row) for row in cm)
            for i in range(2):
                for j in range(2):
                    ax.text(j, i, f"{cm[i][j]:,}", ha="center", va="center",
                            fontsize=17, weight="bold",
                            color="white" if cm[i][j] > max_count * .50 else "#233654")
            ax.set_xticks([0, 1], ["Not Placed", "Placed"])
            ax.set_yticks([0, 1], ["Not Placed", "Placed"])
            ax.set_xlabel("Predicted class", labelpad=12, color="#64748b")
            ax.set_ylabel("Actual class", labelpad=12, color="#64748b")
            ax.tick_params(axis="both", length=0, labelsize=10)
            for spine in ax.spines.values():
                spine.set_visible(False)
            fig.tight_layout(pad=1.8)
            st.pyplot(fig, width="stretch")
            plt.close(fig)
        with explanation_col:
            st.markdown(
                '<div class="f-matrix-summary"><span>CLASS RECALL</span>'
                f'<div class="f-matrix-row"><div>{t("فئة غير متوظف", "Not Placed")}</div>'
                f'<strong>{report["recall_not_placed"]:.1%}</strong></div>'
                f'<div class="f-matrix-row"><div>{t("فئة متوظف", "Placed")}</div>'
                f'<strong>{report["recall_placed"]:.1%}</strong></div>'
                '<p>' +
                t("توضح المصفوفة التوقعات الصحيحة والخاطئة لكل فئة، باستخدام عتبة التصنيف المحددة للنموذج. "
                  "توازن الاستدعاء بين الفئتين مهم عند اختلاف أحجامهما.",
                  "The matrix shows correct and incorrect predictions for each class using the selected decision threshold. "
                  "Class-wise recall helps evaluate performance beyond overall accuracy.") +
                '</p></div>',
                unsafe_allow_html=True,
            )
        st.caption(t("تم توليد هذه المصفوفة من النموذج المحفوظ وملفات الاختبار الحالية، وليست صورة تجريبية عامة.",
                     "This matrix was generated from the current saved model and test split."))

    st.markdown("### " + t("مخططات نتائج التدريب", "Training & analysis visualizations"))
    st.caption(t("الرسومات أدناه ناتجة عن ملفات المشروع الأصلية، وليست رسومات توضيحية من الإنترنت.",
                 "These are the original visual outputs saved with the project—not stock charts."))
    gallery = [
        (
            "09_learning_curve.png",
            t("منحنى التعلم", "Learning curve"),
            t("مقارنة التدريب والتحقق مع تغير حجم بيانات التدريب.",
              "Training and validation performance across dataset sizes."),
        ),
        (
            "10_feature_importance.png",
            t("مساهمة الخصائص في النموذج", "Model feature importance"),
            t("مخطط محفوظ من تحليل Logistic Regression. لا يثبت وجود علاقة سببية.",
              "Saved Logistic Regression analysis; not evidence of causality."),
        ),
        (
            "09_improvement_comparison.png",
            t("مقارنة مقاييس النسخة المتوازنة", "Balanced model summary"),
            t("ملخص بصري محفوظ من التجربة السابقة.",
              "Visual summary preserved from the earlier experiment."),
        ),
        (
            "02_skills_and_placement.png",
            t("العلاقة الوصفية بين المهارات وبيانات التوظيف", "Skills and placement patterns"),
            t("استكشاف وصفي للداتا، وليس تفسيرًا لقرار النموذج.",
              "Descriptive exploration, not a direct explanation of a model decision."),
        ),
    ]
    for index in range(0, len(gallery), 2):
        group = st.columns(2, gap="large")
        for column, item in zip(group, gallery[index:index + 2]):
            filename, title, description = item
            image_file = ROOT / "milestone3_outputs" / filename
            with column:
                with st.container(border=True):
                    st.markdown("#### " + title)
                    if image_file.exists():
                        st.image(str(image_file), width="stretch")
                        st.caption(description)
                    else:
                        st.caption(t("الرسم غير متوفر في مجلد المشروع.",
                                     "The saved chart file is unavailable."))

    comparison_path = ROOT / "model_comparison.csv"
    if comparison_path.exists():
        model_table = pd.read_csv(comparison_path)
        required = {"Model", "CV Accuracy", "CV Balanced Accuracy", "CV Macro F1"}
        if required.issubset(model_table.columns):
            st.markdown("### " + t("مقارنة الخوارزميات", "Algorithm comparison"))
            st.caption(t("مقارنة نتائج التحقق المتقاطع المحفوظة لجميع الخوارزميات التي تم اختبارها.",
                         "Stored cross-validation results for the evaluated algorithms."))
            selected_metric = st.selectbox(
                t("مقياس المقارنة", "Comparison metric"),
                ["CV Balanced Accuracy", "CV Macro F1", "CV Accuracy"],
                index=0,
            )
            chart = model_table[["Model", selected_metric]].copy()
            aliases = {
                "LogisticRegression": "Logistic Regression",
                "RandomForestClassifier": "Random Forest",
                "DecisionTreeClassifier": "Decision Tree",
                "KNeighborsClassifier": "KNN",
            }
            chart["Model"] = chart["Model"].replace(aliases)
            chart[selected_metric] = pd.to_numeric(chart[selected_metric], errors="coerce")
            chart = chart.dropna().sort_values(selected_metric)
            fig, ax = plt.subplots(figsize=(9.1, 4.0))
            fig.patch.set_facecolor("white")
            colors = ["#335b9f" if name == "Logistic Regression" else "#a8b5ca"
                      for name in chart["Model"]]
            bars = ax.barh(chart["Model"], chart[selected_metric] * 100,
                           color=colors, height=.56)
            ax.bar_label(bars, fmt="%.1f%%", padding=7, fontsize=13)
            ax.set_xlim(0, 100)
            ax.set_xlabel("")
            ax.spines[["top", "right", "left"]].set_visible(False)
            ax.tick_params(axis="y", length=0, labelsize=13)
            ax.tick_params(axis="x", labelsize=12, colors="#52657f")
            ax.grid(axis="x", color="#e4eaf2", alpha=.8)
            ax.set_axisbelow(True)
            fig.subplots_adjust(left=0.25, right=0.91, top=0.96, bottom=0.18)
            st.pyplot(fig, width="stretch")
            plt.close(fig)
            st.markdown(
                '<div class="f-chart-axis-label">' +
                t("نتيجة التحقق المتقاطع (%)", "Cross-validation score (%)") +
                '</div>', unsafe_allow_html=True
            )
            with st.expander(t("عرض جدول المقارنة الكامل", "View the full comparison table")):
                table = model_table.drop(columns=["Parameters"], errors="ignore")
                st.dataframe(table, hide_index=True, width="stretch")

    with st.expander(t("منهجية التقييم ومصدر الأرقام", "Evaluation methodology & provenance")):
        st.markdown(t(
            "**النموذج المعتمد:** Logistic Regression، مع اختيار يعتمد على Balanced Accuracy. "
            "**البيانات:** ملفات الاختبار المحفوظة داخل المشروع. "
            "**العتبة:** تؤخذ من metrics.json. "
            "هذه النتائج لا تمثل اختبارًا خارجيًا جديدًا أو ضمانًا لصحة التوقع على الخريجين الفعليين.",
            "**Final model:** Logistic Regression; selection emphasized Balanced Accuracy. "
            "**Data:** the existing saved test split. "
            "**Threshold:** loaded from metrics.json. "
            "These values are not fresh external validation or a guarantee on real-world applicants."
        ))
        if monotonic_meta:
            st.markdown("**" + t("معالجة ترتيب مستويات الإنجليزية",
                                "English-level monotonicity constraint") + "**")
            st.write(t(
                "تمت إعادة ملاءمة نموذج Logistic Regression باستخدام مجموعة التدريب المحفوظة فقط، "
                "مع قيد معلن يجعل معامل مستوى الإنجليزية موجبًا. "
                "لذلك، عند ثبات باقي المدخلات، لا ينخفض المؤشر عند الانتقال من أساسي إلى متوسط إلى متقدم. "
                "هذا قرار تصميمي مبني على افتراض منطقي، وليس دليلًا على تأثير سببي للغة على التوظيف.",
                "Logistic Regression was refitted using only the saved training split, "
                "with a documented positive coefficient constraint for English proficiency. "
                "Holding every other input constant, moving from Basic to Intermediate to Advanced "
                "cannot reduce the model score. This is an explicit domain assumption, not a causal finding."
            ))
            comparison = monotonic_meta.get("model_comparison", {})
            original = comparison.get("original", {})
            updated = comparison.get("monotonic_english", {})
            if original and updated:
                st.dataframe(pd.DataFrame([
                    {
                        "Version": t("النموذج السابق", "Original model"),
                        "Balanced Accuracy": original["balanced_accuracy"],
                        "Macro F1": original["macro_f1"],
                        "ROC AUC": original["roc_auc"],
                    },
                    {
                        "Version": t("النموذج الحالي", "Current model"),
                        "Balanced Accuracy": updated["balanced_accuracy"],
                        "Macro F1": updated["macro_f1"],
                        "ROC AUC": updated["roc_auc"],
                    },
                ]), hide_index=True, width="stretch")
                st.caption(t(
                    "المقارنة أعلاه على مجموعة اختبار راجعناها خلال التطوير، ولا تمثل تحققًا خارجيًا مستقلًا.",
                    "Comparison uses a previously reviewed test split, not independent external validation."
                ))
        if archived_metrics:
            old_count = int(archived_metrics.get("test_rows", 0))
            if report and old_count != report["samples"]:
                st.write(t(
                    f"ملاحظة توثيقية: يسجل ملف metrics.json عدد {old_count:,} عينة، "
                    f"بينما ملفات X_test وy_test الحالية تحتوي {report['samples']:,} عينة. "
                    "لذلك عُرضت المقاييس المعاد حسابها من الملفات الحالية بشكل منفصل.",
                    f"Provenance note: metrics.json records {old_count:,} test rows, "
                    f"while the current X_test and y_test contain {report['samples']:,}. "
                    "The headline metrics above are freshly recomputed from the current saved files."
                ))
            st.write(t(
                f"نتيجة التحقق المتداخل المحفوظة (Balanced Accuracy): "
                f"{archived_metrics.get('nested_balanced_accuracy', 0):.1%}.",
                f"Archived nested validation Balanced Accuracy: "
                f"{archived_metrics.get('nested_balanced_accuracy', 0):.1%}."
            ))
        st.caption(t(
            "الصور المحفوظة من النوتبوك قد تمثل مراحل تدريب أو إعدادات مختلفة؛ "
            "لا تُستخدم لاشتقاق المقاييس المعاد حسابها أعلاه.",
            "Notebook figures may represent separate training runs or settings; "
            "they are not used to derive the recomputed metrics above."
        ))

    st.markdown("### " + t("حدود الاستخدام", "Important limitations"))
    st.markdown(
        '<div class="f-note">' +
        t("النظام أداة تعليمية لاستكشاف الأنماط في البيانات، وليس نظامًا لاتخاذ قرارات التوظيف. "
          "مؤشر فئة التوظيف غير معاير كاحتمال فعلي. فجوات المهارات مبنية على أهداف تعليمية تقريبية، "
          "والمحاكاة لا تثبت أي تأثير سببي. لم يُثبت تمثيل هذه البيانات لسوق العمل الأردني.",
          "This is an educational data exploration tool, not a hiring decision system. "
          "The Placed-class score is not a calibrated probability. Skill gaps use illustrative targets, "
          "and simulation changes are not causal. The data is not verified as representative of Jordan's labor market.") +
        '</div>', unsafe_allow_html=True
    )
    if report:
        data = pd.DataFrame([{
            "Model": model_name, "Threshold": threshold, "Test rows": report["samples"],
            "Accuracy": report["accuracy"], "Balanced Accuracy": report["balanced_accuracy"],
            "Macro F1": report["macro_f1"], "ROC AUC": report["roc_auc"],
            "Not Placed Recall": report["recall_not_placed"],
            "Placed Recall": report["recall_placed"],
        }])
        st.download_button(t("تصدير تقرير التقييم CSV", "Export evaluation CSV"),
                           data.to_csv(index=False).encode("utf-8-sig"),
                           file_name="fursa_model_evaluation.csv", mime="text/csv")

st.markdown(
    f'<div class="f-footer">FURSA AI · '
    f'{t("تقييم مهني استكشافي مبني على البيانات", "Exploratory career insights backed by data")}'
    f'<br>{t("نموذج تعليمي، لا يمثل ضمانًا للتوظيف", "Educational prototype — not a job guarantee")}</div>',
    unsafe_allow_html=True,
)
