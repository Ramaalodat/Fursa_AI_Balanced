from pathlib import Path
import joblib
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="Fursa AI | فرصة", page_icon="✦", layout="wide")
ROOT = Path(__file__).resolve().parent
language = st.radio("Language / اللغة", ["العربية", "English"], horizontal=True, label_visibility="collapsed")
ar = language == "العربية"
def t(arabic, english):
    return arabic if ar else english

direction = "rtl" if ar else "ltr"
alignment = "right" if ar else "left"
st.markdown(f"""<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Arabic:wght@400;600;700;800&display=swap');
.stApp {{background:#f4f7fa;color:#153b50;}}
[data-testid="stMainBlockContainer"] {{max-width:1240px;padding-top:2.2rem;padding-bottom:3rem;direction:ltr;}}
h1,h2,h3,p,label {{font-family:'Noto Sans Arabic',Tahoma,Arial,sans-serif!important;}}
[data-testid="stMarkdownContainer"],[data-testid="stCaptionContainer"],[data-testid="stWidgetLabel"],[data-testid="stExpander"] summary {{direction:{direction};text-align:{alignment};}}
[data-testid="stCaptionContainer"] {{color:#526779!important;line-height:1.9;font-size:14px;}}
[data-testid="stHorizontalBlock"] {{flex-direction:{'row-reverse' if ar else 'row'};}}
[data-testid="stWidgetLabel"] p {{line-height:1.8;font-size:15px;}}
[data-testid="stMetric"] {{background:#fff;border:1px solid #dce5ec;border-radius:15px;padding:18px;}}
[data-testid="stMetricLabel"] {{direction:{direction};text-align:{alignment};}}
[data-testid="stMetricValue"],[data-testid="stMetricDelta"],[data-baseweb="input"],[data-baseweb="slider"] {{direction:ltr;}}
[data-testid="stMetricLabel"] p {{white-space:normal!important;line-height:1.7;}}
[data-testid="stDataFrame"],[data-testid="stImage"],[data-testid="stVegaLiteChart"] {{direction:ltr!important;unicode-bidi:isolate;text-align:left;}}
[data-testid="stForm"],[data-testid="stExpander"] {{background:#fff;border:1px solid #dce5ec;border-radius:15px;}}
[data-testid="stForm"] {{padding:20px;}}
h3 {{font-size:1.4rem!important;line-height:1.8!important;margin-top:.7rem!important;}}
.hero,.result,.overview,.plan,.skill-row {{font-family:'Noto Sans Arabic',Tahoma,Arial,sans-serif;direction:{direction};text-align:{alignment};}}
.hero *, .result *, .overview *, .plan *, .skill-row * {{font-family:'Noto Sans Arabic',Tahoma,Arial,sans-serif!important;}}
.hero {{background:linear-gradient(115deg,#103f51,#176d73);padding:32px 38px;border-radius:24px;margin:8px 0 20px;}}
.hero-label {{font-size:14px;font-weight:700;color:#b1efdf;}}
.hero h1 {{color:#fff!important;font-size:2.5rem!important;line-height:1.7!important;margin:12px 0!important;}}
.hero p {{color:#e4f3f4;line-height:1.9;font-size:16px;margin:0;}}
.hero-tags {{display:flex;gap:10px;flex-wrap:wrap;margin-top:18px;}}
.hero-tags span {{border:1px solid #ffffff33;background:#ffffff10;color:#e8faf8;border-radius:24px;padding:5px 12px;font-size:13px;}}
[data-baseweb="tab-list"] {{direction:{direction};gap:8px;background:#e7eef2;border-radius:14px;padding:6px;margin-bottom:20px;}}
[data-baseweb="tab"] {{border-radius:9px;height:44px;padding:0 20px!important;}}
[data-baseweb="tab"][aria-selected="true"] {{color:white!important;background:#146c76;}}
[data-baseweb="tab-highlight"],[data-baseweb="tab-border"] {{display:none;}}
.result {{display:flex;align-items:center;gap:25px;border:1px solid #dce5ec;border-radius:20px;background:white;padding:24px;margin:12px 0;}}
.result-copy {{flex:1;min-width:0;}}
.result-copy h3 {{font-size:20px!important;margin:5px 0!important;}}
.result-copy p {{font-size:15px;line-height:1.9;color:#425e71;}}
.result-label {{font-size:13px;background:#e7f6f1;color:#167c69;padding:5px 9px;border-radius:7px;display:inline-block;}}
.ring {{width:132px;height:132px;flex-shrink:0;background:conic-gradient(#138a8a var(--angle),#e8eff3 0);border-radius:50%;display:grid;place-items:center;direction:ltr;}}
.ring-inner {{width:112px;height:112px;border-radius:50%;background:white;display:grid;place-items:center;font-size:30px;font-weight:800;}}
.overview {{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin:14px 0 24px;}}
.overview-item {{background:white;border:1px solid #dce5ec;border-radius:14px;padding:16px;}}
.overview-item span {{display:block;font-size:14px;color:#526779;line-height:1.8;}}
.overview-item strong {{display:block;font-size:21px;margin-top:7px;}}
.overview-item.next strong {{font-size:16px;}}
.overview-item.good {{border-inline-start:4px solid #249d7b;}}
.overview-item.growth {{border-inline-start:4px solid #e8ab58;}}
.overview-item.next {{border-inline-start:4px solid #648bbc;}}
.skill-row {{display:flex;justify-content:space-between;align-items:center;gap:18px;padding:10px 0;border-bottom:1px solid #e9eff3;font-size:15px;}}
.skill-value {{white-space:nowrap;font-size:14px;font-weight:700;color:#14796f;background:#edf7f3;padding:3px 9px;border-radius:7px;}}
.plan {{display:flex;gap:15px;align-items:flex-start;padding:20px;background:white;border:1px solid #dce5ec;border-radius:14px;margin:10px 0;}}
.plan-number {{background:#e7f5ef;color:#167c69;min-width:36px;height:36px;display:grid;place-items:center;border-radius:10px;font-weight:800;}}
.plan strong {{font-size:17px;}}
.plan p {{font-size:15px;line-height:1.9;color:#425e71;margin:7px 0;}}
.deliverable {{font-size:14px;font-weight:700;color:#167c69;}}
.stButton button,.stFormSubmitButton button {{border-radius:11px;min-height:46px;}}
.stFormSubmitButton button {{background:#146c76;border-color:#146c76;color:white;}}
@media(max-width:640px) {{.hero {{padding:23px;}} .hero h1 {{font-size:1.7rem!important;}} .result {{gap:15px;padding:17px;align-items:flex-start;}} .ring {{width:96px;height:96px;}} .ring-inner {{width:80px;height:80px;font-size:23px;}} .overview {{grid-template-columns:1fr;}}}}

[data-testid="stVerticalBlockBorderWrapper"] {{border-radius:20px!important;}}
[data-testid="stDataFrame"] {{border-radius:14px;overflow:hidden;}}
[data-testid="stMetric"] {{box-shadow:0 4px 18px #123b5110;}}
[data-testid="stMetricValue"] {{font-weight:800!important;color:#116e75!important;}}
[data-testid="stHeadingWithActionElements"] {{direction:{direction};}}
[data-testid="stExpander"] {{border-radius:14px!important;}}
.perf-header {{direction:{direction};text-align:{alignment};background:linear-gradient(120deg,#ecf8f5,#e8f1f8);padding:25px 28px;border:1px solid #d5e8e7;border-radius:18px;margin:12px 0 22px;}}
.perf-header h2 {{font-size:24px;color:#103f51;margin:0 0 8px;}}
.perf-header p {{font-size:15px;color:#476575;line-height:1.9;margin:0;}}
</style>""",unsafe_allow_html=True)

