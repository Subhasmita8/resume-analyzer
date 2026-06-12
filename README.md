# 🤖 AI Resume Analyzer

An intelligent web application that analyzes resumes against job descriptions and provides a match score, missing skills, and actionable suggestions to improve job fit.

---

## 📌 Features

* 📄 Upload resume (PDF/DOCX)
* 🧠 AI-based text analysis using NLP
* 📊 Match score (0–100%)
* 🔍 Keyword matching between resume & job description
* ❌ Missing skills detection
* 💡 Personalized improvement suggestions
* ⚡ Fast and responsive UI

---

## 🛠️ Tech Stack

### 🔹 Frontend

* HTML
* CSS
* JavaScript

### 🔹 Backend

* Flask (Python)
* Flask-CORS

### 🔹 NLP & ML

* spaCy
* NLTK
* Scikit-learn (TF-IDF + Cosine Similarity)

### 🔹 File Parsing

* PyPDF2
* python-docx

---

## 📂 Project Structure

```
resume-analyzer/
│
├── backend/
│   ├── app.py
│   ├── requirements.txt
│   └── utils/
│
├── frontend/
│   ├── index.html
│   ├── script.js
│   └── style.css
```

---

## ⚙️ How It Works

1. User uploads a resume
2. User enters job description
3. Backend extracts resume text
4. Text is preprocessed using NLP
5. TF-IDF + cosine similarity calculates match score
6. Missing keywords and suggestions are generated
7. Results displayed on UI

---

## 🌍 Deployment

* Backend deployed on Render
* Frontend deployed on Netlify

---

## 🎯 Future Improvements

* 📈 Add charts and analytics
* 🧾 Resume scoring breakdown

---

👨‍💻 Author Subhasmita Prusty
---

⭐ If you found this useful, consider giving it a star!
