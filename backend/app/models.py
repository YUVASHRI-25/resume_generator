from __future__ import annotations

from typing import List, Optional, Literal
from uuid import UUID

from pydantic import BaseModel, Field


class Links(BaseModel):
    linkedin: Optional[str] = None
    github: Optional[str] = None
    portfolio: Optional[str] = None
    other: List[str] = Field(default_factory=list)


class Contacts(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    desired_job_title: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None  # Combined location string for frontend compatibility
    country: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    post_code: Optional[str] = None  # post_code for frontend compatibility (not postcode)
    leetcode_url: Optional[str] = None
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None


class ExperienceEntry(BaseModel):
    job_title: Optional[str] = None
    employer: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None


class EducationEntry(BaseModel):
    school_name: Optional[str] = None
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None
    
    def model_dump(self, **kwargs):
        """Serialize to frontend-compatible format with exact field names."""
        data = super().model_dump(**kwargs)
        # Map backend fields to frontend expected fields
        return {
            "institution": data.get("school_name") or "",
            "location": data.get("location") or "",
            "degree": data.get("degree") or "",
            "start_year": data.get("start_date") or "",
            "end_year": data.get("end_date") or "",
            "description": data.get("description") or "",
        }


class Skills(BaseModel):
    technical: List[str] = Field(default_factory=list)
    soft: List[str] = Field(default_factory=list)
    tools: List[str] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=list)


class ProjectEntry(BaseModel):
    project_name: Optional[str] = None
    description: Optional[str] = None
    technologies: List[str] = Field(default_factory=list)
    link: Optional[str] = None


class CertificateEntry(BaseModel):
    certificate_name: Optional[str] = None
    issuing_organization: Optional[str] = None
    date_of_completion: Optional[str] = None  # MM/YYYY format
    credential_id: Optional[str] = None
    credential_url: Optional[str] = None
    
    def model_dump(self, **kwargs):
        """Serialize to frontend-compatible format with camelCase field names."""
        data = super().model_dump(**kwargs)
        return {
            "name": data.get("certificate_name"),
            "organization": data.get("issuing_organization"),
            "completionDate": data.get("date_of_completion"),
            "credentialId": data.get("credential_id"),
            "credentialUrl": data.get("credential_url"),
        }


class ResumeData(BaseModel):
    contacts: Optional[Contacts] = None
    experience: Optional[List[ExperienceEntry]] = None
    education: Optional[List[EducationEntry]] = None
    skills: Optional[Skills] = None
    projects: Optional[List[ProjectEntry]] = None
    certifications: Optional[List[CertificateEntry]] = None
    achievements: Optional[List[str]] = None
    summary: Optional[str] = None
    
    def model_dump(self, **kwargs):
        """Serialize with proper handling of CertificateEntry and EducationEntry objects."""
        data = super().model_dump(**kwargs)
        # Convert CertificateEntry objects to frontend format
        if self.certifications:
            data["certifications"] = [
                cert.model_dump() if isinstance(cert, CertificateEntry) else cert
                for cert in self.certifications
            ]
        # Convert EducationEntry objects to frontend format (map school_name→institution, start_date→start_year, end_date→end_year)
        if self.education:
            data["education"] = [
                edu.model_dump() if isinstance(edu, EducationEntry) else edu
                for edu in self.education
            ]
        return data


class StoredResume(BaseModel):
    resume_id: UUID
    template_id: str
    data: ResumeData


class ParsedResumeResponse(BaseModel):
    resume_id: UUID
    template_id: str
    data: ResumeData
    
    def model_dump(self, **kwargs):
        """Ensure education data is normalized when serializing response.
        
        This is CRITICAL: FastAPI calls this method when serializing the response.
        We must normalize education entries here to ensure frontend compatibility.
        Also ensures UUID is converted to string for JSON serialization.
        """
        # First, get the base serialized data
        # ResumeData.model_dump() should already normalize education, but we double-check here
        data = super().model_dump(**kwargs)
        
        # CRITICAL: Convert UUID to string for JSON serialization compatibility
        # This ensures JSONResponse can serialize the response without errors
        if isinstance(data.get("resume_id"), UUID):
            data["resume_id"] = str(data["resume_id"])
        
        # CRITICAL: Normalize education entries at the response level
        # This ensures the frontend always receives the correct field names
        if data.get("data") and isinstance(data["data"], dict) and data["data"].get("education"):
            normalized_education = []
            education_list = data["data"]["education"]
            
            for edu in education_list:
                if isinstance(edu, dict):
                    # Normalize dict entries (handles both already-normalized and raw formats)
                    normalized_education.append({
                        "institution": edu.get("institution") or edu.get("school_name") or "",
                        "location": edu.get("location") or "",
                        "degree": edu.get("degree") or "",
                        "start_year": edu.get("start_year") or edu.get("start_date") or "",
                        "end_year": edu.get("end_year") or edu.get("end_date") or "",
                        "description": edu.get("description") or "",
                    })
                else:
                    # If it's an EducationEntry object, use its model_dump
                    if hasattr(edu, 'model_dump'):
                        normalized_education.append(edu.model_dump())
                    else:
                        # Fallback: create normalized dict
                        normalized_education.append({
                            "institution": getattr(edu, 'school_name', None) or getattr(edu, 'institution', None) or "",
                            "location": getattr(edu, 'location', None) or "",
                            "degree": getattr(edu, 'degree', None) or "",
                            "start_year": getattr(edu, 'start_date', None) or getattr(edu, 'start_year', None) or "",
                            "end_year": getattr(edu, 'end_date', None) or getattr(edu, 'end_year', None) or "",
                            "description": getattr(edu, 'description', None) or "",
                        })
            
            data["data"]["education"] = normalized_education
        
        return data


class ChangeTemplateRequest(BaseModel):
    resume_id: UUID
    template_id: str


class GenerateSummaryRequest(BaseModel):
    job_description: str
    resume_data: Optional[ResumeData] = None


class GenerateSummaryResponse(BaseModel):
    summary: str


class ExtractProjectsRequest(BaseModel):
    """Request model for extracting projects from resume text."""
    resume_text: str = Field(..., description="The resume text to extract projects from")