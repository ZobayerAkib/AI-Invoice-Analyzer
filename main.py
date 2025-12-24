from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from openai import OpenAI
from dotenv import load_dotenv
import os
import base64
import fitz  # PyMuPDF
from typing import Optional, Union

# -------------------------
# Load environment variables
# -------------------------
load_dotenv()

BASE_URL = os.getenv("BASE_URL")
API_KEY = os.getenv("API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME")

if not BASE_URL or not API_KEY or not MODEL_NAME:
    raise ValueError("Please set BASE_URL, API_KEY, and MODEL_NAME in .env")

# -------------------------
# Initialize OpenAI Client
# -------------------------
client = OpenAI(
    base_url=BASE_URL,
    api_key=API_KEY,
)

# -------------------------
# FastAPI App
# -------------------------
app = FastAPI(title="AI Invoice Analyzer")

# -------------------------
# Serve static files (index.html)
# -------------------------
app.mount("/static", StaticFiles(directory="."), name="static")

# -------------------------
# Response Schema
# -------------------------
class InvoiceData(BaseModel):
    vendor: Optional[str] = None
    invoice_number: Optional[str] = None
    invoice_date: Optional[str] = None
    due_date: Optional[str] = None
    total_amount: Union[str, float]
    currency: Optional[str] = "USD"
    valid: bool = True



# -------------------------
# Helpers
# -------------------------
def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text.strip()


def normalize_invoice(data: InvoiceData) -> InvoiceData:
    if isinstance(data.total_amount, float):
        data.total_amount = f"{data.total_amount:.2f}"
    return data


# -------------------------
# API Endpoint
# -------------------------
@app.post("/analyze-invoice", response_model=InvoiceData)
async def analyze_invoice(file: UploadFile = File(...)):
    if file.content_type not in [
        "image/png",
        "image/jpeg",
        "application/pdf",
    ]:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    file_bytes = await file.read()

    prompt = """
You are an AI system specialized in parsing invoices and receipts from BOTH
IMAGES and PDF DOCUMENTS.

Your task:
Carefully read ALL visible or extracted text, including:
- Company / Store / Seller name
- Logo text
- Header text at the top of the document
- Footer text
- Invoice metadata blocks
- Total and payment sections

VENDOR EXTRACTION (VERY IMPORTANT):
- The vendor is the STORE / COMPANY / SELLER issuing the invoice.
- It is usually the MOST PROMINENT business name.
- It is often located at the TOP of the image or the FIRST lines of the PDF text.
- If text such as "Seller", "Store", "Ltd", or similar appears,
  that MUST be returned as the vendor.
- Ignore customer names, delivery names, and payment gateways.

Extract and return ONLY valid JSON with the following fields:
- vendor (string or null)
- invoice_number (string or null)
- invoice_date (string or null, format YYYY-MM-DD if possible)
- due_date (string or null, format YYYY-MM-DD if possible)
- total_amount (string or number)
- currency (ISO 4217 code like USD, BDT, EUR if visible; otherwise null)
- valid (true or false)

Rules:
- Use null if a field is missing or not clearly visible.
- Do NOT guess values.
- Do NOT hallucinate.
- If critical fields like vendor or total_amount are missing,
  set valid to false.
- Do NOT include explanations or extra text.
- Output MUST be valid JSON ONLY.


"""

    try:
        # ---------- PDF ----------
        if file.content_type == "application/pdf":
            extracted_text = extract_text_from_pdf(file_bytes)

            if not extracted_text:
                raise HTTPException(
                    status_code=400,
                    detail="No readable text found in PDF (possibly scanned)"
                )

            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": "You extract invoice data from text."},
                    {
                        "role": "user",
                        "content": f"{prompt}\n\nINVOICE TEXT:\n{extracted_text}"
                    }
                ],
                temperature=0,
            )

        # ---------- IMAGE ----------
        else:
            encoded_image = base64.b64encode(file_bytes).decode("utf-8")

            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": "You extract invoice data from images."},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{file.content_type};base64,{encoded_image}"
                                }
                            }
                        ]
                    }
                ],
                temperature=0,
            )

        result = response.choices[0].message.content
        invoice = InvoiceData.model_validate_json(result)
        return normalize_invoice(invoice)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------
# Health Check
# -------------------------
@app.get("/")
def health():
    return {"status": "AI Invoice Analyzer running"}
