import pdfplumber
import io
from tools.llm_client import call_llm
from prompts.topic_prompt import build_topic_prompt

class PDFProcessingService:
    @staticmethod
    def extract_text_standard(file_content: bytes) -> str:
        """Stage 1: Standard PDF text extraction using pdfplumber."""
        text = ""
        with pdfplumber.open(io.BytesIO(file_content)) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
        return text.strip()

    @staticmethod
    def extract_text_ocr(file_content: bytes) -> str:
        """Stage 2: OCR extraction (requires pytesseract and pdf2image)."""
        # Note: This part requires Tesseract OCR to be installed on your system.
        # For now, it's a placeholder to guide your architecture.
        try:
            import pytesseract
            from pdf2image import convert_from_bytes
            images = convert_from_bytes(file_content)
            text = ""
            for img in images:
                text += pytesseract.image_to_string(img) + "\n"
            return text.strip()
        except ImportError:
            return ""

    @classmethod
    def process_pdf_to_text(cls, file_content: bytes) -> str:
        """Orchestrates the extraction stages."""
        # 1. Try standard extraction
        text = cls.extract_text_standard(file_content)
        
        # 2. If standard fails, try OCR
        if not text:
            text = cls.extract_text_ocr(file_content)
            
        return text

    @staticmethod
    def convert_text_to_json_via_llm(raw_text: str):
        """Stage 3: Use LLM to structure any text into the target JSON format."""
        if not raw_text:
            return None
            
        # We reuse your existing prompt logic to ensure consistency
        prompt = build_topic_prompt(raw_text)
        content = call_llm(prompt, temperature=0.0)
        return content # This returns the JSON string from LLM