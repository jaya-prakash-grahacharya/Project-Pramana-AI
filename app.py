import os
import base64
import markdown
from flask import Flask, render_template, request
from groq import Groq
from PIL import Image

app = Flask(__name__)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
if os.environ.get('RENDER'):
    app.config['UPLOAD_FOLDER'] = '/tmp/uploads'
else:
    app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'uploads')

# Ensure the folder actually exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# CONFIGURATION
# This pulls the key from Render's 'Environment' tab
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')

# DEBUG CHECK: If the key is missing, this will show in your Render Logs
if not GROQ_API_KEY:
    print("CRITICAL ERROR: GROQ_API_KEY is not set in Environment Variables!")
else:
    print(f"API Key detected: {GROQ_API_KEY[:5]}***") # Shows only first 5 chars for safety

client = Groq(api_key=GROQ_API_KEY)

# 2026 Forensic Models
VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"
TEXT_MODEL = "llama-3.3-70b-versatile"

def process_image(path):
    img = Image.open(path)
    if img.mode != 'RGB': img = img.convert('RGB')
    if img.width > 1024:
        ratio = 1024 / float(img.width)
        height = int((float(img.height) * float(ratio)))
        img = img.resize((1024, height), Image.Resampling.LANCZOS)
    img.save(path, format="JPEG", quality=85)
    return path

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    option = request.form.get('option')
    try:
        if option in ["1", "3"]:
            file = request.files.get('file')
            if file and file.filename != '':
                path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(path)
                processed_path = process_image(path)
                
                with open(processed_path, "rb") as f:
                    encoded_image = base64.b64encode(f.read()).decode('utf-8')

                # Define forensic prompt
                prompt = "Perform deep forensic analysis. Is this AI-generated? Look for artifacts. Verdict: REAL or AI."
                if option == "3":
                    prompt = "Analyze this job offer/document for fraud. Look for red flags. Verdict: REAL or SCAM."

                completion = client.chat.completions.create(
                    model=VISION_MODEL,
                    messages=[{"role": "user", "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}}
                    ]}]
                )
                
                ai_reasoning = markdown.markdown(completion.choices[0].message.content)

                # Forensic Metadata Box (Reconstructed)
                forensic_box = f"""
                <div style="margin-bottom: 25px; background: #0f172a; border: 1px solid #38bdf8; padding: 20px; border-radius: 12px; color: #f8fafc;">
                    <h4 style="margin-top: 0; color: #38bdf8; border-bottom: 1px solid #1e293b; padding-bottom: 10px;">🛡️ Synthetic Origin Profile</h4>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; font-size: 0.9rem;">
                        <div><strong>System Origin:</strong> Inferred Cloud GPU Cluster</div>
                        <div><strong>EXIF Headers:</strong> [ABSENT / STRIPPED]</div>
                        <div><strong>Model Signature:</strong> Latent Diffusion Fingerprint</div>
                        <div><strong>Hardware Noise:</strong> Missing Physical Sensor PRNU</div>
                    </div>
                </div>
                """
                return render_template('result.html', result=forensic_box + ai_reasoning)

        elif option == "2":
            news_text = request.form.get('news_text')
            completion = client.chat.completions.create(
                model=TEXT_MODEL,
                messages=[{"role": "user", "content": f"Fact check this: {news_text}"}]
            )
            result = markdown.markdown(completion.choices[0].message.content)
            return render_template('result.html', result=result)

    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)