st.markdown(f'''<section class="hero"><div class="hero-label">✦ FURSA AI / {t("فرصة جديدة للتطوّر","YOUR NEXT OPPORTUNITY")}</div><h1>{t("اعرف قدراتك. خطّط لخطوتك الجاية.","Know your strengths. Plan your next step.")}</h1><p>{t("اكتشف نقاط قوتك، والجوانب اللي ممكن تطورها، وجرب كيف يتغير مؤشر النموذج مع تطوير مهاراتك.","Discover your strengths, areas to develop, and how your model score responds to changes.")}</p><div class="hero-tags"><span>{t("تحليل ملفك","Profile insights")}</span><span>{t("خطة تطوير","Growth plan")}</span><span>{t("محاكاة التحسين","What-if simulation")}</span></div></section>''', unsafe_allow_html=True)


FEATURES = [
    "CGPA", "Programming_Skill", "Problem_Solving", "Projects_Completed",
    "Internships", "Certifications", "Communication_Skills",
    "English_Proficiency", "Resume_Score", "Interview_Score"
]
LABELS = {
    "CGPA": ("المعدل الجامعي من 4", "CGPA out of 4"),
    "Programming_Skill": ("البرمجة من 10", "Programming out of 10"),
    "Problem_Solving": ("حل المشكلات من 10", "Problem solving out of 10"),
    "Projects_Completed": ("عدد المشاريع", "Completed projects"),
    "Internships": ("عدد التدريبات العملية", "Internships"),
    "Certifications": ("عدد الشهادات", "Certificates"),
    "Communication_Skills": ("التواصل من 10", "Communication out of 10"),
    "English_Proficiency": ("مستوى الإنجليزية", "English proficiency"),
    "Resume_Score": ("تقييم السيرة الذاتية من 100", "Resume score out of 100"),
    "Interview_Score": ("تقييم المقابلة من 100", "Interview score out of 100"),
}
TARGETS = {
    "Programming_Skill": 7, "Problem_Solving": 7,
    "Communication_Skills": 7, "Projects_Completed": 3,
    "Internships": 1, "Certifications": 1,
    "Resume_Score": 70, "Interview_Score": 70
}
ADVICE = {
    "Programming_Skill": ("تدرّب على Python وطبّق اللي تعلمته بمشروع صغير.", "Practise Python and build a small project."),
    "Problem_Solving": ("حلّ مسائل عملية واشرح خطوات الحل.", "Solve practical problems and explain your approach."),
    "Communication_Skills": ("تدرّب على عرض مشروعك خلال دقيقتين.", "Practise a two-minute project pitch."),
    "Projects_Completed": ("أنجز مشروعًا وانشره مع README واضح.", "Complete a project and publish it with a clear README."),
    "Internships": ("حدّث سيرتك وقدّم على فرص تدريب مناسبة.", "Update your CV and apply for relevant internships."),
    "Certifications": ("اختَر دورة مرتبطة بهدفك وطبّق محتواها.", "Choose a relevant course and apply what you learn."),
    "Resume_Score": ("حسّن سيرتك بإضافة المشاريع والإنجازات القابلة للقياس.", "Improve your CV with projects and measurable achievements."),
    "Interview_Score": ("جرّب مقابلة تدريبية وراجع إجاباتك.", "Try a mock interview and review your answers.")
}

