import os
import sys
import io
from dotenv import load_dotenv

# Projenin ana dizinini path'e ekle
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.pdf_service import PDFProcessingService

# .env dosyasındaki API anahtarlarını yükle
load_dotenv()

def run_test(pdf_filename):
    """
    Tests the entire PDF processing flow including the decision mechanism.
    Checks both root and tests/ directory for the file.
    """
    # Klasör yollarını belirle
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 1. Ana dizinde ara, bulamazsa 2. tests/ klasöründe ara
    pdf_path = os.path.join(base_dir, pdf_filename)
    if not os.path.exists(pdf_path):
        pdf_path = os.path.join(tests_dir, pdf_filename)

    if not os.path.exists(pdf_path):
        print(f"Error: '{pdf_filename}' not found in root or tests/ directory!")
        print(f"Checked paths:\n1. {os.path.join(base_dir, pdf_filename)}\n2. {os.path.join(tests_dir, pdf_filename)}")
        return

    print(f"\n--- Starting Flow Test: {pdf_path} ---")
    
    try:
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()

        # Karar mekanizmasını ve işleme akışını tetikle
        result = PDFProcessingService.process_pdf_to_text(pdf_bytes)

        print("-" * 40)
        print(f"DECISION: {result['method'].upper()} method was selected.")
        print(f"TEXT LENGTH: {len(result['text'])} characters.")
        
        if result['text']:
            print("\nTEXT PREVIEW (First 300 chars):")
            print(result['text'][:300] + "...")
        else:
            print("\nWARNING: No text could be extracted.")
        print("-" * 40)

    except Exception as e:
        print(f"An error occurred during testing: {e}")

if __name__ == "__main__":
    # Test dosyasının adını buraya yaz
    test_file = "deneme.pdf" 
    run_test(test_file)