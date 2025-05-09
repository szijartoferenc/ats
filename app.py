import streamlit as st
import cohere
import os
import pandas as pd
import plotly.express as px
from docx import Document
import fitz  # PyMuPDF
from PIL import Image
import base64
from io import BytesIO
import re
from dotenv import load_dotenv

# 🌐 PAGE CONFIG
st.set_page_config(page_title="Intelligent ATS", layout="wide")

# ✅ Környezeti változók betöltése
load_dotenv()

# ✅ Cohere API kulcs beállítása
cohere_api_key = os.getenv("COHERE_API_KEY")  # .env-ből
co = cohere.Client(cohere_api_key)  # Cohere kliens inicializálása

# 🌗 Dark/Light mód
if st.sidebar.toggle("🌙 Dark Mode", value=False):
    st.markdown("<style>body { background-color: #1E1E1E; color: white; }</style>", unsafe_allow_html=True)

# 🌍 Nyelvválasztás
language = st.sidebar.selectbox("🌍 Language", ["English", "Magyar"])
t = lambda en, hu: hu if language == "Magyar" else en

# 📄 DOCX feldolgozás
def extract_text_from_docx(file):
    doc = Document(file)
    return "\n".join([para.text for para in doc.paragraphs])

# 📄 PDF feldolgozás és előnézet
def extract_text_from_pdf(file):
    with fitz.open(stream=file.read(), filetype="pdf") as doc:
        return "\n".join(page.get_text() for page in doc)

def render_pdf_preview(file):
    images = []
    with fitz.open(stream=file.read(), filetype="pdf") as doc:
        for page in doc:
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            images.append(img)
    return images

# 📊 Kulcsszó statisztika
def get_keyword_density(text, keywords):
    words = text.lower().split()
    return {kw: words.count(kw.lower()) for kw in keywords}

# 🔍 Kulcsszó kiemelés
def highlight_keywords(text, keywords):
    for word in keywords:
        pattern = re.compile(re.escape(word), re.IGNORECASE)
        text = pattern.sub(f'<span style="background-color: yellow; color: black;"><b>{word}</b></span>', text)
    return text

# 🤖 Cohere válasz

def generate_response_from_cohere(prompt):
    try:
        response = co.generate(
            model="command",  # Generatív modell neve
            prompt=prompt,
            max_tokens=500  # Beállítható, hogy hány tokent használjon
        )
        return response.generations[0].text.strip()  # A válasz szövegének hozzáférése
    except Exception as e:
        return f"❌ Error: {str(e)}"

def extract_industry_keywords(job_desc):
    prompt = f"Extract 10 most relevant keywords for this job description:\n{job_desc}"
    response = generate_response_from_cohere(prompt)
    return [kw.strip() for kw in response.split(",") if kw.strip()]

# 📤 Export segéd

def get_download_link(df, filetype="csv"):
    towrite = BytesIO()
    if filetype == "csv":
        df.to_csv(towrite, index=False)
        mime = "text/csv"
        ext = "csv"
    else:
        df.to_excel(towrite, index=False, engine='openpyxl')
        mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ext = "xlsx"
    towrite.seek(0)
    b64 = base64.b64encode(towrite.read()).decode()
    href = f'<a href="data:{mime};base64,{b64}" download="report.{ext}">📥 Download as {ext.upper()}</a>'
    return href

# 📄 Feltöltés
st.title(t("Upload Resume and Job Description", "Önéletrajz és álláshirdetés feltöltése"))
resume_file = st.file_uploader(t("Upload Resume (PDF/DOCX/TXT)", "Önéletrajz feltöltése (PDF/DOCX/TXT)"), type=["pdf", "docx", "txt"])
job_desc = st.text_area(t("Paste Job Description", "Másold be az álláshirdetést"))

# 🗑️ Job Description törlése
if st.button(t("Clear Job Description", "Álláshirdetés törlése")):
    job_desc = ""

# 🚀 Elemzés indítása
if st.button(t("Analyze", "Elemzés indítása")) and resume_file and job_desc:
    file_bytes = resume_file.read()
    resume_text = ""

    if resume_file.type == "application/pdf":
        resume_text = extract_text_from_pdf(BytesIO(file_bytes))
        st.subheader(t("PDF Preview", "PDF előnézet"))
        for img in render_pdf_preview(BytesIO(file_bytes)):
            st.image(img, use_container_width=True)
    elif resume_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        resume_text = extract_text_from_docx(BytesIO(file_bytes))
    elif resume_file.type == "text/plain":
        resume_text = file_bytes.decode("utf-8")

    # 🔍 Iparági kulcsszavak generálása
    industry_keywords = extract_industry_keywords(job_desc)

    # 🧠 AI értékelés
    prompt = f"""
    You are an AI ATS.
    Compare this resume: ```{resume_text}``` 
    with the following job description: ```{job_desc}``` 
    Highlight keyword matches, gaps, and provide a suitability score (0-100).
    Categorize missing skills into technical and soft skills.
    Return a summary report with improvement tips.
    """
    response_text = generate_response_from_cohere(prompt)

    st.subheader(t("AI Feedback", "AI visszajelzés"))
    st.markdown(response_text)

    # 📊 Kulcsszavak elemzése
    density = get_keyword_density(resume_text, industry_keywords)
    if not density:
        st.warning(t("No keywords found to display.", "Nincs kulcsszó, amit megjeleníthetnénk."))
    else:
        df = pd.DataFrame(list(density.items()), columns=["Keyword", "Count"])
        st.subheader(t("Keyword Density", "Kulcsszó gyakoriság"))
        st.dataframe(df)
        st.markdown(get_download_link(df, "csv"), unsafe_allow_html=True)
        st.markdown(get_download_link(df, "excel"), unsafe_allow_html=True)

        st.subheader(t("Keyword Usage Chart", "Kulcsszó használati diagram"))
        fig = px.bar(df, x="Keyword", y="Count", title="Keyword Usage")
        st.plotly_chart(fig)

    # 🕒 Score history
        if "score_history" not in st.session_state:
            st.session_state["score_history"] = []

        score_line = re.search(r"(\d{1,3})\s*/\s*100", response_text)
        score = int(score_line.group(1)) if score_line else 0

        st.session_state["score_history"].append({
            "Job": job_desc[:30] + "...",
            "Score": score
        })

        score_df = pd.DataFrame(st.session_state["score_history"])

        st.subheader(t("Score Comparison", "Pontszám összehasonlítás"))
        if score_df.empty:
            st.warning(t("No scores to compare.", "Nincs pontszám az összehasonlításhoz."))
        else:
            fig_score = px.bar(
                score_df,
                x="Job",
                y="Score",
                color="Score",
                color_continuous_scale="Blues",
                title="Suitability Score per Job"
            )
            fig_score.update_layout(yaxis_range=[0, 100])
            st.plotly_chart(fig_score)

# ℹ️ Oldalsáv információ
st.sidebar.info(t("Upload your resume and compare it with job postings using AI.",
                  "Töltsd fel az önéletrajzod, és hasonlítsd össze álláshirdetésekkel mesterséges intelligenciával."))
