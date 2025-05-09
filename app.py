import streamlit as st
import pandas as pd
import plotly.express as px
from docx import Document
import fitz  # PyMuPDF
from PIL import Image
import base64
from io import BytesIO
import re
import requests
from dotenv import load_dotenv
import os

# 🌐 PAGE CONFIG
st.set_page_config(page_title="Intelligent ATS", layout="wide")

# 🔐 API kulcs betöltése .env-ből
load_dotenv()
API_KEY = os.getenv("OPENROUTER_API_KEY")
if not API_KEY:
    st.error("❌ API kulcs hiányzik! Állítsd be az OPENROUTER_API_KEY értékét a .env fájlban.")
    st.stop()

# 📄 DOCX feldolgozás
def extract_text_from_docx(file):
    doc = Document(file)
    return "\n".join([para.text for para in doc.paragraphs])

# 📄 PDF feldolgozás
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

# 🤖 OpenRouter hívás
def generate_response_from_openrouter(prompt):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    data = {
        "model": "mistralai/mixtral-8x7b",  # vagy más elérhető modell
        "messages": [{"role": "user", "content": prompt}]
    }

    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"].strip()
        else:
            st.error(f"❌ OpenRouter API hiba: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"❌ Kivétel történt: {str(e)}")
        return None

# 📥 Fájl feltöltés
st.title("Upload Resume and Job Description")
resume_file = st.file_uploader("Upload Resume (PDF/DOCX/TXT)", type=["pdf", "docx", "txt"])
job_desc = st.text_area("Paste Job Description")

if st.button("Clear Job Description"):
    job_desc = ""

# 📤 Elemzés
if st.button("Analyze") and resume_file and job_desc:
    file_bytes = resume_file.read()
    resume_text = ""

    if resume_file.type == "application/pdf":
        resume_text = extract_text_from_pdf(BytesIO(file_bytes))
        st.subheader("PDF Preview")
        for img in render_pdf_preview(BytesIO(file_bytes)):
            st.image(img, use_container_width=True)
    elif resume_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        resume_text = extract_text_from_docx(BytesIO(file_bytes))
    elif resume_file.type == "text/plain":
        resume_text = file_bytes.decode("utf-8")

    # 🔍 Iparági kulcsszavak
    prompt_keywords = f"List 10 most relevant keywords for this job description:\n{job_desc}"
    keywords_text = generate_response_from_openrouter(prompt_keywords)
    keywords = [kw.strip() for kw in keywords_text.split(",")] if keywords_text else []

    if not keywords:
        st.warning("No industry keywords were extracted.")
    else:
        st.subheader("Extracted Industry Keywords")
        st.write(keywords)

    # 🧠 AI értékelés
    prompt_analysis = f"""
    You are an AI ATS.
    Compare this resume: ```{resume_text}``` 
    with the following job description: ```{job_desc}``` 
    Highlight keyword matches, gaps, and provide a suitability score (0-100).
    Categorize missing skills into technical and soft skills.
    Return a summary report with improvement tips.
    """
    response_text = generate_response_from_openrouter(prompt_analysis)

    if response_text:
        st.subheader("AI Feedback")
        st.markdown(response_text)

        # 📊 Kulcsszavak stat
        density = get_keyword_density(resume_text, keywords)
        df = pd.DataFrame(list(density.items()), columns=["Keyword", "Count"])
        st.subheader("Keyword Density")
        st.dataframe(df)

        st.subheader("Keyword Usage Chart")
        fig = px.bar(df, x="Keyword", y="Count", title="Keyword Usage")
        st.plotly_chart(fig)

        # 🧠 Pontszám kinyerés
        match = re.search(r"(\d{1,3})\s*/\s*100", response_text)
        score = int(match.group(1)) if match else 0

        if "score_history" not in st.session_state:
            st.session_state["score_history"] = []

        st.session_state["score_history"].append({"Job": job_desc[:30] + "...", "Score": score})

        # 📈 Diagram
        score_df = pd.DataFrame(st.session_state["score_history"])
        st.subheader("Score Comparison")
        fig_score = px.bar(score_df, x="Job", y="Score", color="Score", color_continuous_scale="Blues", title="Suitability Score")
        fig_score.update_layout(yaxis_range=[0, 100])
        st.plotly_chart(fig_score)
