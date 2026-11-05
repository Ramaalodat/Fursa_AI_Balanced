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

ar = st.session_state.ui_lang == "العربية"

def t(arabic, english):
    return arabic if ar else english

def mascot(mood, width=240):
    path = ASSETS / f"duck_{mood}.svg"
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

css = """
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;600;700;800&family=DM+Sans:wght@400;500;600;700;800&display=swap');
:root{--ink:#272344;--muted:#736f8c;--purple:#7056c9;--purple-dark:#4c398e;--mint:#44b7a2;--gold:#f7b94f;--line:#e9e4f4;}
.stApp{background:#fcfbff;color:var(--ink);font-family:'Cairo','DM Sans',Tahoma,sans-serif;}
[data-testid="stHeader"]{background:#fcfbff;}
[data-testid="stMainBlockContainer"]{max-width:1160px;padding-top:4.2rem;padding-bottom:4rem;}
[data-testid="stMarkdownContainer"],[data-testid="stCaptionContainer"],[data-testid="stWidgetLabel"],
[data-testid="stHeadingWithActionElements"],[data-testid="stAlert"],[data-testid="stExpander"]{direction:__DIR__;text-align:__ALIGN__;}
[data-testid="stMarkdownContainer"] p,[data-testid="stWidgetLabel"] p{font-family:'Cairo','DM Sans',Tahoma,sans-serif;line-height:1.85;}
[data-testid="stHorizontalBlock"]{flex-direction:__ROW__;}
[data-testid="stMetric"]{border:1px solid var(--line);background:white;padding:18px;border-radius:18px;box-shadow:0 6px 20px #6953ac0a;}
[data-testid="stMetricValue"]{color:var(--purple-dark)!important;font-weight:800;}
[data-testid="stMetricLabel"]{direction:__DIR__;text-align:__ALIGN__;}
[data-testid="stMetricLabel"] p{white-space:normal!important;}
[data-testid="stForm"],[data-testid="stExpander"],[data-testid="stVerticalBlockBorderWrapper"]{border-radius:20px!important;border-color:var(--line)!important;}
[data-testid="stForm"]{padding:18px 21px;background:white;}
.stTabs [data-baseweb="tab-list"]{direction:__DIR__;gap:5px;border-bottom:1px solid #ece7f5;overflow-x:auto;}
.stTabs [data-baseweb="tab"]{border-radius:12px 12px 0 0;color:#645b82;font-family:'Cairo','DM Sans',Tahoma,sans-serif;padding:0 19px;white-space:nowrap;}
.stTabs [aria-selected="true"]{color:#5d43b1!important;font-weight:800!important;background:#f3efff;}
.stTabs [data-baseweb="tab-highlight"]{background:#7659ce;}
.stButton button,.stFormSubmitButton button,.stDownloadButton button{border-radius:12px;min-height:44px;font-family:'Cairo','DM Sans',Tahoma,sans-serif;font-weight:700;border-color:#cfc3ed;}
.stButton button[kind="primary"],.stFormSubmitButton button[kind="primary"]{background:#6a52bf;border-color:#6a52bf;color:white;}
.stButton button:hover,.stDownloadButton button:hover{border-color:var(--purple);color:var(--purple);}
.stSlider [data-baseweb="slider"]{direction:ltr;}
[data-testid="stCaptionContainer"]{color:#77728e;line-height:1.75;}
[data-testid="stDataFrame"]{direction:ltr;}
[data-testid="stImage"]{text-align:center;}
h1,h2,h3{font-family:'Cairo','DM Sans',Tahoma,sans-serif!important;}
h2{font-size:1.65rem!important;color:#32285a!important;line-height:1.65!important;}
h3{font-size:1.18rem!important;}
.f-top{direction:__DIR__;text-align:__ALIGN__;display:flex;align-items:center;gap:11px;margin:3px 0 7px;}
.f-logo{width:48px;height:48px;border-radius:15px;background:linear-gradient(140deg,#8068db,#4d3a98);display:grid;place-items:center;color:white;font-size:25px;box-shadow:0 5px 12px #7764bc22;}
.f-top strong{display:block;font-size:23px;font-weight:800;color:#32255f;line-height:1.3;}
.f-top small{display:block;color:#88809f;font-size:12px;font-weight:600;margin-top:2px;}
.f-hero{direction:__DIR__;text-align:__ALIGN__;background:linear-gradient(115deg,#f4efff 0%,#fffcff 68%,#effbf6 100%);border:1px solid #e6dcff;border-radius:27px;padding:30px 32px;margin:16px 0 17px;min-height:260px;position:relative;overflow:hidden;}
.f-hero:before{content:"";position:absolute;width:230px;height:230px;background:#e2d7ff6e;border-radius:50%;top:-110px;inset-inline-end:-85px;}
.f-eyebrow{display:inline-flex;border-radius:30px;background:#eee7ff;color:#674db2;font-weight:800;padding:6px 13px;font-size:12px;position:relative;}
.f-hero h1{font-size:clamp(1.65rem,3vw,2.6rem)!important;color:#3b296d!important;line-height:1.5!important;margin:14px 0 5px;}
.f-hero p{font-size:15px;line-height:1.95;color:#68617e;margin:0;max-width:650px;}
.f-tags{display:flex;gap:8px;flex-wrap:wrap;margin-top:20px;}
.f-tags span{padding:6px 12px;background:#fff;border:1px solid #e6dcfa;border-radius:10px;color:#6657a4;font-weight:700;font-size:12px;}
.f-stepstrip{direction:__DIR__;display:flex;align-items:center;justify-content:space-between;gap:8px;background:white;border:1px solid var(--line);border-radius:18px;padding:15px 18px;margin-bottom:22px;flex-wrap:wrap;}
.f-step{display:flex;align-items:center;gap:8px;color:#5d5772;font-size:13px;font-weight:700;}
.f-step i{font-style:normal;display:grid;place-items:center;width:28px;height:28px;border-radius:50%;background:#f1ebff;color:#6e53c6;font-weight:800;}
.f-separator{color:#c8bcdf;font-weight:800;}
.f-section{direction:__DIR__;text-align:__ALIGN__;margin:20px 0 14px;}
.f-section .f-num{display:inline-block;background:#efeaff;color:#6b50ba;border-radius:8px;padding:3px 10px;margin-inline-end:9px;font-size:13px;font-weight:800;}
.f-section h2{display:inline;font-size:22px!important;margin:0;}
.f-section p{color:#7a748e;font-size:13px;margin:8px 0 0;}
.f-panel{direction:__DIR__;text-align:__ALIGN__;background:white;border:1px solid var(--line);border-radius:20px;padding:22px;margin:10px 0;box-shadow:0 7px 27px #7064a00a;}
.f-panel h3{font-size:18px!important;margin:6px 0 8px;color:#3e326a!important;line-height:1.6;}
.f-panel p{font-size:14px;color:#716d83;line-height:1.9;margin:0;}
.f-kicker{font-size:13px;color:#8b72ce;font-weight:800;}
.f-result{direction:__DIR__;text-align:__ALIGN__;background:linear-gradient(110deg,#ffffff,#faf8ff);border:1px solid #e5defa;border-radius:23px;padding:28px;margin:12px 0;display:flex;align-items:center;justify-content:space-between;gap:24px;}
.f-result h2{font-size:21px!important;margin:6px 0!important;color:#3d306c!important;}
.f-result p{font-size:13px;line-height:1.9;color:#6a657e;max-width:610px;}
.f-result-value{background:#f1eafe;border:1px solid #d9caf9;border-radius:50%;width:148px;height:148px;display:flex;align-items:center;justify-content:center;flex-direction:column;flex-shrink:0;direction:ltr;}
.f-result-value strong{font-size:30px;color:#563da1;}
.f-result-value span{font-size:10px;color:#736393;letter-spacing:.8px;}
.f-chip{display:inline-block;background:#efeafc;border:1px solid #e2d7fb;color:#644caa;padding:5px 10px;border-radius:9px;font-size:12px;font-weight:800;}
.f-grid{direction:__DIR__;display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin:15px 0 18px;}
.f-stat{background:white;border-radius:16px;border:1px solid var(--line);padding:18px;box-shadow:0 4px 18px #6353a308;}
.f-stat span{color:#77718d;font-size:12px;display:block;}
.f-stat strong{color:#3e326a;display:block;font-size:22px;margin-top:7px;overflow-wrap:anywhere;}
.f-stat small{color:#837e92;font-size:11px;}
.f-skill{direction:__DIR__;display:flex;justify-content:space-between;gap:12px;padding:11px 0;border-bottom:1px solid #f0edfa;font-size:13px;}
.f-skill:last-child{border:0;}
.f-skill b{color:#574296;background:#f0eaff;padding:3px 9px;border-radius:8px;direction:ltr;white-space:nowrap;}
.f-skill-good b{background:#e6f8f0;color:#247f65;}
.f-action{direction:__DIR__;display:flex;align-items:flex-start;gap:15px;background:white;border:1px solid #e8e2f7;border-radius:17px;padding:17px;margin:10px 0;}
.f-index{min-width:38px;height:38px;display:grid;place-items:center;background:#ede7fd;color:#634ab6;border-radius:12px;font-weight:800;}
.f-action strong{font-size:15px;color:#403565;}
.f-action p{font-size:13px;color:#766f88;line-height:1.8;margin:6px 0;}
.f-action small{color:#369a85;font-weight:800;}
.f-note{direction:__DIR__;background:#f6f3fe;border-inline-start:4px solid #9278de;border-radius:10px;padding:12px 16px;margin:16px 0;color:#645a86;font-size:13px;line-height:1.95;}
.f-footer{text-align:center;color:#8c86a1;padding:25px 10px 8px;font-size:12px;direction:__DIR__;}
@media(max-width:740px){
[data-testid="stHorizontalBlock"]{flex-direction:column!important;}
[data-testid="stHorizontalBlock"] > [data-testid="stColumn"]{min-width:100%!important;width:100%!important;flex:1 1 auto!important;}
[data-testid="stMainBlockContainer"]{padding-top:4rem;}
.f-hero{padding:21px;min-height:0;}
.f-hero h1{font-size:1.65rem!important;}
.f-result{flex-direction:column-reverse;align-items:flex-start;padding:19px;}
.f-result-value{width:105px;height:105px;}.f-result-value strong{font-size:22px;}
.f-grid{grid-template-columns:1fr;}
.f-stepstrip{gap:10px;}
.f-separator{display:none;}
}
"""
css = css.replace("__DIR__", "rtl" if ar else "ltr")
css = css.replace("__ALIGN__", "right" if ar else "left")
css = css.replace("__ROW__", "row-reverse" if ar else "row")
st.markdown("<style>" + css + "</style>", unsafe_allow_html=True)

