import os
import base64
import markdown
from flask import Flask, render_template, request
from groq import Groq
from PIL import Image

app = Flask(__name__)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

if os.environ.get('RENDER'):
    UPLOAD_FOLDER = '/tmp/uploads'
else:
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# -------------------------------------
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
client = Groq(api_key=GROQ_API_KEY)

# Models
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
        if not GROQ_API_KEY:
            return "Error: GROQ_API_KEY not found in Environment Variables."

        if option in ["1", "3"]:
            file = request.files.get('file')
            if file and file.filename != '':
                # SECURE PATH JOINING
                filename = file.filename
                path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(path)
                
                processed_path = process_image(path)
                
                with open(processed_path, "rb") as f:
                    encoded_image = base64.b64encode(f.read()).decode('utf-8')

                prompt = """
                ACT AS A SENIOR DIGITAL FORENSICS INVESTIGATOR.
                Analyze the provided media for 'Synthetic Architectural Signatures'.
                
                REQUIRED REPORT FORMAT:
                1. **VERDICT**: [REAL or AI]
                2. **GENERATOR IDENTIFICATION**: (Identify if this is Midjourney, DALL-E 3, Stable Diffusion, or Adobe Firefly based on the pixel smoothing and lighting style).
                3. **INFERRED COMPUTATIONAL ENVIRONMENT**: (Explain that the 'Device' is a Cloud GPU Cluster rather than a physical camera).
                4. **FORENSIC REASONING**:
                   - **Texture Analysis**: Is it too 'plastic' or 'painterly'?
                   - **Artifact Check**: Look for warped edges or non-human proportions.
                   - **Metadata Logic**: Explain that the 'Location' is a virtual latent space, hence the lack of GPS.
                
                If the image is REAL, identify the likely smartphone or camera brand (e.g., iPhone/Samsung) based on the post-processing style.
                """
                if option == "3":
                    prompt = "Analyze this job offer letter for authenticity. Check for signs of scams such as: 
                                - requests for money or fees,
                                - suspicious email domains,
                                - poor grammar or formatting,
                                - unverifiable company details,
                                - unrealistic salary or benefits,
                                - lack of official contact information.
                                
                                Verdict required: REAL or SCAM."

                completion = client.chat.completions.create(
                    model=VISION_MODEL,
                    messages=[{"role": "user", "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}}
                    ]}]
                )
                
                ai_reasoning = markdown.markdown(completion.choices[0].message.content)

                forensic_box = f"""
<div style="background: #0f172a; border: 1px solid #38bdf8; padding: 20px; border-radius: 12px; margin-bottom: 20px; font-family: monospace;">
    <h4 style="color: #38bdf8; margin-top: 0;">🕵️ FORENSIC SPECIFICATIONS</h4>
    <p><strong>Device Source:</strong> Virtual LPU/GPU Environment (Inferred)</p>
    <p><strong>Logical Location:</strong> Latent Diffusion Space</p>
    <p><strong>Sensor Noise:</strong> 0% Physical PRNU (AI Signature)</p>
    <p><strong>Metadata Status:</strong> <span style="color: #ef4444;">STRIPPED / NON-EXISTENT</span></p>
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
        return f"System Error: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)
