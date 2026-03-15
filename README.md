# 🛡️ Pramāna: AI-Powered Digital Forensics Hub

**Pramāna** (Sanskrit for "Proof" or "Knowledge") is an advanced digital forensics tool designed to verify the authenticity of digital media and information. In an era of sophisticated deepfakes and AI-generated misinformation, Pramāna provides a mathematical "source of truth."

---

## 🚀 Key Features
* **📷 Image Forensics:** Analyzes pixel distribution and PRNU noise to detect AI-generated artifacts from models like Midjourney and DALL-E.
* **📰 News Validator:** Cross-references headlines and text to identify potential misinformation or "fake news."
* **🛡️ Scam Job Verifier:** Scans offer letters and job descriptions for linguistic red flags and common fraud patterns.
* **🔍 Digital Trace Analysis:** Infers synthetic origin profiles even when EXIF metadata has been stripped.

---

## 🛠️ Technical Stack
* **Backend:** Python / Flask
* **Intelligence:** Llama 4 Scout (Vision) & Llama 3.3 (Text) via Groq LPU Cloud
* **Frontend:** HTML5, CSS3 (Glassmorphism UI), JavaScript
* **Deployment:** Render (Cloud Hosting) & Cron-Job (Persistence)

---

## 📂 Project Structure
```text
Pramana-Forensics/
├── app.py              # Main Flask Backend
├── requirements.txt    # System Dependencies
├── static/             # Assets (Icons, Images)
└── templates/          # UI Components (Dashboard, Reports)