@st.cache_resource
def load_artifacts(model_file, model_mtime, preprocessor_file, preprocessor_mtime):
    return joblib.load(model_file), joblib.load(preprocessor_file)

model_file = ROOT / "milestone3_outputs" / "best_placement_model.pkl"
preprocessor_file = ROOT / "milestone3_outputs" / "preprocessor.pkl"
if not model_file.exists() or not preprocessor_file.exists():
    st.error(t("ملفات الموديل مش موجودة. شغّلي خلية حفظ الموديل والـ Preprocessor بالنوتبوك، وخلي مجلد milestone3_outputs جنب app.py.",
               "Model files not found. Run the notebook's model-saving cell and keep milestone3_outputs beside app.py."))
    st.stop()

try:
    model, preprocessor = load_artifacts(
        str(model_file), model_file.stat().st_mtime_ns,
        str(preprocessor_file), preprocessor_file.stat().st_mtime_ns
    )
except Exception as error:
    st.error(t("تعذر تحميل الموديل. تأكدي من توافق إصدارات المكتبات.", "Could not load model. Check library versions."))
    st.exception(error)
    st.stop()

def score(values):
    frame = pd.DataFrame([values], columns=FEATURES)
    # Match the notebook's English_Proficiency encoding before preprocessing.
    english_levels = {"Basic": 1, "Intermediate": 2, "Advanced": 3}
    frame["English_Proficiency"] = frame["English_Proficiency"].replace(english_levels).astype(int)
    # Exactly as in notebook cell 24: optional columns are handled by intersection.
    soft_cols = [c for c in ["Communication_Skills", "Teamwork", "Problem_Solving"] if c in frame.columns]
    practical_cols = [c for c in ["Projects_Completed", "Internships", "Hackathons"] if c in frame.columns]
    frame["Soft_Skills_Average"] = frame[soft_cols].mean(axis=1)
    frame["Practical_Exposure_Score"] = frame[practical_cols].sum(axis=1)
    matrix = preprocessor.transform(frame)
    # The notebook trained with a pandas DataFrame with these exact output names.
    matrix = pd.DataFrame(matrix, columns=preprocessor.get_feature_names_out())
    classes = list(model.classes_)
    positive_idx = classes.index(1) if 1 in classes else classes.index("Placed")
    return float(model.predict_proba(matrix)[0, positive_idx] * 100)

