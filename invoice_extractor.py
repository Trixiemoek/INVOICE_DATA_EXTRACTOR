import streamlit as st
from invoice2data import extract_data
from invoice2data.extract.loader import read_templates
import os
import tempfile

# Directory where templates are stored
TEMPLATES_DIR = r"C:\Users\HomePC\Documents\PERSONAL PROJECTS\INVOICE2DATAMODEL\Template"

# Function to load templates
def load_templates():
    templates = read_templates(TEMPLATES_DIR)
    return templates

# Function to extract invoice data
def extract_invoice_data(pdf_bytes):
    templates = load_templates()
    
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(pdf_bytes)
            temp_file_path = temp_file.name
        
        result = extract_data(temp_file_path, templates=templates)

        os.remove(temp_file_path)

        if result:
            return result
        else:
            return "No template matched for this invoice."
        
    except Exception as e:
        return f"Error: {e}"

# Streamlit UI
st.title('Invoice Data Extractor')

uploaded_file = st.file_uploader("Choose an invoice PDF", type="pdf")

if uploaded_file is not None:
    st.write("Extracting data from invoice... Please wait.")
    
    result = extract_invoice_data(uploaded_file.read())
    
    if isinstance(result, dict):
        st.success("Invoice data extracted successfully!")
        st.json(result)
    else:
        st.error(result)
