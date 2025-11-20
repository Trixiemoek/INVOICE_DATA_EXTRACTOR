import streamlit as st
from PIL import Image
import pytesseract
from pdf2image import convert_from_bytes
import re

# Path to your installed Tesseract OCR executable
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

st.set_page_config(page_title="Invoice Extractor", page_icon="🧾")
st.title("🧾 Offline Invoice Extractor (Image/PDF)")

# --- File Uploader ---
uploaded_file = st.file_uploader("Upload Invoice (PDF, JPG, PNG)", type=["pdf", "jpg", "png"])

# --- Extraction Helpers ---
def extract_invoice_number(text):
    patterns = [
        r"Invoice\s*#?:?\s*([\w\-\/]+)",
        r"Invoice No\.?\s*[:\-]?\s*([\w\-\/]+)",
        r"\bINV[\d\-]+"
    ]
    for pat in patterns:
        match = re.search(pat, text, re.IGNORECASE)
        if match:
            return match.group(1)
    return "Not found"

def extract_total(text):
    patterns = [
        r"Total\s*[:\-]?\s*(KES|USD|\$)?\s*([\d,]+\.\d{2})",
        r"(KES|USD|\$)?\s*([\d,]+\.\d{2})\s*Total",
        r"Amount\s*Due\s*[:\-]?\s*(KES|USD|\$)?\s*([\d,]+\.\d{2})",
    ]
    for pat in patterns:
        match = re.search(pat, text, re.IGNORECASE)
        if match:
            currency = match.group(1) or ""
            amount = match.group(2)
            return f"{currency} {amount}".strip()
    return "Not found"

def extract_vendor(text):
    lines = text.splitlines()
    for line in lines[:15]:  # Check more lines for better match
        if re.search(r"(Ltd|Limited|Company|Enterprises|Inc|Nairobi|PO Box|Kenya)", line, re.IGNORECASE):
            return line.strip()
    return "Not found"

def extract_period(text):
    patterns = [
        r"(\d{2}/\d{2}/\d{4})\s*[-–to]+\s*(\d{2}/\d{2}/\d{4})",
        r"Start\s*[:\-]?\s*(\d{2}/\d{2}/\d{4})\s*.*?End\s*[:\-]?\s*(\d{2}/\d{2}/\d{4})"
    ]
    for pat in patterns:
        match = re.search(pat, text, re.IGNORECASE)
        if match:
            return f"{match.group(1)} to {match.group(2)}"
    return "Not found"

def extract_narration(text):
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if re.search(r"(Narration|Payment For|Purpose|Description)", line, re.IGNORECASE):
            if i + 1 < len(lines):
                return lines[i + 1].strip()
            match = re.search(r"(?:Narration|Payment For|Purpose|Description)\s*[:\-]?\s*(.+)", line, re.IGNORECASE)
            if match:
                return match.group(1).strip()
    return "Not found"

def extract_all(text):
    return {
        "Invoice Number": extract_invoice_number(text),
        "Total": extract_total(text),
        "Vendor": extract_vendor(text),
        "Payment Period": extract_period(text),
        "Payment Narration": extract_narration(text),
    }

# --- Main App Logic ---
if uploaded_file:
    try:
        # Convert PDF to image or read uploaded image
        if uploaded_file.type == "application/pdf":
            images = convert_from_bytes(uploaded_file.read(), dpi=300)
            image = images[0]
        else:
            image = Image.open(uploaded_file)

        # OCR text extraction
        text = pytesseract.image_to_string(image)

        st.subheader("🧾 Extracted OCR Text")
        st.text_area("Raw Text", text, height=250)

        # Field extraction
        extracted = extract_all(text)

        st.subheader("🧠 Extracted Fields")
        invoice_number = st.text_input("Invoice Number", extracted["Invoice Number"])
        total = st.text_input("Total Amount", extracted["Total"])
        vendor = st.text_input("Vendor Name", extracted["Vendor"])
        period = st.text_input("Payment Period", extracted["Payment Period"])
        narration = st.text_area("Payment Narration", extracted["Payment Narration"])

        if st.button("✅ Confirm & Save"):
            st.success("Invoice saved with the following details:")
            st.json({
                "Invoice Number": invoice_number,
                "Total": total,
                "Vendor": vendor,
                "Payment Period": period,
                "Payment Narration": narration,
            })

    except Exception as e:
        st.error(f"⚠️ Error reading file: {e}")
