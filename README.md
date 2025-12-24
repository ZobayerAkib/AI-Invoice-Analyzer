# 🧾 AI Invoice Analyzer (FastAPI + Vision + PDF)

An AI-powered invoice and receipt analyzer that extracts structured invoice data from **images (JPG/PNG)** and **PDF documents** using a Large Language Model (LLM).

The system supports **vision-based parsing**, **PDF text extraction**, and outputs **validated JSON** via a FastAPI backend.

---

## 🚀 Features

- 📸 Parse invoice **images** (JPG, PNG)
- 📄 Parse **text-based PDFs**
- 🤖 Uses GitHub-hosted LLM via OpenAI-compatible SDK
- 🧠 Smart vendor detection (logos, headers, prominent text)
- 🧾 Extracts structured fields:
  - Vendor
  - Invoice number
  - Invoice date
  - Due date
  - Total amount
  - Currency
  - Validation flag
- 🌐 FastAPI REST API
- 🧩 Schema-safe & production-ready (no API crashes)

---

## 📁 Project Structure

```text
ai-invoice-analyzer/
│
├── main.py              # FastAPI backend
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (not committed)
├── .gitignore
└── README.md
```
## ⚙️ Tech Stack
```
Backend: FastAPI, Pydantic
AI Model: GitHub-hosted LLM (OpenAI SDK compatible)
Vision: Image-based invoice parsing
PDF Parsing: PyMuPDF
Frontend: HTML, CSS, JavaScript
Deployment-ready: Uvicorn

```
## 🔐 Environment Setup

Create a .env file in the project root:
````
BASE_URL=https://models.inference.ai.azure.com
API_KEY=your_github_model_api_key
MODEL_NAME=gpt-4o-mini

````
⚠️ Never commit .env to GitHub.

## 📦 Installation

```
pip install -r requirements.txt
```
Required packages:

```
fastapi
uvicorn
openai
python-dotenv
python-multipart
pymupdf

```
## ▶️ Run the Application
```
uvicorn main:app --reload

```
## 📤 API Usage
Upload Invoice (Image or PDF)
```
curl -X POST http://127.0.0.1:8000/analyze-invoice \
  -H "accept: application/json" \
  -F "file=@invoice.jpg"

```
## 📥 Example Response
```

{
  "vendor": "ABC Seller",
  "invoice_number": "INV-2025-019",
  "invoice_date": "2025-12-20",
  "due_date": null,
  "total_amount": "530.00",
  "currency": "BDT",
  "valid": true
}

```
## 🧠 How It Works

### Image Invoices
1. Invoice image is base64 encoded.
2. Sent to a vision-capable LLM.
3. Vendor extracted from logo/header.
4. Structured JSON returned with fields:
   - `vendor`
   - `invoice_number`
   - `invoice_date`
   - `due_date`
   - `total_amount`
   - `currency`
   - `valid`

### PDF Invoices
1. Text extracted using **PyMuPDF**.
2. Extracted text sent to LLM.
3. Invoice fields parsed from content into structured JSON.

## 🙌 Author
```
Md. Zobayer Ibna Kabir
CSE Graduate | AI & ML Enthusiast
GitHub: https://github.com/ZobayerAkib
```

⭐ If you find this project useful, consider giving it a star!
