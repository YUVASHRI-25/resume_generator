from __future__ import annotations

import json
import os
import re
from typing import Optional, List

from dotenv import load_dotenv
from openai import OpenAI

from ..models import CertificateEntry

# Load environment variables
load_dotenv()

# Initialize OpenRouter client
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY not found in environment variables")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)


def _normalize_text(text: str) -> str:
    """Normalize and clean extracted text while preserving meaning."""
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    # Fix common OCR errors
    text = text.replace('|', 'I').replace('0', 'O')  # Common OCR mistakes
    # Normalize line breaks
    text = re.sub(r'\n\s*\n', '\n', text)
    return text.strip()


def _normalize_date(date_str: Optional[str]) -> Optional[str]:
    """Normalize date to MM/YYYY format when possible."""
    if not date_str:
        return None
    
    date_str = str(date_str).strip()
    
    # Remove common prefixes/suffixes
    date_str = re.sub(r'^(issued|completed|earned|obtained|received|date[:]?)\s*:?\s*', '', date_str, flags=re.IGNORECASE)
    date_str = date_str.strip()
    
    # Format: MM/YYYY or M/YYYY
    mm_yyyy_match = re.match(r'^(\d{1,2})[/-](\d{4})$', date_str)
    if mm_yyyy_match:
        month = mm_yyyy_match.group(1).zfill(2)
        year = mm_yyyy_match.group(2)
        # Validate month
        if 1 <= int(month) <= 12:
            return f"{month}/{year}"
    
    # Format: YYYY-MM (ISO format)
    iso_match = re.match(r'^(\d{4})[-/](\d{1,2})$', date_str)
    if iso_match:
        year = iso_match.group(1)
        month = iso_match.group(2).zfill(2)
        if 1 <= int(month) <= 12:
            return f"{month}/{year}"
    
    # Format: Month YYYY or MMM YYYY (full or abbreviated)
    month_names = {
        'january': '01', 'february': '02', 'march': '03', 'april': '04',
        'may': '05', 'june': '06', 'july': '07', 'august': '08',
        'september': '09', 'october': '10', 'november': '11', 'december': '12',
        'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04',
        'may': '05', 'jun': '06', 'jul': '07', 'aug': '08',
        'sep': '09', 'sept': '09', 'oct': '10', 'nov': '11', 'dec': '12'
    }
    
    date_lower = date_str.lower()
    for month_name, month_num in month_names.items():
        # Check if month name appears in the date string
        if month_name in date_lower:
            # Extract year (4 digits starting with 19 or 20)
            year_match = re.search(r'\b(19|20)\d{2}\b', date_str)
            if year_match:
                return f"{month_num}/{year_match.group(0)}"
    
    # Format: DD/MM/YYYY or DD-MM-YYYY (extract month and year)
    ddmmyyyy_match = re.match(r'^\d{1,2}[/-](\d{1,2})[/-](\d{4})$', date_str)
    if ddmmyyyy_match:
        month = ddmmyyyy_match.group(1).zfill(2)
        year = ddmmyyyy_match.group(2)
        if 1 <= int(month) <= 12:
            return f"{month}/{year}"
    
    # Format: YYYY only
    year_match = re.search(r'\b(19|20)\d{2}\b', date_str)
    if year_match:
        year = year_match.group(0)
        # Default to January if only year is found
        return f"01/{year}"
    
    # If already in MM/YYYY format but with extra text, try to extract
    mm_yyyy_in_text = re.search(r'(\d{1,2})[/-](\d{4})', date_str)
    if mm_yyyy_in_text:
        month = mm_yyyy_in_text.group(1).zfill(2)
        year = mm_yyyy_in_text.group(2)
        if 1 <= int(month) <= 12:
            return f"{month}/{year}"
    
    # Return None if can't normalize (better than returning invalid date)
    return None


def _call_openrouter(prompt: str, model: str = "openai/gpt-4o-mini") -> str:
    """Call OpenRouter API with the given prompt."""
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": """You are an expert resume parser specialized in CERTIFICATION extraction.

TASK:
Extract ONLY certificate / certification / course completion details from the given resume text.

CRITICAL EXTRACTION RULES:

1. WHAT TO EXTRACT (ONLY these):
   ✓ Professional certifications (AWS, Azure, Google Cloud, etc.)
   ✓ Technical certifications (Microsoft, Oracle, Cisco, etc.)
   ✓ Course completion certificates (Coursera, Udemy, edX, NPTEL, etc.)
   ✓ Professional licenses (if explicitly mentioned as certificates)
   ✓ Online course certificates with completion proof
   ✓ Industry certifications (PMP, CFA, etc.)

