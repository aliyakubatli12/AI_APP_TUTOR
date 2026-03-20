from fastapi import APIRouter, UploadFile, File, HTTPException
from services.pdf_service import PDFProcessingService
from tools.topic_extractor.topic_extractor import extract_topics
import json

router = APIRouter()

@router.post("/analyze-pdf")
async def analyze_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Invalid file type.")

    content = await file.read()
    
    # Step 1 & 2: Get text from PDF (Standard or OCR)
    extracted_text = PDFProcessingService.process_pdf_to_text(content)
    
    if not extracted_text:
        raise HTTPException(status_code=422, detail="Content could not be extracted even with OCR.")

    # Step 3: Convert to JSON and Extract Topics
    # Here we use your existing pipeline which already handles LLM conversion
    try:
        result = extract_topics(extracted_text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))