def name(key):
    return t(*LABELS[key])

assessment, performance = st.tabs([
    t("✦ تحليل ملفك وخطتك", "✦ Your profile & plan"),
    t("◈ أداء النموذج", "◈ Model performance")
])

with assessment:
    st.subheader(t("1. بياناتك ومهاراتك", "1. Your details & skills"))
    st.caption(t("عبّي بياناتك العشرة واضغط حلّل ملفّي.", "Complete your ten inputs and analyse your profile."))
    with st.form("profile_form"):
        a, b, c = st.columns(3)
        values = {}
        with a:
            st.markdown("**" + t("الدراسة والمهارات", "Academic & technical skills") + "**")
            values["CGPA"] = st.slider(name("CGPA"), 2.0, 4.0, 3.1, 0.01)
            values["Programming_Skill"] = st.slider(name("Programming_Skill"), 1, 10, 6)
            values["Problem_Solving"] = st.slider(name("Problem_Solving"), 1, 10, 6)
            values["English_Proficiency"] = st.selectbox(
                name("English_Proficiency"), ["Basic", "Intermediate", "Advanced"], index=1,
                format_func=lambda v: {"Basic":t("أساسي","Basic"),"Intermediate":t("متوسط","Intermediate"),"Advanced":t("متقدم","Advanced")}[v]
            )
        with b:
            st.markdown("**" + t("الخبرة العملية", "Practical experience") + "**")
            values["Projects_Completed"] = st.number_input(name("Projects_Completed"), 0, 15, 2, 1)
            values["Internships"] = st.number_input(name("Internships"), 0, 5, 0, 1)
            values["Certifications"] = st.number_input(name("Certifications"), 0, 10, 1, 1)
        with c:
            st.markdown("**" + t("المهارات المهنية", "Professional skills") + "**")
            values["Communication_Skills"] = st.slider(name("Communication_Skills"), 1, 10, 6)
            values["Resume_Score"] = st.slider(name("Resume_Score"), 0, 100, 65)
            values["Interview_Score"] = st.slider(name("Interview_Score"), 0, 100, 65)
        st.caption(t("مستوى الإنجليزية يتحوّل إلى رقم بنفس ترميز النوتبوك قبل إدخاله للموديل.",
                     "English level uses the same numeric encoding as the training notebook."))
        submitted = st.form_submit_button(t("حلّل ملفّي ←", "Analyse my profile →"), type="primary", use_container_width=True)
    if submitted:
        st.session_state["fursa_profile"] = values.copy()

    if "fursa_profile" in st.session_state:
        profile = st.session_state["fursa_profile"]
        try:
            current = score(profile)
        except Exception as error:
            st.error(t("في عدم توافق بين مدخلات التطبيق والموديل المحفوظ. أعيدي تشغيل خلايا التدريب والحفظ.",
                       "Saved model and app inputs do not match. Re-run training and saving cells."))
            st.exception(error)
            st.stop()
        st.subheader(t("2. نتيجتك", "2. Your result"))
        st.markdown(f"""<div class="result"><div class="ring" style="--angle:{current*3.6:.2f}deg"><div class="ring-inner">{current:.1f}%</div></div><div class="result-copy"><span class="result-label">{t('مؤشر النموذج','MODEL SCORE')}</span><h3>{t('تحليل ملفك','Your profile analysis')}</h3><p>{t('هذا مؤشر ميل النموذج لفئة التوظيف في بيانات التدريب، مش نسبة جاهزية مثبتة ولا ضمان للحصول على وظيفة.','This reflects the model tendency towards the placed class in its training data; it is not a validated readiness score or job guarantee.')}</p></div></div>""", unsafe_allow_html=True)

        strengths = []
        gaps = []
        for key in TARGETS:
            if profile[key] >= TARGETS[key]:
                strengths.append(key)
            else:
                gaps.append(key)
        gaps.sort(key=lambda key: profile[key] / TARGETS[key])
        next_area = name(gaps[0]) if gaps else t("تطوير مشروع جديد", "Build another project")
        st.markdown(f"""<div class="overview"><div class="overview-item good"><span>{t('جوانب حققت الهدف التعليمي','Areas meeting targets')}</span><strong>{len(strengths)} / {len(TARGETS)}</strong></div><div class="overview-item growth"><span>{t('جوانب قابلة للتطوير','Areas to develop')}</span><strong>{len(gaps)}</strong></div><div class="overview-item next"><span>{t('ابدأ من هون','START HERE')}</span><strong>{next_area}</strong></div></div>""", unsafe_allow_html=True)
        st.subheader(t("3. نقاط القوة وفجوات التطوير", "3. Strengths & development gaps"))
        st.caption(t("المقارنة هون مع أهداف تعليمية تقريبية، مش متطلبات مؤكدة لسوق العمل أو تفسير مباشر للموديل.",
                     "These are illustrative educational targets, not verified labour-market requirements or model explanations."))
        left, right = st.columns(2)
        with left:
            with st.container(border=True):
                st.markdown("#### " + t("✓ نقاط القوة", "✓ Strengths"))
                for key in strengths:
                    st.markdown(f'<div class="skill-row"><span>{name(key)}</span><span class="skill-value">{profile[key]}</span></div>', unsafe_allow_html=True)
                if not strengths:
                    st.write(t("لسه في فرص كثيرة للتطور.", "There is plenty of room to grow."))
        with right:
            with st.container(border=True):
                st.markdown("#### " + t("↗ أولويات التطوير", "↗ Growth priorities"))
                for key in gaps:
                    st.markdown(f'<div class="skill-row"><span>{name(key)}</span><span class="skill-value">{profile[key]} / {TARGETS[key]}</span></div>', unsafe_allow_html=True)
                if not gaps:
                    st.write(t("حققت كل الأهداف التعليمية المحددة.", "You meet all illustrative targets."))
        st.subheader(t("4. خطتك العملية", "4. Your action plan"))
        plan_keys = gaps[:3] if gaps else ["Projects_Completed", "Interview_Score"]
        for i, key in enumerate(plan_keys, 1):
            st.markdown(f'<div class="plan"><div class="plan-number">{i:02d}</div><div><strong>{name(key)}</strong><p>{t(*ADVICE[key])}</p></div></div>', unsafe_allow_html=True)

        st.subheader(t("5. جرّب تطوير ملفك", "5. Explore improvements"))
        st.caption(t("غيّر القيم وشوف استجابة الموديل. هاي محاكاة، مش إثبات إن إضافة تدريب بتسبب توظيف.",
                     "Change values to explore model responses. This is not evidence that an internship causes employment."))
        p, q, r = st.columns(3)
        add_projects = p.slider(t("مشاريع إضافية", "Additional projects"), 0, 3, 0)
        add_internships = q.slider(t("تدريبات إضافية", "Additional internships"), 0, 2, 0)
        add_programming = r.slider(t("تحسن البرمجة", "Programming improvement"), 0, 3, 0)
        scenario = profile.copy()
        scenario["Projects_Completed"] = min(15, profile["Projects_Completed"] + add_projects)
        scenario["Internships"] = min(5, profile["Internships"] + add_internships)
        scenario["Programming_Skill"] = min(10, profile["Programming_Skill"] + add_programming)
        future = score(scenario)
        before, after, difference = st.columns(3)
        before.metric(t("قبل", "Before"), f"{current:.1f}%")
        after.metric(t("بعد", "After"), f"{future:.1f}%")
        difference.metric(t("الفرق بالنقاط المئوية", "Difference in percentage points"), f"{future-current:+.1f}")
        st.download_button(
            t("تنزيل بياناتي CSV", "Download profile CSV"),
            pd.DataFrame([profile]).to_csv(index=False).encode("utf-8-sig"),
            file_name="fursa_profile.csv", mime="text/csv"
        )
    else:
        st.info(t("عبّي بياناتك واضغط حلّل ملفّي حتى تشوفي النتيجة والخطة.",
                  "Complete your details and select Analyse to see your results."))

