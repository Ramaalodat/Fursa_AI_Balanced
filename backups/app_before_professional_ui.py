from pathlib import Path
import json

import joblib
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="فرصة AI | Fursa AI",
    page_icon="🐣",
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
        st.write("🐣")

def panel(title, body, kicker="✦"):
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
st.markdown("<style>" + css + "</style>", unsafe_allow_html=True)

brand, change_lang, preferences = st.columns([5.5, 1.25, 1.25], vertical_alignment="center")
with brand:
    st.markdown(
        '<div class="f-top"><div class="f-logo">✦</div><div>'
        '<strong>فرصة <span class="f-logo-word">AI</span><span class="f-status">FURSA LAB</span></strong>'
        '<small>Career clarity · Skills growth · Realistic ML insights</small></div></div>',
        unsafe_allow_html=True,
    )
with change_lang:
    st.selectbox(
        "Language / اللغة", ["العربية", "English"],
        key="ui_lang", label_visibility="collapsed",
    )
with preferences:
    with st.popover(t("⚙️ إعدادات", "⚙️ Settings")):
        st.markdown("#### " + t("تفضيلات الموقع", "Display preferences"))
        st.toggle(t("تقليل الحركة", "Reduce motion"), key="reduce_motion")
        st.toggle(t("عرض مدمج", "Compact spacing"), key="compact_layout")
        st.divider()
        if st.button(t("مسح التقييم وإعادة البدء", "Reset assessment"), key="reset_all"):
            st.session_state.pop("fursa_profile", None)
            for key in list(st.session_state.keys()):
                if key.startswith("task_done_") or key.startswith("sim_"):
                    del st.session_state[key]
            st.rerun()
        st.caption(t("يتم حفظ التفضيلات ونتيجة التقييم في الجلسة الحالية فقط.",
                     "Preferences and assessment are kept only in this session."))

hero_text, hero_mascot = st.columns([1.65, 1], vertical_alignment="center")
with hero_text:
    st.markdown(
        f'<div class="f-hero"><span class="f-eyebrow">{t("رحلتك المهنية بتبدأ من هون ✨","YOUR GROWTH STARTS HERE ✨")}</span>'
        f'<h1>{t("اكتشف مهاراتك، وابنِ فرصتك الجاية.", "Discover your strengths. Build your next opportunity.")}</h1>'
        f'<p>{t("جاوب عن 10 أسئلة بسيطة، وخلي فرصة AI يساعدك تفهم ملفك، تحدد أولويات تطويرك، وتجرب أثر التغييرات على مؤشر النموذج.",
                   "Answer 10 simple questions to explore your profile, spot learning priorities and experiment with changes to the model score.")}</p>'
        f'<div class="f-tags"><span>✓ {t("تحليل ذكي","Model insights")}</span><span>✦ {t("خطة مخصصة","Personal learning plan")}</span>'
        f'<span>↗ {t("محاكاة تفاعلية","What-if explorer")}</span></div></div>',
        unsafe_allow_html=True,
    )
with hero_mascot:
    mascot("graduate", 340)

st.markdown(
    f'<div class="f-stepstrip">'
    f'<div class="f-step"><i>1</i>{t("أدخل مهاراتك","Add your skills")}</div><span class="f-separator">→</span>'
    f'<div class="f-step"><i>2</i>{t("اعرف مؤشر النموذج","See model insights")}</div><span class="f-separator">→</span>'
    f'<div class="f-step"><i>3</i>{t("خطط للتطوير","Create your plan")}</div><span class="f-separator">→</span>'
    f'<div class="f-step"><i>4</i>{t("جرّب التحسين","Try improvements")}</div>'
    f'</div>',
    unsafe_allow_html=True,
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
    "Resume_Score": ("تقييم السيرة الذاتية (من 100)", "Resume self-rating (out of 100)"),
    "Interview_Score": ("تقييم المقابلة (من 100)", "Interview self-rating (out of 100)"),
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
    "explore": ("لسا بستكشف مجالي", "Still exploring"),
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

model_path = ROOT / "milestone3_outputs" / "best_placement_model.pkl"
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
    t("🐣 قيّم ملفك", "🐣 Assess your profile"),
    t("🧩 خطتك والمهارات", "🧩 Skills & action plan"),
    t("🚀 جرّب التحسين", "🚀 What-if lab"),
    t("📊 عن الموديل", "📊 About the model"),
])

