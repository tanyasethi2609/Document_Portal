import os
import fitz
import uuid
from datetime import datetime
from pathlib import Path
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException

class DocHandler:
    """
    PDF save + read (page-wise) for analysis.
    """
    def __init__(self, data_dir = None, session_id = None):
        self.log = CustomLogger().get_logger(__name__)
        self.data_dir = data_dir or os.getenv("DATA_STORAGE_PATH", os.path.join(os.getcwd(), "data", "document_analysis"))
        self.session_id = session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        self.session_path = os.path.join(self.data_dir, self.session_id)
        os.makedirs(self.session_path, exist_ok=True)
        self.log.info("DocHandler initialized", session_id=self.session_id, session_path=self.session_path)

    def save_pdf(self, uploaded_file) -> str:
        try:
            filename = os.path.basename(uploaded_file.name)
            if not filename.lower().endswith(".pdf"):
                raise ValueError("Invalid file type. Only PDFs are allowed.")
            save_path = os.path.join(self.session_path, filename)
            with open(save_path, "wb") as f:
                if hasattr(uploaded_file, "read"):
                    f.write(uploaded_file.read())
                else:
                    f.write(uploaded_file.getbuffer())
            self.log.info("PDF saved successfully", file=filename, save_path=save_path, session_id=self.session_id)
            return save_path
        except Exception as e:
            self.log.error("Failed to save PDF", error=str(e), session_id=self.session_id)
            raise DocumentPortalException(f"Failed to save PDF: {str(e)}", e) from e

    def read_pdf(self, pdf_path: str) -> str:
        try:
            text_chunks = []
            with fitz.open(pdf_path) as doc:
                for page_num in range(doc.page_count):
                    page = doc.load_page(page_num)
                    text_chunks.append(f"\n--- Page {page_num + 1} ---\n{page.get_text()}")  # type: ignore
            text = "\n".join(text_chunks)
            self.log.info("PDF read successfully", pdf_path=pdf_path, session_id=self.session_id, pages=len(text_chunks))
            return text
        except Exception as e:
            self.log.error("Failed to read PDF", error=str(e), pdf_path=pdf_path, session_id=self.session_id)
            raise DocumentPortalException(f"Could not process PDF: {pdf_path}", e) from e

if __name__ == "__main__":
    from pathlib import Path
    from io import BytesIO
    handler = DocHandler()
    print(f"Session ID: {handler.session_id}")
    print(f"Session Path: {handler.session_path}")
    pdf_path = r"C:\\Users\\ARSHPARAM\\tanya\\Document_Portal\\data\\document_analysis\\sample.pdf"



class DummyFile:
    def __init__(self, file_path):
        self.name = Path(file_path).name
        self.file_path = file_path
        
    def getbuffer(self):
        return open(self.file_path, "rb").read()
pdf_path = r"C:\\Users\\ARSHPARAM\\tanya\\Document_Portal\\data\\document_analysis\\sample.pdf"   
dummy_pdf = DummyFile(pdf_path)
handler = DocHandler(session_id="test_session_001")

try:
    saved_path =handler.save_pdf(dummy_pdf)
    print(f"Saved PDF Path: {saved_path}")
    content = handler.read_pdf(saved_path)
    print(f"PDF Content:\n{content[:500]}...")  # Print first 500 characters
except DocumentPortalException as e:
    print(f"Error: {e}")