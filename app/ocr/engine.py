import fitz  # PyMuPDF
import easyocr
import numpy as np
from PIL import Image
import io
import logging

logger = logging.getLogger(__name__)

class OCREngine:
    def __init__(self):
        # Initialize EasyOCR reader once in memory for speed
        self.reader = easyocr.Reader(['en'], gpu=False)

    def extract_text_from_scanned_pdf(self, file_bytes: bytes) -> str:
        extracted_text = []
        try:
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            for page_num in range(len(doc)):
                page = doc[page_num]
                pix = page.get_pixmap(dpi=200)
                img = Image.open(io.BytesIO(pix.tobytes()))
                img_np = np.array(img)
                
                results = self.reader.readtext(img_np, detail=0)
                page_text = " ".join(results)
                extracted_text.append(page_text)
            return "\n".join(extracted_text)
        except Exception as e:
            logger.error(f"OCR Extraction failed: {str(e)}")
            return ""