with profile_tab:
    section("01", t("خلينا نتعرف على مهاراتك", "Let's explore your profile"),
            t("جاوب بواقعية؛ الهدف نفهم نقاط قوتك وأولويات تطويرك.", "Use realistic estimates so your learning priorities make sense."))
    intro, intro_pic = st.columns([3, 1], vertical_alignment="center")
    with intro:
        panel(
            t("بطوط جاهز يساعدك!", "Your duck buddy is ready!"),
            t("عبّي المعلومات، وبعدها رح تشوف مؤشر النموذج، ونقاط القوة، والأشياء اللي ممكن تطورها.",
              "Complete the form to explore the model output, your strengths, and possible growth areas."),
            "✦ FURSA AI"
        )
    with intro_pic:
        mascot("assessment", 225)

    with st.form("career_form"):
        career_goal = st.selectbox(
            t("مجال اهتمامك (للتوصيات فقط — لا يدخل للموديل)",
              "Your direction (for learning tips only — not a model input)"),
            list(CAREER_GOALS),
            format_func=lambda goal: t(*CAREER_GOALS[goal]),
        )
        academics, experience, professional = st.columns(3)
        inputs = {"Career_Goal": career_goal}
        with academics:
            st.markdown("#### " + t("🎓 الدراسة والمهارات", "🎓 Academic & tech"))
            inputs["CGPA"] = st.slider(label("CGPA"), 2.0, 4.0, 3.10, 0.01, help=t("المقياس المستخدم في بيانات التدريب هو من 4.", "Training uses a 4-point GPA scale."))
            inputs["Programming_Skill"] = st.slider(label("Programming_Skill"), 1, 10, 6)
            inputs["Problem_Solving"] = st.slider(label("Problem_Solving"), 1, 10, 6)
            inputs["English_Proficiency"] = st.selectbox(
                label("English_Proficiency"),
                ["Basic", "Intermediate", "Advanced"], index=1,
                format_func=lambda x: {"Basic": t("أساسي", "Basic"),
                                       "Intermediate": t("متوسط", "Intermediate"),
                                       "Advanced": t("متقدم", "Advanced")}[x]
            )
        with experience:
            st.markdown("#### " + t("💻 الخبرة والتطبيق", "💻 Practical experience"))
            inputs["Projects_Completed"] = st.number_input(label("Projects_Completed"), min_value=0, max_value=15, value=2, step=1)
            inputs["Internships"] = st.number_input(label("Internships"), min_value=0, max_value=5, value=0, step=1)
            inputs["Certifications"] = st.number_input(label("Certifications"), min_value=0, max_value=10, value=1, step=1)
        with professional:
            st.markdown("#### " + t("🤝 الجاهزية المهنية", "🤝 Professional skills"))
            inputs["Communication_Skills"] = st.slider(label("Communication_Skills"), 1, 10, 6)
            inputs["Resume_Score"] = st.slider(label("Resume_Score"), 0, 100, 65,
                help=t("تقييم تقريبي منك، مش تحليل آلي للسيرة الذاتية.", "Your estimate, not an automated CV audit."))
            inputs["Interview_Score"] = st.slider(label("Interview_Score"), 0, 100, 65,
                help=t("تقييم تقريبي، مش نتيجة مقابلة حقيقية.", "Your estimate, not a real interview assessment."))
        st.caption(t("المعلومات بتظل داخل جلسة الموقع الحالية؛ التنزيل بيكون فقط لما تضغط عليه.",
                     "Your entries remain in this app session; nothing downloads unless you choose to export."))
        submitted = st.form_submit_button(t("✨ حلّل ملفّي", "✨ Analyse my profile"), type="primary", width="stretch")
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
            tone = t("ملفك فيه إشارات إيجابية ضمن بيانات التدريب", "Your inputs align positively with the training patterns")
            mood = "success"
        elif result >= 45:
            tone = t("في جوانب قوية وفرص تطوير إضافية", "There are strengths and opportunities to grow")
            mood = "assessment"
        else:
            tone = t("ابدأ بخطوات صغيرة ومنتظمة", "Small, consistent steps are a great place to start")
            mood = "tea"

        section("02", t("هاي نتيجتك", "Here's your model result"),
                t("النتيجة مرتبطة بنموذجنا التدريبي، وليست نسبة توظيف مؤكدة.", "This is a model output, not a verified chance of employment."))
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
            f'<div class="f-grid"><div class="f-stat"><span>{t("نقاط حققت هدف التطوير","Targets met")}</span><strong>{len(strengths)} / {len(TARGETS)}</strong><small>{t("أهداف تعليمية توضيحية","Illustrative learning targets")}</small></div>'
            f'<div class="f-stat"><span>{t("أولويات يمكن تحسينها","Growth areas")}</span><strong>{len(gaps)}</strong><small>{t("حسب القيم اللي أدخلتها","Based on entered values")}</small></div>'
            f'<div class="f-stat"><span>{t("أفضل خطوة تبدأ فيها","Suggested first step")}</span><strong style="font-size:17px">{start_here}</strong><small>{t("من خطة مهاراتك","From your learning plan")}</small></div></div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="f-note">' +
            t("💡 اضغط على تبويب «خطتك والمهارات» لتشوف الأولويات العملية، وبعدها جرّب محاكاة التحسين. حدود المهارات المستخدمة أمثلة تعليمية مش معايير توظيف رسمية.",
              "💡 Open 'Skills & action plan' to see next steps, then try the what-if lab. Skill thresholds are illustrative, not verified hiring requirements.") +
            '</div>', unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<div class="f-note">' +
            t("🐣 أول ما تحلّل ملفك رح تظهر هون النتائج وخطة واضحة تكمل فيها.", "🐣 Your results and recommended next steps will appear here after you submit.") +
            '</div>', unsafe_allow_html=True,
        )