2. WHAT NOT TO EXTRACT (STRICTLY EXCLUDE):
   ✗ Internships or training programs
   ✗ Projects or project descriptions
   ✗ Workshops (unless explicitly titled as "Certificate" or "Certification")
   ✗ Work experience entries
   ✗ Education degrees or academic qualifications
   ✗ Skills or technical proficiencies
   ✗ Awards or achievements (unless they are certifications)
   ✗ Volunteer work or extracurricular activities

3. EXTRACTION LOGIC:
   - Look for section headings: "Certificates", "Certifications", "Licenses & Certifications", "Professional Certifications", "Courses & Certifications", "Online Certifications", "Training & Certifications", "Additional Qualifications"
   - Extract from bullet points, tables, or paragraph formats
   - Handle OCR errors and normalize text
   - Preserve original certificate names exactly as written
   - Extract issuing organization from context (Coursera, Microsoft, Google, AWS, etc.)
   - Extract dates in any format and normalize to MM/YYYY
   - Extract credential IDs if explicitly mentioned (License numbers, Certificate IDs, etc.)
   - Extract URLs if verification links are provided

4. DATE NORMALIZATION:
   - "January 2023" → "01/2023"
   - "Jan 2023" → "01/2023"
   - "2023" → "01/2023" (default to January)
   - "03/2023" → "03/2023"
   - "March 15, 2023" → "03/2023"
   - "2023-03" → "03/2023"

5. ORGANIZATION EXTRACTION:
   - Extract from context: "AWS Certified Solutions Architect" → organization: "AWS"
   - Extract from platform: "Coursera - Machine Learning" → organization: "Coursera"
   - Extract from issuer: "Issued by Microsoft" → organization: "Microsoft"
   - If not clear, leave as null

6. VALIDATION:
   - certificate_name is REQUIRED (cannot be null)
   - If certificate_name is missing, skip the entry
   - All other fields can be null if not found
   - Return empty array [] if no valid certificates found

