import pdfplumber
import io
import os
from llm_client import call_llm, call_vision_llm
from prompts.topic_prompt import build_topic_prompt

class PDFProcessingService:
    @staticmethod
    def extract_text_standard(file_content: bytes, max_pages: int = None) -> str:
        """Stage 1: Standard PDF text extraction using pdfplumber."""
        text = ""
        with pdfplumber.open(io.BytesIO(file_content)) as pdf:
            pages = pdf.pages[:max_pages] if max_pages else pdf.pages
            for page in pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
        return text.strip()

    @staticmethod
    def extract_text_ocr(file_content: bytes, max_pages: int = None) -> str:
        """Stage 2: OCR extraction using Tesseract."""
        try:
            import pytesseract
            from pdf2image import convert_from_bytes
            
            images = convert_from_bytes(file_content, last_page=max_pages)
            text = ""
            for img in images:
                text += pytesseract.image_to_string(img, lang='tur+eng') + "\n"
            return text.strip()
        except Exception as e:
            print(f"OCR Error: {e}")
            return ""

    @staticmethod
    def extract_text_vision(file_content: bytes, max_pages: int = None) -> str:
        """Stage 3: Vision LLM extraction - Fallback using image-to-text models."""
        from pdf2image import convert_from_bytes
        try:
            images = convert_from_bytes(file_content, last_page=max_pages)
            full_text = ""
            for img in images:
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format='JPEG')
                
                vision_prompt = "Extract all readable text from this document image accurately. Provide only the raw text."
                page_text = call_vision_llm(img_byte_arr.getvalue(), vision_prompt)
                full_text += page_text + "\n"
            return full_text.strip()
        except Exception as e:
            print(f"Vision Extraction Error: {e}")
            return ""

    @classmethod
    def _determine_best_method(cls, file_content: bytes) -> str:
        """
        Decision mechanism based on page count and content comparison of the first two pages.
        """
        with pdfplumber.open(io.BytesIO(file_content)) as pdf:
            total_pages = len(pdf.pages)

        # Direct Vision LLM if 2 pages or fewer
        if total_pages <= 2:
            print(f"PDF has {total_pages} page(s). Using Vision LLM directly.")
            return "vision"

        print(f"Analyzing {total_pages} pages. Testing first two pages...")
        
        std_sample = cls.extract_text_standard(file_content, max_pages=2)
        ocr_sample = cls.extract_text_ocr(file_content, max_pages=2)
        vis_sample = cls.extract_text_vision(file_content, max_pages=2)

        len_std = len(std_sample)
        len_ocr = len(ocr_sample)
        len_vis = len(vis_sample)

        # Decision Logic:
        # 1. All same? Use standard.
        if len_std == len_ocr == len_vis and len_std > 0:
            return "standard"
        
        # 2. Standard is less, but OCR and Vision are same? Use OCR.
        if len_std < len_ocr and len_ocr == len_vis:
            return "ocr"
            
        # 3. Vision is better than both? Use Vision.
        if len_std < len_vis and len_ocr < len_vis:
            return "vision"

        return "standard"

    @classmethod
    def process_pdf_to_text(cls, file_content: bytes) -> dict:
        """Main entry point to convert PDF to text using the selected best method."""
        best_method = cls._determine_best_method(file_content)
        print(f"Final Decision: Using '{best_method}' method.")

        if best_method == "ocr":
            text = cls.extract_text_ocr(file_content)
        elif best_method == "vision":
            text = cls.extract_text_vision(file_content)
        else:
            text = cls.extract_text_standard(file_content)

        return {"text": text, "method": best_method}

    @staticmethod
    def convert_text_to_json_via_llm(raw_text: str):
        """Stage 4: Structure text into JSON using standard LLM."""
        if not raw_text:
            return None
        prompt = build_topic_prompt(raw_text)
        content = call_llm(prompt, temperature=0.0)
        return content