with plan_tab:
    if "fursa_profile" not in st.session_state:
        section("02", t("خلينا نبدأ من تقييمك", "Start with an assessment"),
                t("عبّي البيانات أولاً بتبويب التقييم حتى نقدر نجهز خطة خاصة بملفك.", "Fill in the assessment first to see your learning plan."))
        mascot("detective", 285)
    else:
        profile = st.session_state["fursa_profile"]
        strengths, gaps = analyze_skills(profile)
        section("03", t("بطوط اكتشف نقاط قوتك", "Your skills under the magnifying glass"),
                t("مقارنة مع أهداف تعليمية مقترحة، وليست تفسيرًا سببيًا من النموذج.",
                  "A comparison with illustrative learning targets, not a causal explanation from the model."))
        info, pic = st.columns([3, 1], vertical_alignment="center")
        with info:
            panel(
                t("آهاا! عرفت وين ممكن تتطور!", "Aha! Here's where you can grow!"),
                t("الهدف نستخدم نتيجة الملف لنعمل خطوات واضحة قابلة للتنفيذ، مش بس نطلع رقم.",
                  "The goal is to turn your inputs into concrete next steps, not just a number."),
                "🔍 SKILLS DETECTIVE"
            )
        with pic:
            mascot("detective", 240)
        good_col, next_col = st.columns(2)
        with good_col:
            with st.container(border=True):
                st.markdown("#### " + t("💚 جوانب قوية", "💚 Targets you meet"))
                if not strengths:
                    st.write(t("لسا في مجال نشتغل عليه، وهذا طبيعي.", "There's plenty of room to develop."))
                for key in strengths:
                    st.markdown(f'<div class="f-skill f-skill-good"><span>{label(key)}</span><b>{profile[key]} / {TARGETS[key]}</b></div>', unsafe_allow_html=True)
        with next_col:
            with st.container(border=True):
                st.markdown("#### " + t("💜 أولويات التطوير", "💜 Areas to work on"))
                if not gaps:
                    st.write(t("حققت كل الأهداف التعليمية المدرجة!", "You meet all the illustrative learning targets!"))
                for key in gaps:
                    st.markdown(f'<div class="f-skill"><span>{label(key)}</span><b>{profile[key]} / {TARGETS[key]}</b></div>', unsafe_allow_html=True)

        section("04", t("خطة بسيطة تمشي عليها", "Your practical action plan"),
                t("ابدأ بأول ثلاث أولويات، وكل خطوة معها تطبيق عملي.",
                  "Focus on up to three priorities, each with a concrete action."))
        priority_keys = gaps[:3] if gaps else ["Projects_Completed", "Interview_Score"]
        for i, key in enumerate(priority_keys, 1):
            st.markdown(
                f'<div class="f-action"><div class="f-index">{i:02d}</div><div><strong>{label(key)}</strong>'
                f'<p>{t(*ADVICE[key])}</p><small>{t("✓ خطوة قابلة للتطبيق","✓ Practical next step")}</small></div></div>',
                unsafe_allow_html=True,
            )
        st.markdown("#### " + t("🌱 فكرة مشروع تناسب هدفك", "🌱 A portfolio idea for your direction"))
        chosen_goal = profile.get("Career_Goal", "explore")
        panel(t(*CAREER_GOALS.get(chosen_goal, CAREER_GOALS["explore"])),
              t(*PROJECT_IDEAS.get(chosen_goal, PROJECT_IDEAS["explore"])),
              "PORTFOLIO STARTER")
        st.markdown("#### " + t("☑️ تابع تقدمك", "☑️ Track your progress"))
        with st.container(border=True):
            done = 0
            for key in priority_keys:
                finished = st.checkbox(
                    t("أنجزت خطوة: ", "Completed: ") + label(key),
                    key="task_done_" + key,
                )
                done += int(finished)
            st.markdown(f"**{t('الخطوات المكتملة', 'Completed steps')}: {done} / {len(priority_keys)}**")
            st.progress(done / len(priority_keys))
            st.caption(t("المتابعة بتظل محفوظة خلال جلسة الموقع فقط.",
                         "This checklist is stored only during the current session."))
        report_lines = [
            t("فرصة AI — خطة تطوير شخصية", "FURSA AI — Personal Learning Plan"),
            t("مؤشر النموذج: ", "Model score: ") + f"{predict_score(profile):.1f}%",
            t("الرقم ليس احتمال توظيف معايرًا أو ضمانًا بوظيفة.",
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
            t("⬇️ نزّل خطتك كملف نصي", "⬇️ Download your learning plan"),
            "\n".join(report_lines).encode("utf-8"),
            file_name="fursa_learning_plan.txt",
            mime="text/plain",
        )

with simulation_tab:
    if "fursa_profile" not in st.session_state:
        section("05", t("المختبر بستنّى تقييمك", "Your what-if lab is waiting"),
                t("ابدأ بتقييم ملفك حتى نقدر نقارن المؤشر قبل وبعد.", "First assess your profile so we can compare before and after."))
        mascot("coder", 290)
    else:
        profile = st.session_state["fursa_profile"]
        before_score = predict_score(profile)
        section("05", t("شو بصير لو حسّنت مهاراتك؟", "What if you improved your skills?"),
                t("جرّب قيم افتراضية بدون ما تغيّر ملفك الأصلي.", "Try hypothetical changes without modifying your original profile."))
        expl, pic = st.columns([3, 1], vertical_alignment="center")
        with expl:
            panel(
                t("استناني شوي، بحلل مستقبلك!", "Let's try a few possibilities!"),
                t("زِد مشاريع أو تدريب أو مستوى برمجة وشوف كيف بتتغير استجابة النموذج.",
                  "Add hypothetical projects, internships or programming experience to see how the model responds."),
                "🧪 WHAT-IF LAB"
            )
        with pic:
            mascot("coder", 245)
        x, y, z = st.columns(3)
        with x:
            add_projects = st.slider(t("مشاريع جديدة", "Extra projects"), 0, 3, 0, key="sim_projects")
        with y:
            add_internships = st.slider(t("تدريبات جديدة", "Extra internships"), 0, 2, 0, key="sim_internships")
        with z:
            add_programming = st.slider(t("تطوير البرمجة", "Programming improvement"), 0, 3, 0, key="sim_programming")
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
            st.info(t("حرّك أي شريط عشان تشوف الفرق ✨", "Move a slider to see the comparison ✨"))
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
                t("⬇️ نزّل ملفك الأصلي CSV", "⬇️ Download original profile"),
                pd.DataFrame([profile]).to_csv(index=False).encode("utf-8-sig"),
                file_name="fursa_profile.csv", mime="text/csv",
                key="original_export", width="stretch",
            )
        with export_scenario:
            st.download_button(
                t("⬇️ نزّل السيناريو CSV", "⬇️ Download scenario CSV"),
                pd.DataFrame([scenario]).to_csv(index=False).encode("utf-8-sig"),
                file_name="fursa_scenario.csv", mime="text/csv",
                key="scenario_export", width="stretch",
            )