Return ONLY valid JSON (no markdown, no explanations, no comments).""",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
            max_tokens=3000,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        raise ValueError(f"Error calling OpenRouter API: {str(e)}")


def _extract_json_from_response(response: str) -> dict:
    """Extract JSON from the API response, handling markdown code blocks."""
    # Remove markdown code blocks if present
    response = response.strip()
    if response.startswith("```"):
        # Extract content between code blocks
        parts = response.split("```")
        if len(parts) >= 3:
            response = parts[1]
            # Remove language identifier if present
            if "\n" in response:
                response = response.split("\n", 1)[1]
    
    # Remove any leading/trailing non-JSON text
    response = response.strip()
    
    try:
        return json.loads(response)
    except json.JSONDecodeError as e:
        # Try to find JSON object in the response
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except:
                pass
        raise ValueError(f"Failed to parse JSON from response: {str(e)}")


def extract_certifications(resume_text: str) -> Optional[List[CertificateEntry]]:
    """Extract certifications from resume text using OpenAI GPT-4o-mini.
    
    Returns a list of CertificateEntry objects with detailed information:
    - certificate_name: Name of the certification or course
    - issuing_organization: Platform or authority (Coursera, Microsoft, Google, etc.)
    - date_of_completion: Completion or issue date (MM/YYYY)
    - credential_id: License / Credential ID if explicitly mentioned
    - credential_url: Verification or certificate link if explicitly mentioned
    
    Returns None if no certifications found or if extraction fails.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    if not resume_text or not resume_text.strip():
        logger.warning("Resume text is empty")
        return None
    
    normalized_text = _normalize_text(resume_text)
    
    # Limit text length to avoid token issues
    if len(normalized_text) > 4000:
        normalized_text = normalized_text[:4000] + "..."
    
    logger.info(f"Extracting certifications from {len(normalized_text)} characters")
    
    prompt = f"""Extract ONLY certificate / certification / course completion details from the resume text below.

RESUME TEXT:
{normalized_text}

EXTRACTION INSTRUCTIONS:

1. SCAN FOR CERTIFICATE SECTIONS:
   Look for headings like: "Certificates", "Certifications", "Licenses & Certifications", "Professional Certifications", "Courses & Certifications", "Online Certifications", "Training & Certifications", "Additional Qualifications"

2. EXTRACT EACH CERTIFICATE:
   For each certificate found, extract:
   
   a) certificate_name (REQUIRED):
      - Full name of the certification or course
      - Examples: "AWS Certified Solutions Architect", "Machine Learning by Stanford", "Microsoft Azure Fundamentals"
      - Preserve exact name as written
   
   b) issuing_organization (OPTIONAL):
      - Platform, company, or authority that issued the certificate
      - Examples: "AWS", "Coursera", "Microsoft", "Google", "Stanford University", "Udemy", "NPTEL"
      - Extract from context if not explicitly stated
      - If unclear, use null
   
   c) date_of_completion (OPTIONAL):
      - Completion date or issue date
      - Normalize to MM/YYYY format
      - Examples: "01/2023", "03/2022", "12/2021"
      - If only year is found, use "01/YYYY"
      - If not found, use null
   
   d) credential_id (OPTIONAL):
      - License number, certificate ID, or credential identifier
      - Examples: "AZ-900", "AWS-12345", "License #123456"
      - Only extract if explicitly mentioned
      - If not found, use null
   
   e) credential_url (OPTIONAL):
      - Verification link or certificate URL
      - Must be a valid URL (starts with http:// or https://)
      - Examples: "https://www.coursera.org/verify/ABC123", "https://credly.com/badges/xyz"
      - If not found, use null

3. EXCLUSION RULES:
   - DO NOT extract internships, projects, work experience, or education
   - DO NOT extract skills or technical proficiencies
   - DO NOT extract workshops unless explicitly titled as "Certificate"
   - Only extract items that are clearly certificates, certifications, licenses, or course completions

4. OUTPUT FORMAT:
   Return STRICT JSON only (no markdown, no explanations):
   {{
     "certificates": [
       {{
         "certificate_name": "AWS Certified Solutions Architect",
         "issuing_organization": "AWS",
         "date_of_completion": "03/2023",
         "credential_id": "AWS-12345",
         "credential_url": "https://www.credly.com/badges/abc123"
       }},
       {{
         "certificate_name": "Machine Learning",
         "issuing_organization": "Coursera",
         "date_of_completion": "01/2022",
         "credential_id": null,
         "credential_url": "https://www.coursera.org/verify/xyz789"
       }}
     ]
   }}

5. VALIDATION:
   - certificate_name is REQUIRED for each entry
   - If certificate_name is missing, skip that entry
   - All other fields can be null
   - If no certificates found, return: {{"certificates": []}}
   - Return ONLY valid JSON (no markdown code blocks, no explanations)

EXAMPLES OF VALID CERTIFICATES:
✓ "AWS Certified Solutions Architect - Associate" → certificate
✓ "Google Cloud Professional Cloud Architect" → certificate
✓ "Machine Learning by Stanford (Coursera)" → certificate
✓ "Microsoft Azure Fundamentals (AZ-900)" → certificate
✓ "PMP Certification" → certificate
✓ "Oracle Certified Java Developer" → certificate

EXAMPLES OF INVALID (DO NOT EXTRACT):
✗ "Software Developer Intern at Google" → internship
✗ "Built a web application using React" → project
✗ "Bachelor of Science in Computer Science" → education
✗ "5 years of experience in Python" → experience/skill

Return ONLY the JSON object with certificates array."""
    
    try:
        response = _call_openrouter(prompt, model="openai/gpt-4o-mini")
        logger.info(f"OpenRouter response received: {len(response)} characters")
        
        data = _extract_json_from_response(response)
        logger.info(f"Parsed JSON data type: {type(data)}")
        
        # Handle both formats: direct array or wrapped in "certificates" key
        certificates_list = None
        if isinstance(data, list):
            certificates_list = data
            logger.info(f"Found direct array with {len(certificates_list)} entries")
        elif isinstance(data, dict):
            if "certificates" in data:
                certificates_list = data["certificates"]
                logger.info(f"Found certificates key with value type: {type(certificates_list)}")
            else:
                logger.warning(f"Dict response missing 'certificates' key. Keys: {list(data.keys())}")
                # Try to find any array in the dict
                for key, value in data.items():
                    if isinstance(value, list):
                        certificates_list = value
                        logger.info(f"Using array from key '{key}' with {len(certificates_list)} entries")
                        break
        
        if certificates_list is None:
            logger.warning("No certificates list found in response")
            return None
        
        if not isinstance(certificates_list, list):
            logger.warning(f"Certificates list is not a list, got: {type(certificates_list)}")
            return None
        
        if len(certificates_list) == 0:
            logger.info("Certificates list is empty - no certifications found")
            return None
        
        logger.info(f"Processing {len(certificates_list)} certificate entries")
        
        entries = []
        for idx, item in enumerate(certificates_list):
            if not isinstance(item, dict):
                logger.warning(f"Entry {idx} is not a dict, skipping")
                continue
            
            # Extract and clean certificate_name (REQUIRED field)
            certificate_name = (
                item.get("certificate_name") or 
                item.get("name") or 
                item.get("certification") or 
                item.get("title") or
                item.get("certificate")
            )
            if certificate_name:
                certificate_name = str(certificate_name).strip()
                # Remove common prefixes/suffixes that might have been included
                certificate_name = re.sub(r'^(certificate|certification|cert):\s*', '', certificate_name, flags=re.IGNORECASE)
                certificate_name = certificate_name.strip()
                if not certificate_name or len(certificate_name) < 2:
                    certificate_name = None
            else:
                certificate_name = None
            
            # Skip entry if certificate_name is missing (required field)
            if not certificate_name:
                logger.warning(f"Skipping entry {idx+1}: missing required certificate_name")
                continue
            
            # Extract and clean issuing_organization
            issuing_organization = (
                item.get("issuing_organization") or 
                item.get("organization") or 
                item.get("issuer") or 
                item.get("platform") or
                item.get("issued_by") or
                item.get("provider")
            )
            if issuing_organization:
                issuing_organization = str(issuing_organization).strip()
                # Clean common prefixes
                issuing_organization = re.sub(r'^(issued by|from|by):\s*', '', issuing_organization, flags=re.IGNORECASE)
                issuing_organization = issuing_organization.strip()
                if not issuing_organization or len(issuing_organization) < 2:
                    issuing_organization = None
            else:
                issuing_organization = None
            
            # Extract and normalize date_of_completion
            date_of_completion = (
                item.get("date_of_completion") or 
                item.get("date") or 
                item.get("completion_date") or 
                item.get("issue_date") or
                item.get("issued_date") or
                item.get("earned_date") or
                item.get("completed")
            )
            if date_of_completion:
                date_of_completion = _normalize_date(str(date_of_completion).strip())
            else:
                date_of_completion = None
            
            # Extract credential_id
            credential_id = (
                item.get("credential_id") or 
                item.get("credential") or 
                item.get("id") or 
                item.get("license_id") or
                item.get("certificate_id") or
                item.get("credential_number") or
                item.get("license_number")
            )
            if credential_id:
                credential_id = str(credential_id).strip()
                # Remove common prefixes
                credential_id = re.sub(r'^(id|credential|license|certificate|number)[:\s#]*', '', credential_id, flags=re.IGNORECASE)
                credential_id = credential_id.strip()
                if not credential_id or len(credential_id) < 1:
                    credential_id = None
            else:
                credential_id = None
            
            # Extract credential_url (validate it's a URL)
            credential_url = (
                item.get("credential_url") or 
                item.get("url") or 
                item.get("link") or 
                item.get("verification_url") or
                item.get("certificate_url") or
                item.get("verification_link")
            )
            if credential_url:
                credential_url = str(credential_url).strip()
                # Validate it's a URL
                url_pattern = re.compile(
                    r'^https?://'  # http:// or https://
                    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
                    r'localhost|'  # localhost...
                    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
                    r'(?::\d+)?'  # optional port
                    r'(?:/?|[/?]\S+)$', re.IGNORECASE)
                
                if not url_pattern.match(credential_url):
                    # If it doesn't start with http, try to add https://
                    if not credential_url.startswith(('http://', 'https://')):
                        credential_url = f"https://{credential_url}"
                        if not url_pattern.match(credential_url):
                            credential_url = None
                    else:
                        credential_url = None
                
                if credential_url and len(credential_url) < 10:  # Too short to be a valid URL
                    credential_url = None
            else:
                credential_url = None
            
            # Only add entry if we have at least certificate_name
            if certificate_name:
                entries.append(CertificateEntry(
                    certificate_name=certificate_name,
                    issuing_organization=issuing_organization,
                    date_of_completion=date_of_completion,
                    credential_id=credential_id,
                    credential_url=credential_url,
                ))
                logger.info(f"Added certificate {idx+1}: {certificate_name} from {issuing_organization}")
            else:
                logger.warning(f"Skipping entry {idx+1}: missing certificate_name")
        
        if entries:
            logger.info(f"Successfully extracted {len(entries)} certifications")
            return entries
        else:
            logger.warning("No valid certificate entries created")
            return None
            
    except ValueError as e:
        logger.error(f"JSON parsing error: {str(e)}")
        logger.error(f"Response was: {response[:500] if 'response' in locals() else 'N/A'}")
        return None
    except Exception as e:
        logger.error(f"Error extracting certifications: {str(e)}", exc_info=True)
        return None

