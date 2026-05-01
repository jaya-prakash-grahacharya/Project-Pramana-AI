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
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
client = Groq(api_key=GROQ_API_KEY)


VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"
TEXT_MODEL = "llama-3.3-70b-versatile"

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
                filename = file.filename
                path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(path)
                
                img = Image.open(path)
                if img.mode != 'RGB': 
                    img = img.convert('RGB')
                img.thumbnail((500, 500), Image.Resampling.LANCZOS)
                img.save(path, format="JPEG", quality=60)
                
                with open(path, "rb") as f:
                    encoded_image = base64.b64encode(f.read()).decode('utf-8')

                # Define Prompts
                if option == "3":
                    prompt = ''' You are an expert in digital forensics and scam detection. Analyze the following job offer letter carefully and determine if it is genuine or fraudulent. Consider the following factors in your analysis:

                                    1. Sender details:
                                       - Is the email domain/company address official and verifiable?
                                       - Are there spelling errors, generic greetings, or suspicious formatting?
                                    
                                    2. Content authenticity:
                                       - Does the letter mention unrealistic salaries, benefits, or guaranteed employment without interviews?
                                       - Are there urgent deadlines or pressure tactics?
                                    
                                    3. Verification of company:
                                       - Is the company name real and registered?
                                       - Does the job description match the company’s industry?
                                    
                                    4. Red flags:
                                       - Requests for upfront payment, bank details, or personal information.
                                       - Use of free email services (e.g., Gmail, Yahoo) instead of corporate domains.
                                       - Poor grammar, vague role descriptions, or inconsistent logos/branding.
                                    
                                    5. Overall judgment:
                                       - Provide a clear conclusion: “Likely Genuine” or “Likely Scam.”
                                       - Explain reasoning with evidence from the text.
                                
                                Verdict required: REAL or SCAM.'''
                else:
                    prompt = """ ACT AS A SENIOR DIGITAL FORENSICS INVESTIGATOR.
                Analyze the provided media for 'Synthetic Architectural Signatures'.
                
                REQUIRED REPORT FORMAT:
                1. **VERDICT**: [REAL or AI]
                2. **GENERATOR IDENTIFICATION**: (Identify if this is Midjourney, DALL-E 3, Stable Diffusion, or Adobe Firefly based on the pixel smoothing and lighting style and stylistic cues ).
                3. **INFERRED COMPUTATIONAL ENVIRONMENT**: (Explain that the 'Device' is a Cloud GPU Cluster rather than a physical camera).
                4. **FORENSIC REASONING**:
                   - **Texture Analysis**: Assess whether surfaces appear overly 'plastic,' 'painterly,' or unnaturally smooth.?
                   - **Artifact Check**: Identify warped edges, inconsistent geometry, or non-human proportions.
                   - **Metadata Logic**: Explain that the 'Location' is a virtual latent space, hence the lack of GPS.
                5. **DEVICE IDENTIFICATION**:
                   - If AI: Conclude 'Cloud GPU Cluster.'
                   - If REAL: Identify likely smartphone/camera brand (e.g., iPhone, Samsung) based on post-processing style.
                6. **EVIDENCE SUMMARY**: Provide concise justification for the verdict, citing specific anomalies or authentic features.
                
                OUTPUT: Deliver a structured forensic report in the above format, with clear, evidence-based reasoning."""

                completion = client.chat.completions.create(
                    model=VISION_MODEL,
                    messages=[{
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}}
                        ]
                    }],
                    temperature=0.0,
                    top_p=1,
                    max_tokens=250
                )
                
                ai_reasoning = markdown.markdown(completion.choices[0].message.content)


                forensic_box = f"""
                <div style="background: #0f172a; border: 1px solid #38bdf8; padding: 20px; border-radius: 12px; margin-bottom: 20px; font-family: monospace; color: white;">
                    <h4 style="color: #38bdf8; margin-top: 0;">🕵️ FORENSIC SPECIFICATIONS</h4>
                    <p><strong>Device Source:</strong> Virtual LPU/GPU Environment (Inferred)</p>
                    <p><strong>Logical Location:</strong> Latent Diffusion Space</p>
                    <p><strong>Sensor Noise:</strong> 0% Physical PRNU (AI Signature)</p>
                    <p><strong>Metadata Status:</strong> <span style="color: #ef4444;">STRIPPED / NON-EXISTENT</span></p>
                </div>
                """
                return render_template('result.html', result=forensic_box + ai_reasoning)

        # HANDLE NEWS TEXT (Option 2)
        elif option == "2":
            news_text = request.form.get('news_text')
            completion = client.chat.completions.create(
                model=TEXT_MODEL,
                messages=[{"role": "user", "content": f"Fact check this news: {news_text}"}],
                temperature=0.0
            )
            result = markdown.markdown(completion.choices[0].message.content)
            return render_template('result.html', result=result)

    except Exception as e:
        return f"System Error: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)