brand, change_lang = st.columns([5, 1], vertical_alignment="center")
with brand:
    st.markdown(
        '<div class="f-top"><div class="f-logo">🐣</div><div>'
        '<strong>فرصة <span style="color:#8567d1">AI</span></strong>'
        '<small>FURSA AI · Your career growth companion</small></div></div>',
        unsafe_allow_html=True,
    )
with change_lang:
    st.selectbox(
        "Language / اللغة",
        ["العربية", "English"],
        key="ui_lang",
        label_visibility="collapsed",
    )

hero_text, hero_mascot = st.columns([1.9, 1], vertical_alignment="center")
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
    mascot("graduate", 270)

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
        mascot("coach", 175)

    with st.form("career_form"):
        academics, experience, professional = st.columns(3)
        inputs = {}
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
            mood = "coach"
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
            mascot(mood, 200)
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
        mascot("detective", 240)
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
            mascot("detective", 180)
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
        report_lines = [
            "FURSA AI - Personal Learning Plan",
            "Model score: " + f"{predict_score(profile):.1f}%",
            "This is not a calibrated hiring probability or guarantee.",
            "",
            "Growth priorities:",
        ]
        report_lines += [
            f"- {LABELS[key][1]}: {ADVICE[key][1]}" for key in priority_keys
        ]
        report_lines += ["", "Illustrative educational guidance only."]
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
        mascot("coder", 240)
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
            mascot("coder", 175)
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
        if not (add_projects or add_internships or add_programming):
            st.info(t("حرّك أي شريط عشان تشوف الفرق ✨", "Move a slider to see the comparison ✨"))
        else:
            st.markdown(
                '<div class="f-note">' +
                t("هاي محاكاة لنفس النموذج، مش وعد إنه التدريبات أو المشاريع رح ترفع فرص التوظيف فعليًا. ممكن المؤشر ما يرتفع حتى لو زادت بعض المهارات.",
                  "This is an exploratory model simulation, not evidence that adding a project or internship causes employment. The score may not always increase.") +
                '</div>', unsafe_allow_html=True
            )
        st.download_button(
            t("⬇️ نزّل ملفك CSV", "⬇️ Download your profile CSV"),
            pd.DataFrame([profile]).to_csv(index=False).encode("utf-8-sig"),
            file_name="fursa_profile.csv", mime="text/csv",
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

st.markdown(
    f'<div class="f-footer">🐣 FURSA AI · {t("كل مهارة جديدة، خطوة أقرب لفرصتك.","Every new skill brings you one step closer to opportunity.")}'
    f'<br>{t("مشروع تعليمي وتجريبي — مش ضمان توظيف","Educational prototype — not a job guarantee")}</div>',
    unsafe_allow_html=True,
)