with performance:
    st.markdown(f'''<div class="perf-header"><h2>{t("أداء نماذج Fursa AI", "Fursa AI model performance")}</h2><p>{t("مقارنة واضحة بين الخوارزميات التي جربناها، وبالأرقام المحفوظة من التدريب. هاي نتائج نماذج على الداتا، مش تقييم جاهزية شخص معيّن.", "A clear comparison of trained algorithms using saved results. These are dataset-level metrics, not personal readiness ratings.")}</p></div>''', unsafe_allow_html=True)

    comparison_file = ROOT / "milestone3_outputs" / "model_comparison.csv"
    if not comparison_file.exists():
        comparison_file = ROOT / "model_comparison.csv"

    if comparison_file.exists():
        comparison = pd.read_csv(comparison_file)
        # The exported notebook compares cross-validation metrics, not holdout scores.
        metric_names = {
            "CV Accuracy": ("Accuracy", "Accuracy"),
            "CV Balanced Accuracy": ("الدقة المتوازنة", "Balanced accuracy"),
            "CV Macro F1": ("Macro F1", "Macro F1"),
            "Accuracy": ("Accuracy", "Accuracy"),
            "F1-Score": ("F1-Score", "F1-Score"),
            "ROC-AUC": ("ROC-AUC", "ROC-AUC"),
        }
        available = [column for column in metric_names if column in comparison.columns]
        preferred = [column for column in ["CV Accuracy", "CV Balanced Accuracy", "CV Macro F1", "Accuracy", "F1-Score", "ROC-AUC"] if column in available]
        display_names = {
            "LogisticRegression": "Logistic Regression",
            "RandomForestClassifier": "Random Forest",
            "DecisionTreeClassifier": "Decision Tree",
            "KNeighborsClassifier": "KNN",
            "K-Nearest Neighbors": "KNN",
        }
        table = comparison.copy()
        if "Model" in table.columns:
            table["Model"] = table["Model"].replace(display_names)

        if preferred and "Model" in table.columns:
            primary = "CV Balanced Accuracy" if "CV Balanced Accuracy" in preferred else preferred[0]
            leading_idx = pd.to_numeric(table[primary], errors="coerce").idxmax()
            best_name = str(table.loc[leading_idx, "Model"])
            st.caption(t("نتائج مقارنة الخوارزميات من ملف التدريب المحفوظ", "Algorithm comparison from the saved training results"))
            st.markdown("#### " + t("النتائج بنظرة سريعة", "Results at a glance"))
            a, b, c = st.columns(3)
            a.metric(t("عدد الخوارزميات", "Algorithms tested"), str(len(table)))
            b.metric(t("الأعلى حسب", "Highest by") + " " + metric_names[primary][1], best_name)
            c.metric(t("قيمة المقياس الأعلى", "Top metric value"), f"{float(table.loc[leading_idx, primary]):.2%}")

            st.markdown("#### " + t("قارن الأداء بصريًا", "Compare model performance"))
            chosen = st.selectbox(
                t("اختار المقياس", "Choose a metric"),
                preferred,
                index=preferred.index("CV Balanced Accuracy") if "CV Balanced Accuracy" in preferred else 0,
                format_func=lambda key: t(*metric_names[key]),
            )
            chart = table[["Model", chosen]].copy()
            chart[chosen] = pd.to_numeric(chart[chosen], errors="coerce")
            chart = chart.dropna().sort_values(chosen, ascending=True)
            fig, ax = plt.subplots(figsize=(9, 3.9))
            colors = ["#177f83" if model == best_name and chosen == primary else "#66b5b0" for model in chart["Model"]]
            bars = ax.barh(chart["Model"], chart[chosen].to_numpy() * 100, color=colors, height=0.58)
            ax.bar_label(bars, fmt="%.1f%%", padding=6, fontsize=10)
            ax.set_xlim(0, max(100, float(chart[chosen].max() * 100 + 12)))
            ax.set_xlabel(t("النتيجة (%)", "Score (%)"))
            ax.spines[["top", "right", "left"]].set_visible(False)
            ax.grid(axis="x", alpha=0.13)
            ax.set_axisbelow(True)
            fig.patch.set_facecolor("white")
            ax.set_facecolor("white")
            fig.tight_layout()
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)

            st.markdown("#### " + t("ملخص المقاييس", "Metrics summary"))
            selected_columns = ["Model"] + preferred[:3]
            pretty = table[selected_columns].copy()
            for column in preferred[:3]:
                pretty[column] = pd.to_numeric(pretty[column], errors="coerce").map(lambda v: f"{v:.2%}" if pd.notna(v) else "—")
            pretty = pretty.rename(columns={key: t(*metric_names[key]) for key in preferred[:3]})
            st.dataframe(pretty, hide_index=True, use_container_width=True)

            st.info(t("الأعلى في مقياس معيّن مش بالضرورة الأفضل في كل المقاييس. اختاروا الموديل بناءً على هدف المشروع ونتائج التحقق، مش Accuracy لحالها.",
                      "A model leading one metric may not lead others. Select based on project goals and validation, not accuracy alone."))
            with st.expander(t("التفاصيل التقنية الكاملة والإعدادات", "Full technical results and parameters")):
                st.dataframe(table, hide_index=True, use_container_width=True)
                st.download_button(t("تنزيل النتائج CSV", "Download results CSV"), comparison.to_csv(index=False).encode("utf-8-sig"), "fursa_model_comparison.csv", "text/csv")
        else:
            st.warning(t("ملف المقارنة موجود، لكن أسماء أعمدته غير متوافقة مع العرض.", "Comparison file is present but its columns are not recognized."))
            st.dataframe(comparison, hide_index=True, use_container_width=True)
    else:
        st.info(t("ملف مقارنة الخوارزميات مش موجود. احفظي نتائج النوتبوك في model_comparison.csv جنب app.py أو داخل milestone3_outputs.",
                  "Model comparison data is missing. Export model_comparison.csv alongside app.py or into milestone3_outputs."))

    st.markdown("#### " + t("شو بتعني النتائج؟", "What do the scores mean?"))
    st.write(t("**Accuracy** نسبة التوقعات الصحيحة. **Balanced Accuracy** بتوازن اهتمامنا بالفئتين، و**Macro F1** بيساعدنا نشوف الأداء بدون ما نركز على الفئة الأكبر فقط. الأرقام من الداتا المستخدمة بالتجربة، وما بتثبت جاهزية خريجي الأردن أو فرصة توظيف شخص محدد.",
               "**Accuracy** is the share of correct predictions. **Balanced accuracy** accounts for recall across both classes, and **Macro F1** measures F1 equally across classes. These dataset-level scores do not establish readiness or employment prospects for individuals or Jordanian graduates."))

st.caption(t("FURSA AI · كل مهارة بتتعلمها بتفتح فرصة.",
             "FURSA AI · Every skill you build opens a new opportunity."))
