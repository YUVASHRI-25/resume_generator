from __future__ import annotations

import os
import tempfile
from typing import Tuple
from uuid import uuid4

from fastapi import UploadFile

from . import text_extraction_service, nlp_parsing_service
from ..models import ResumeData, StoredResume
from ..storage import storage


UPLOAD_DIR = os.path.join(tempfile.gettempdir(), "resume_uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


async def handle_resume_upload(file: UploadFile, template_id: str) -> Tuple[str, ResumeData]:
    """Save uploaded PDF, extract text (with OCR fallback), parse, and persist resume.

    Returns a tuple of (resume_id, parsed_resume_data).
    """
    tmp_path = None
    try:
        # Persist uploaded file to a temporary location
        suffix = os.path.splitext(file.filename or "resume.pdf")[1] or ".pdf"
        with tempfile.NamedTemporaryFile(delete=False, dir=UPLOAD_DIR, suffix=suffix) as tmp:
            contents = await file.read()
            if not contents:
                raise ValueError("Uploaded file is empty")
            tmp.write(contents)
            tmp_path = tmp.name

        # Extract raw text from the PDF (text-based or scanned)
        raw_text = text_extraction_service.extract_text_with_ocr_fallback(tmp_path)
        
        if not raw_text or len(raw_text.strip()) < 10:
            raise ValueError("Could not extract text from PDF. The file might be corrupted or password-protected.")

        # NLP-based parsing into structured resume data
        resume_data: ResumeData = nlp_parsing_service.parse_resume(raw_text)

        # Store in in-memory store for reuse across template switches
        resume_id = uuid4()
        stored = StoredResume(resume_id=resume_id, template_id=template_id, data=resume_data)
        storage.save_resume(stored)

        # Convert UUID to string and ensure resume_data is serializable
        return str(resume_id), resume_data
    except Exception as e:
        # Clean up temp file on error
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except:
                pass
        raise
