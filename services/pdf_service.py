import pdfplumber
import io
import os
from tools.llm_client import call_llm
from prompts.topic_prompt import build_topic_prompt

class PDFProcessingService:
    @staticmethod
    def extract_text_standard(file_content: bytes) -> str:
        """Stage 1: Standard PDF text extraction using pdfplumber."""
        text = ""
        # Create a file-like object from bytes for pdfplumber
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
            
            # If running in Docker, these tools are pre-installed in the path.
            # If on Windows, specify the tesseract executable path here if not in PATH:
            # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
            
            # Convert PDF pages to images for character recognition
            images = convert_from_bytes(file_content)
            text = ""
            for img in images:
                # Using 'tur+eng' language support to recognize Turkish and English characters simultaneously
                text += pytesseract.image_to_string(img, lang='tur+eng') + "\n"
            return text.strip()
        except ImportError:
            # Handle cases where required OCR libraries are missing from the environment
            return ""
        except Exception as e:
            # Log unexpected errors during the OCR process
            print(f"OCR Error: {e}")
            return ""

    @classmethod
    def process_pdf_to_text(cls, file_content: bytes) -> str:
        """Orchestrates the extraction stages."""
        # 1. Try standard extraction
        text = cls.extract_text_standard(file_content)
        
        # 2. If standard fails (e.g., the PDF is image-based), try OCR
        if not text:
            # Inform the user or logs that the fallback OCR mechanism is being activated
            print("Standard extraction returned empty text. Attempting Tesseract OCR...")
            text = cls.extract_text_ocr(file_content)
            
        return text

    @staticmethod
    def convert_text_to_json_via_llm(raw_text: str):
        """Stage 3: Use LLM to structure any text into the target JSON format."""
        if not raw_text:
            return None
            
        # We reuse your existing prompt logic to ensure consistency
        # This sends the extracted raw text to the LLM to identify topics
        prompt = build_topic_prompt(raw_text)
        content = call_llm(prompt, temperature=0.0)
        return content # This returns the JSON string from LLM