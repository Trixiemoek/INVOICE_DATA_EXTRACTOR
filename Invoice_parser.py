import streamlit as st
import google.generativeai as genai
import os
import mimetypes
import json

# ------------------------------
# Load Gemini API Key from Streamlit Secrets
# ------------------------------
# On Streamlit Cloud, add gemini_api in the Secrets tab (Settings → Secrets)
api_key = os.environ.get("gemini_api")

if not api_key:
    st.error("❌ Gemini API key not found in Streamlit Secrets.")
    st.stop()

genai.configure(api_key=api_key)

# ------------------------------
# Gemini Model Config
# ------------------------------
model = genai.GenerativeModel(
    model_name="models/gemini-2.5-pro",
    generation_config={"temperature": 0.1, "max_output_tokens": 4096}
)

# ------------------------------
# Helper Functions
# ------------------------------
def read_file(upload):
    """Read uploaded PDF or image file for Gemini."""
    mime_type = upload.type
    if mime_type not in ["image/png", "image/jpeg", "application/pdf"]:
        raise ValueError("⚠️ Unsupported file type.")
    return {"mime_type": mime_type, "data": upload.read()}

def clean_json_text(text):
    """Remove markdown code fences and validate JSON."""
    text = text.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        raise ValueError("❌ Model returned invalid JSON. Try adjusting prompt.")

# ------------------------------
# Streamlit UI
# ------------------------------
st.title("💡 InvoicePasa - Extract Info from Your Invoice")
st.write("""
Upload your invoice (PDF or Image) and get a clean structured JSON output.
Extract details like invoice number, narration, amounts, customer info, and line items automatically.
""")

uploaded = st.file_uploader("Upload Invoice File", type=["pdf", "png", "jpg", "jpeg"])

if uploaded:
    st.success("✅ File uploaded successfully!")

    system_prompt = """
    You are an expert in extracting structured data from invoices.
    Return ONLY pure JSON.
    Do NOT include explanations, comments, or markdown formatting.
    """

    user_prompt = """
    Convert the uploaded invoice into a clean structured JSON object.
    Only return JSON. Include invoice number, narration, amounts, dates, customer info, and line items.
    """

    if st.button("Extract Invoice Data"):
        with st.spinner("Extracting data... please wait"):
            file_data = read_file(uploaded)
            response = model.generate_content([system_prompt, file_data, user_prompt])
            raw_text = response.text

            try:
                json_data = clean_json_text(raw_text)
                st.success("✅ Extraction successful!")
                st.json(json_data)
            except Exception as e:
                st.error(str(e))
                st.write("Raw model output for debugging:")
                st.code(raw_text)