with science_tab:
    section("06", t("كيف بيشتغل فرصة AI؟", "How does Fursa AI work?"),
            t("نفس فكرة المشروع بس بشرح بسيط ونتائج واضحة.", "The project explained with a simple and transparent flow."))
    flow_a, flow_b, flow_c = st.columns(3)
    with flow_a:
        panel(t("1 · البيانات", "1 · Inputs"),
              t("10 مدخلات عن الدراسة والمهارات والتطبيق العملي.",
                "10 inputs covering academics, skills and practical work."), "🧾")
    with flow_b:
        panel(t("2 · نموذج ML", "2 · ML model"),
              t("Preprocessing وميزات مشتقة، وبعدها نموذج تصنيف محفوظ.",
                "Preprocessing, engineered features and a saved classifier."), "⚙️")
    with flow_c:
        panel(t("3 · خطة ومحاكاة", "3 · Plan & simulator"),
              t("نقاط قوة وأولويات تعليمية، وتجربة تغييرات افتراضية.",
                "Illustrative learning priorities and hypothetical changes."), "🧩")

    metrics_path = ROOT / "metrics.json"
    metrics = {}
    if metrics_path.exists():
        try:
            metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
        except (ValueError, OSError):
            st.warning(t("لم نتمكن من قراءة ملف المقاييس.", "Could not load the evaluation metrics."))
    if metrics:
        st.markdown("### " + t("📈 نتائج التقييم المحفوظة", "📈 Saved evaluation results"))
        p1, p2, p3, p4 = st.columns(4)
        p1.metric("Test accuracy", f"{metrics.get('test_accuracy',0)*100:.1f}%")
        p2.metric("Balanced accuracy", f"{metrics.get('balanced_accuracy',0)*100:.1f}%")
        p3.metric("Macro F1", f"{metrics.get('macro_f1',0)*100:.1f}%")
        p4.metric("ROC AUC", f"{metrics.get('roc_auc',0)*100:.1f}%")
        st.caption(t("الأرقام من ملف metrics.json الخاص بتجربة التدريب؛ الاختبار سبق استخدامه أثناء التطوير ولا يمثل تحققًا خارجيًا جديدًا.",
                     "Figures come from the saved metrics.json. The test set was reviewed during development and is not a fresh external validation."))
    comparison_path = ROOT / "model_comparison.csv"
    if comparison_path.exists():
        comp = pd.read_csv(comparison_path)
        if {"Model", "CV Accuracy", "CV Balanced Accuracy", "CV Macro F1"}.issubset(comp.columns):
            st.markdown("### " + t("⚖️ مقارنة الخوارزميات", "⚖️ Compare algorithms"))
            selected_metric = st.selectbox(
                t("اختار مقياس المقارنة", "Choose a comparison metric"),
                ["CV Balanced Accuracy", "CV Accuracy", "CV Macro F1"],
                index=0,
            )
            simplified = comp[["Model", selected_metric]].copy()
            simplified["Model"] = simplified["Model"].replace({
                "LogisticRegression": "Logistic Regression",
                "RandomForestClassifier": "Random Forest",
                "DecisionTreeClassifier": "Decision Tree",
                "KNeighborsClassifier": "KNN",
            })
            simplified[selected_metric] = pd.to_numeric(simplified[selected_metric], errors="coerce")
            simplified = simplified.sort_values(selected_metric)
            fig, ax = plt.subplots(figsize=(9, 3.3))
            fig.patch.set_facecolor("#fcfbff")
            bars = ax.barh(simplified["Model"], simplified[selected_metric] * 100,
                           color="#8067d6", height=.58)
            ax.bar_label(bars, fmt="%.1f%%", padding=5)
            ax.set_xlim(0, 100)
            ax.set_xlabel(t("نتيجة التحقق المتقاطع (%)", "Cross-validation score (%)"))
            ax.spines[["top", "right", "left"]].set_visible(False)
            ax.grid(axis="x", alpha=.12)
            ax.set_axisbelow(True)
            fig.tight_layout()
            st.pyplot(fig, width="stretch")
            plt.close(fig)
            with st.expander(t("شوف الجدول الكامل", "See complete model comparison")):
                st.dataframe(comp, hide_index=True, width="stretch")
    if metrics:
        with st.expander(t("📚 شرح نتائج التقييم بالتفصيل", "📚 Interpreting the saved evaluation")):
            st.write(t(
                f"تم اختيار النموذج بناءً على Balanced Accuracy. التقييم المتداخل داخل بيانات التدريب يساوي {metrics.get('nested_balanced_accuracy', 0):.1%}. "
                "نتائج الاختبار المحفوظة معروضة للتوثيق فقط؛ تم الرجوع لنفس مجموعة الاختبار أثناء التطوير، لذلك لا يمكن اعتبارها تأكيدًا خارجيًا مستقلًا.",
                f"The model was selected using balanced accuracy. Nested validation within training scored {metrics.get('nested_balanced_accuracy', 0):.1%}. "
                "Saved holdout results are reported for documentation: this same test set was reviewed during development, so this is not independent external validation."
            ))
            st.markdown("**Accuracy** · **Balanced Accuracy** · **Macro F1** · **ROC AUC**")
            st.caption(t("مقاييس لتقييم التصنيف على الداتا، وليست قياسًا مباشرًا لمهارات الشخص.",
                         "Dataset-level classification metrics, not a direct measure of a person's ability."))
    metrics_export = json.dumps(metrics, ensure_ascii=False, indent=2).encode("utf-8")
    st.download_button(t("⬇️ نزّل ملف نتائج التجربة JSON", "⬇️ Download experiment metrics JSON"),
                       metrics_export, "fursa_metrics.json", mime="application/json")
    st.markdown("### " + t("🛡️ شو حدود المشروع؟", "🛡️ Important limitations"))
    st.markdown(
        '<div class="f-note">' +
        t("النظام مشروع تعليمي مبني على بيانات تدريب، وليس أداة توظيف رسمية. رقم Placed مستخرج من predict_proba ولكنه غير مثبت كاحتمال توظيف معاير. فجوات المهارات مبنية على قواعد تعليمية مقترحة، وليست تفسيرًا مباشرًا لقرار النموذج. البيانات لا تثبت تمثيل سوق العمل الأردني، والمحاكاة ليست تحليلًا سببيًا.",
          "This is an educational prototype, not an official employment assessment. The Placed-class score comes from predict_proba but has not been established as a calibrated hiring probability. Skill gaps are illustrative rules, not direct model explanations. The dataset is not verified as representative of Jordan's job market and the simulator is not causal.") +
        '</div>', unsafe_allow_html=True,
    )
    st.markdown("### " + t("🎤 كيف تشرح المشروع بالعرض؟", "🎤 Present the project in four steps"))
    st.write(t("**المشكلة:** الخريج مش دايمًا بيعرف من وين يبدأ. **الحل:** بنستخدم بيانات مهاراته مع نموذج ML. **القيمة:** بنعرض مناطق التطوير مع خطوات عملية. **الإضافة التفاعلية:** بنجرب سيناريوهات افتراضية ونوضح حدودها.",
               "**Problem:** graduates may struggle to prioritize skills. **Solution:** apply an ML classifier to user inputs. **Value:** communicate strengths and actionable learning priorities. **Interactive feature:** explore hypothetical changes while explaining limitations."))
    with st.expander(t("🎤 أسئلة ممكن تنسأل عنها وقت المناقشة", "🎤 Questions to prepare for the presentation")):
        st.markdown(t(
            "**ليش Balanced Accuracy؟** لأنها توازن متوسط الاستدعاء بين فئة المتوظفين وغير المتوظفين، حتى ما نعتمد على Accuracy لحالها عند اختلاف أحجام الفئات.\n\n"
            "**هل النتيجة نسبة التوظيف؟** لا؛ هي خرج النموذج من بيانات التجربة وليست احتمالًا معايرًا أو ضمانًا.\n\n"
            "**كيف حددتم Skill Gaps؟** بمقارنة المدخلات بأهداف تعليمية توضيحية محددة مسبقًا، وليس باستخدام Explainable AI أو تفسير مباشر للتوقع.\n\n"
            "**هل المحاكاة تثبت إن زيادة التدريب تسبب التوظيف؟** لا، هي توضح كيف يستجيب النموذج لتغير المدخلات فقط.\n\n"
            "**شو القيمة المضافة؟** جمع التقييم والتوصيات التعليمية والمحاكاة في تجربة واضحة للمستخدم؛ مش الادعاء بتطوير خوارزمية جديدة.\n\n"
            "**شو أكبر محدودية؟** البيانات لم يثبت تمثيلها لسوق العمل الأردني، والاختبار المحفوظ ليس تحققًا خارجيًا جديدًا.",
            "**Why balanced accuracy?** It averages recall across the Placed and Not Placed classes so a majority class does not dominate.\n\n"
            "**Is the number an employment probability?** No; it is an uncalibrated model output, not a hiring guarantee.\n\n"
            "**Where do skill gaps come from?** Illustrative educational thresholds, not a direct ML explanation.\n\n"
            "**Does the what-if tool establish causality?** No; it only demonstrates how the model responds to changed inputs.\n\n"
            "**What's the contribution?** One integrated user experience that combines a classifier, education-oriented next steps, and a transparent simulator.\n\n"
            "**Main limitation?** Dataset representativeness for Jordan is unverified, and the saved test set is not fresh external validation."
        ))
    st.markdown('<div class="f-story"><strong>' + t("طريقة عرض الديمو خلال دقيقة", "One-minute demo flow") + '</strong><p>' +
                t("ابدأ بالمشكلة، أدخل بيانات تجريبية، اشرح معنى المؤشر، اعرض أهم ثلاث خطوات، بعدين غيّر قيمة في المحاكاة. اختم بتوضيح إن النتائج استكشافية.",
                  "Start with the problem, enter a sample profile, explain the score, show three learning actions, change one scenario input, and finish with the limitations.") +
                '</p></div>', unsafe_allow_html=True)

st.markdown(
    f'<div class="f-footer">🐣 FURSA AI · {t("كل مهارة جديدة، خطوة أقرب لفرصتك.","Every new skill brings you one step closer to opportunity.")}'
    f'<br>{t("مشروع تعليمي وتجريبي — مش ضمان توظيف","Educational prototype — not a job guarantee")}</div>',
    unsafe_allow_html=True,
)
