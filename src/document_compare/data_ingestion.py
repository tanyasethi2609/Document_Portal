import sys
from pathlib import Path 
import pymupdf as fitz
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException

class DocumentIngestion():
    def __init__(self, base_dir:str = "C:\\Users\\ARSHPARAM\\tanya\\Document_Portal\\data\\document_compare"):
        self.log = CustomLogger().get_logger(__name__)
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)


    def delete_existing_files(self):
        '''
        Deletes existing files at the specified paths.
        '''
        try:
            if self.base_dir.exists() and self.base_dir.is_dir():
                for file in self.base_dir.iterdir():
                    if file.is_file():
                        file.unlink()
        except Exception as e:
           self.log.error(f"Error occurred while deleting existing files: {e}")
           raise DocumentPortalException("An error occurred while deleting existing files", sys)

    def save_uploaded_files(self,reference_file,actual_file):
        '''
        Saves the uploaded files to the specific directory.
        '''
        try:
            self.delete_existing_files()
            self.log.info("Existing files deleted successfully")

            ref_path = self.base_dir/ reference_file.name
            act_path = self.base_dir/ actual_file.name
            if not reference_file.name.endswith(".pdf") or not actual_file.name.endswith(".pdf"):
                raise ValueError("Both files must be PDF format")
            
            with open(ref_path, 'wb') as ref_f:
                ref_f.write(reference_file.getbuffer())

            with open(act_path, 'wb') as act_f:
                act_f.write(actual_file.getbuffer())

            self.log.info("Files saved", reference = str(ref_path), actual = str(act_path))
            return ref_path, act_path

        except Exception as e:
           self.log.error(f"Error occurred while reading PDF: {e}")
           raise DocumentPortalException("An error occurred while saving uploaded files", sys)

    def read_pdf(self,pdf_path:Path) -> str:
        '''
        Reads a PDF file and extracts text from each page.
        '''
        try:
            with fitz.open(pdf_path) as doc:
                if doc.is_encrypted:
                    raise ValueError(f"The PDF file is encrypted {pdf_path.name}")
                all_text = []
                for page_num in range(doc.page_count):
                    page = doc.load_page(page_num)
                    page_text = page.get_text()
                    if page_text.strip():
                        all_text.append(f"Page {page_num + 1} --- \n{page_text.strip()}")
                self.log.info(f"Successfully read PDF", file = str(pdf_path), pages=len(all_text))
            return "\n".join(all_text)
        except Exception as e:
           self.log.error(f"Error occurred while reading PDF: {e}")
           raise DocumentPortalException("An error occurred while reading PDF", sys)
        
    def combine_documents(self)->str:
        try:
            content_dict = {}
            doc_parts = []
            
            for filename in sorted(self.base_dir.iterdir()):
                if filename.is_file() and filename.suffix.lower() == '.pdf':
                    content_dict[filename.name] = self.read_pdf(filename)

            for file_name, content in content_dict.items():
                doc_parts.append(f"Document: {file_name}\n{content}")

            combined_text = "\n\n".join(doc_parts)
            self.log.info("Documents combined successfully", num_parts=len(doc_parts))
            return combined_text
        except Exception as e:
            self.log.error(f"Error occurred while combining documents: {e}")
            raise DocumentPortalException("An error occurred while combining documents", sys)
    
    def clean_old_sessions(self, keep_latest: int = 3):
        try:
            sessions = sorted([f for f in self.base_dir.iterdir() if f.is_dir()], reverse=True)
            for folder in sessions[keep_latest:]:
                shutil.rmtree(folder, ignore_errors=True)
                log.info("Old session folder deleted", path=str(folder))
        except Exception as e:
            log.error("Error cleaning old sessions", error=str(e))
            raise DocumentPortalException("Error cleaning old sessions", e) from e
        
