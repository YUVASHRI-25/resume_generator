from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from uuid import UUID
from typing import List, Dict, Any, Optional
import json

from ..services import file_service, template_mapping_service, summary_generation_service
from ..storage import storage
from ..models import ParsedResumeResponse, ChangeTemplateRequest, GenerateSummaryRequest, GenerateSummaryResponse, ResumeData

router = APIRouter(prefix="", tags=["resume"])


def ensure_uuid_serialization(response_data: dict) -> dict:
    """Ensure UUID objects are converted to strings for JSON serialization.
    
    This is a safety net to ensure UUIDs are JSON-serializable.
    """
    if isinstance(response_data.get("resume_id"), UUID):
        response_data["resume_id"] = str(response_data["resume_id"])
    return response_data


def ensure_education_normalization(response_data: dict) -> dict:
    """Ensure education entries have correct field names for frontend.
    
    This is a safety net to ensure normalization happens even if model_dump() is bypassed.
    """
    if response_data.get("data") and isinstance(response_data["data"], dict):
        education_list = response_data["data"].get("education")
        if education_list:
            normalized = []
            for edu in education_list:
                if isinstance(edu, dict):
                    normalized.append({
                        "institution": str(edu.get("institution") or edu.get("school_name") or ""),
                        "location": str(edu.get("location") or ""),
                        "degree": str(edu.get("degree") or ""),
                        "start_year": str(edu.get("start_year") or edu.get("start_date") or ""),
                        "end_year": str(edu.get("end_year") or edu.get("end_date") or ""),
                        "description": str(edu.get("description") or ""),
                    })
                else:
                    # If it's an object, try to get attributes
                    normalized.append({
                        "institution": str(getattr(edu, 'institution', None) or getattr(edu, 'school_name', None) or ""),
                        "location": str(getattr(edu, 'location', None) or ""),
                        "degree": str(getattr(edu, 'degree', None) or ""),
                        "start_year": str(getattr(edu, 'start_year', None) or getattr(edu, 'start_date', None) or ""),
                        "end_year": str(getattr(edu, 'end_year', None) or getattr(edu, 'end_date', None) or ""),
                        "description": str(getattr(edu, 'description', None) or ""),
                    })
            response_data["data"]["education"] = normalized
    return response_data


def normalize_education(education_list: List[Any]) -> List[Dict[str, str]]:
    """Normalize education entries to match frontend expected format.
    
    Maps:
    - school_name → institution
    - start_date → start_year
    - end_date → end_year
    
    Returns empty strings for missing fields.
    """
    if not education_list:
        return []
    
    normalized = []
    for edu in education_list:
        # Handle both dict and EducationEntry objects
        if isinstance(edu, dict):
            normalized.append({
                "institution": edu.get("institution") or edu.get("school_name") or "",
                "location": edu.get("location") or "",
                "degree": edu.get("degree") or "",
                "start_year": edu.get("start_year") or edu.get("start_date") or "",
                "end_year": edu.get("end_year") or edu.get("end_date") or "",
                "description": edu.get("description") or "",
            })
        else:
            # If it's an EducationEntry object, use its model_dump
            normalized.append(edu.model_dump())
    
    return normalized


def normalize_resume_data(resume_data: ResumeData) -> ResumeData:
    """Normalize ResumeData to ensure education fields match frontend format.
    
    This ensures that when FastAPI serializes the response, education entries
    have the correct field names (institution, start_year, end_year) that the frontend expects.
    """
    if resume_data.education:
        # The EducationEntry.model_dump() already handles the mapping,
        # but we ensure it's called by converting to dict and back if needed
        # Actually, since we're using model_dump() in EducationEntry, this should work
        # But to be extra safe, we ensure the data structure is correct
        pass  # The model_dump() in EducationEntry already handles normalization
    return resume_data


@router.post("/upload-resume", response_model=ParsedResumeResponse)
async def upload_resume(file: UploadFile = File(...), template_id: str = Form(...)):
    # Check file extension instead of content_type (more reliable)
    filename = file.filename or ""
    if not filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    # Also check content type if available, but be flexible
    if file.content_type and file.content_type not in ["application/pdf", "application/x-pdf"]:
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    try:
        resume_id_str, parsed_resume = await file_service.handle_resume_upload(file, template_id)
        resume_id_uuid = UUID(resume_id_str)

        # Create response object
        response_obj = ParsedResumeResponse(resume_id=resume_id_uuid, template_id=template_id, data=parsed_resume)
        
        # CRITICAL: Get normalized data using model_dump() to ensure education fields are correctly mapped
        # This ensures frontend receives: institution, start_year, end_year (not school_name, start_date, end_date)
        response_data = response_obj.model_dump()
        
        # Double-check normalization (safety net)
        response_data = ensure_education_normalization(response_data)
        # Ensure UUID is converted to string for JSON serialization
        response_data = ensure_uuid_serialization(response_data)
        
        # Return as JSONResponse to ensure our normalization is used
        return JSONResponse(content=response_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing resume: {str(e)}")


@router.get("/resume/{resume_id}", response_model=ParsedResumeResponse)
async def get_resume(resume_id: UUID):
    stored = storage.get_resume(resume_id)
    if not stored:
        raise HTTPException(status_code=404, detail="Resume not found")

    # Create response and normalize education fields
    response_obj = ParsedResumeResponse(resume_id=resume_id, template_id=stored.template_id, data=stored.data)
    response_data = response_obj.model_dump()
    response_data = ensure_education_normalization(response_data)
    # Ensure UUID is converted to string for JSON serialization
    response_data = ensure_uuid_serialization(response_data)
    return JSONResponse(content=response_data)


@router.post("/change-template", response_model=ParsedResumeResponse)
async def change_template(payload: ChangeTemplateRequest):
    updated = template_mapping_service.change_template(payload.resume_id, payload.template_id)
    if not updated:
        raise HTTPException(status_code=404, detail="Resume not found")

    # Create response and normalize education fields
    response_obj = ParsedResumeResponse(resume_id=updated.resume_id, template_id=updated.template_id, data=updated.data)
    response_data = response_obj.model_dump()
    response_data = ensure_education_normalization(response_data)
    # Ensure UUID is converted to string for JSON serialization
    response_data = ensure_uuid_serialization(response_data)
    return JSONResponse(content=response_data)


@router.post("/generate-summary", response_model=GenerateSummaryResponse)
async def generate_summary(payload: GenerateSummaryRequest):
    """Generate a professional summary based on job description using google/flan-t5-base model."""
    try:
        # Convert ResumeData to dict if provided
        resume_dict = None
        if payload.resume_data:
            resume_dict = payload.resume_data.model_dump() if hasattr(payload.resume_data, 'model_dump') else payload.resume_data.dict()
        
        summary = await summary_generation_service.generate_summary_from_job_description(
            job_description=payload.job_description,
            resume_data=resume_dict
        )
        
        return GenerateSummaryResponse(summary=summary)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating summary: {str(e)}")


