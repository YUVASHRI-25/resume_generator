from __future__ import annotations

import json
import os
import re
from typing import Dict, Optional

from dotenv import load_dotenv
from openai import OpenAI

from ..models import (
    Contacts,
    ExperienceEntry,
    EducationEntry,
    Skills,
    ProjectEntry,
    ResumeData,
    CertificateEntry,
)
from . import section_detection_service, certification_extraction_service

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


# Regex patterns for validation
EMAIL_REGEX = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
PHONE_REGEX = re.compile(r'(\+?\d[\d\s().-]{7,}\d)')
POSTCODE_INDIA = re.compile(r'\b\d{6}\b')
POSTCODE_USA = re.compile(r'\b\d{5}\b')

# Common job title keywords to avoid confusing with names
JOB_TITLE_KEYWORDS = [
    'engineer', 'developer', 'manager', 'analyst', 'designer', 'specialist',
    'consultant', 'director', 'lead', 'senior', 'junior', 'associate',
    'architect', 'scientist', 'researcher', 'coordinator', 'executive'
]

# Common organization keywords to avoid confusing with names
ORG_KEYWORDS = [
    'university', 'college', 'institute', 'school', 'corporation', 'inc',
    'ltd', 'llc', 'company', 'technologies', 'solutions', 'systems'
]


def _normalize_text(text: str) -> str:
    """Normalize and clean extracted text while preserving structure (keep newlines).
    
    We must preserve newlines so section_detection_service can find headings.
    """
    # Normalize Windows/Mac line endings to \n
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    # Collapse excessive spaces but keep newlines
    text = re.sub(r'[ \t]+', ' ', text)
    # Collapse more than two consecutive newlines to exactly two
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Fix common OCR errors
    text = text.replace('|', 'I').replace('0', 'O')  # Common OCR mistakes
    return text.strip()


def _validate_email(email: Optional[str]) -> Optional[str]:
    """Validate email format."""
    if not email:
        return None
    email = email.strip()
    if EMAIL_REGEX.match(email):
        return email.lower()
    return None


def _validate_phone(phone: Optional[str]) -> Optional[str]:
    """Validate and clean phone number."""
    if not phone:
        return None
    # Remove spaces, dashes, brackets
    cleaned = re.sub(r'[\s\-()]', '', phone.strip())
    # Check if it's a valid phone number (at least 10 digits)
    if re.match(r'^\+?\d{10,15}$', cleaned):
        return cleaned
    return None


def _split_name(full_name: Optional[str]) -> tuple[Optional[str], Optional[str]]:
    """Intelligently split full name into first_name and last_name.
    
    Rules:
    - 2 words → First Name + Last Name
    - 3+ words → First Name + Remaining as Last Name
    """
    if not full_name:
        return None, None
    
    # Clean and normalize
    name = full_name.strip()
    words = name.split()
    
    if len(words) == 0:
        return None, None
    elif len(words) == 1:
        return words[0], None
    elif len(words) == 2:
        return words[0], words[1]
    else:
        # 3+ words: first word is first name, rest is last name
        return words[0], ' '.join(words[1:])


def _is_likely_name(text: str) -> bool:
    """Check if text is likely a person name (not job title or organization)."""
    text_lower = text.lower()
    
    # Check if it contains job title keywords
    for keyword in JOB_TITLE_KEYWORDS:
        if keyword in text_lower:
            return False
    
    # Check if it contains organization keywords
    for keyword in ORG_KEYWORDS:
        if keyword in text_lower:
            return False
    
    # Check if it's mostly alphabetic (names should be)
    words = text.split()
    if not words:
        return False
    
    # All words should be alphabetic (allow hyphens and apostrophes)
    for word in words:
        if not re.match(r'^[A-Za-z\-\']+$', word):
            return False
    
    return True


def _clean_phone(phone: str) -> str:
    """Clean phone number: remove spaces, dashes, brackets."""
    return re.sub(r'[\s\-()]', '', phone.strip())


def _call_openrouter(prompt: str, model: str = "openai/gpt-4.1-mini") -> str:
    """Call OpenRouter API with the given prompt."""
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": """You are an advanced Resume Parsing AI that extracts structured data from ANY type of resume:
- ATS-friendly text resumes
- Design resumes (tables, columns, icons)
- Scanned resumes (OCR output)
- Incomplete or unstructured resumes

RULES:
- Extract information strictly from the provided text
- Do NOT invent or infer missing information
- Use null for single values that are missing
- Use empty arrays [] for lists that are missing
- Never hallucinate data
- Normalize and clean text while preserving meaning
- Handle OCR noise and correct obvious errors logically
- Return ONLY valid JSON (no markdown, no explanations, no comments)

If OCR text contains noise, correct obvious errors logically.
If multiple resumes appear, extract only the primary one.""",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
            max_tokens=2000,  # Limit tokens to avoid 402 Payment Required error
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


def _extract_email_fallback(text: str) -> Optional[str]:
    """Fallback regex-based email extraction from full text (prioritizing header region)."""
    # First try header region (first 50 lines)
    header_lines = text.splitlines()[:50]
    header_text = "\n".join(header_lines)
    
    matches = EMAIL_REGEX.findall(header_text)
    if matches:
        # Prefer personal emails (gmail, outlook, yahoo, etc.)
        personal_domains = ['gmail', 'outlook', 'yahoo', 'hotmail', 'icloud', 'protonmail']
        for email in matches:
            email_lower = email.lower()
            if any(domain in email_lower for domain in personal_domains):
                return email.lower()
        # Return first match if no personal email found
        return matches[0].lower()
    
    # If not found in header, search full text
    all_matches = EMAIL_REGEX.findall(text)
    if all_matches:
        # Prefer personal emails
        personal_domains = ['gmail', 'outlook', 'yahoo', 'hotmail', 'icloud', 'protonmail']
        for email in all_matches:
            email_lower = email.lower()
            if any(domain in email_lower for domain in personal_domains):
                return email.lower()
        # Return first match if no personal email found
        return all_matches[0].lower()
    
    return None


def _extract_phone_fallback(text: str) -> Optional[str]:
    """Fallback regex-based phone extraction from full text (prioritizing header region)."""
    # First try header region (first 50 lines)
    header_lines = text.splitlines()[:50]
    header_text = "\n".join(header_lines)
    
    matches = PHONE_REGEX.findall(header_text)
    if matches:
        # Clean and validate first match
        phone = _clean_phone(matches[0])
        if _validate_phone(phone):
            return phone
    
    # If not found in header, search full text
    all_matches = PHONE_REGEX.findall(text)
    if all_matches:
        # Try each match until we find a valid phone
        for match in all_matches:
            phone = _clean_phone(match)
            if _validate_phone(phone):
                return phone
    
    return None


def _extract_urls_fallback(text: str) -> Dict[str, Optional[str]]:
    """Fallback regex-based URL extraction from full text.
    
    Returns a dict with github_url, leetcode_url, linkedin_url.
    """
    urls = {
        "github_url": None,
        "leetcode_url": None,
        "linkedin_url": None,
    }
    
    # Search full text for URLs
    github_pattern = r'https?://(?:www\.)?github\.com/[^\s\)]+'
    leetcode_pattern = r'https?://(?:www\.)?leetcode\.com/[^\s\)]+'
    linkedin_pattern = r'https?://(?:www\.)?linkedin\.com/[^\s\)]+'
    
    github_matches = re.findall(github_pattern, text, re.IGNORECASE)
    leetcode_matches = re.findall(leetcode_pattern, text, re.IGNORECASE)
    linkedin_matches = re.findall(linkedin_pattern, text, re.IGNORECASE)
    
    if github_matches:
        urls["github_url"] = github_matches[0]
    if leetcode_matches:
        urls["leetcode_url"] = leetcode_matches[0]
    if linkedin_matches:
        urls["linkedin_url"] = linkedin_matches[0]
    
    return urls


def _parse_personal_details(text: str) -> Contacts:
    """Extract personal details using OpenRouter with strict validation rules.
    
    Rules:
    1. Name: Take first line with capitalized words as full name
    2. Job Title: Extract from headline or summary line
    3. Email: Regex-based detection, prefer personal emails
    4. Phone: Accept various formats, clean output
    5. Location: Extract country, city, address, postcode separately
    6. Validation: If confidence < threshold, return null for that field
    """
    # Use first 50 lines for personal details (header region - increased for better coverage)
    # Also check first 2000 characters to catch contact info that might span multiple lines
    header_lines = text.splitlines()[:50]
    header_text = "\n".join(header_lines)
    
    # Also get first 2000 characters in case contact info is formatted differently
    first_chars = text[:2000]
    
    # Use the longer of the two for better extraction
    if len(first_chars) > len(header_text):
        header_text = first_chars
    
    # Limit header text to 3000 characters to avoid token limit issues (increased limit)
    if len(header_text) > 3000:
        header_text = header_text[:3000] + "..."
    
    # Extract email, phone, and URLs using regex as fallback/validation
    email_fallback = _extract_email_fallback(text)
    phone_fallback = _extract_phone_fallback(text)
    urls_fallback = _extract_urls_fallback(text)  # Extract URLs from full text
    
    prompt = f"""You are extracting personal contact information from a resume. Follow these STRICT rules:

RESUME TEXT (header region):
{header_text}

EXTRACTION RULES:

1️⃣ NAME EXTRACTION:
- Take the FIRST LINE with capitalized words as the full name
- Split intelligently:
  * 2 words → First Name + Last Name
  * 3+ words → First Name + Remaining as Last Name
- ❌ NEVER confuse job titles, college names, or company names as person name
- Only extract if text is clearly a person name (alphabetic, no job keywords)

2️⃣ DESIRED JOB TITLE:
- Extract from resume headline (below name) or summary line
- Look for patterns like "Software Engineer | Java Developer"
- If multiple roles exist, pick the most recent/strongest one
- Normalize titles: "S/W Engg" → "Software Engineer"
- Common formats: "Role | Technology", "Role at Company", standalone role

3️⃣ EMAIL (MANDATORY):
- Use regex: [a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}
- Prefer personal email (Gmail, Outlook, etc.)
- ❌ IGNORE portfolio emails inside project descriptions
- If no valid email found, use null

4️⃣ PHONE NUMBER:
- Accept formats: +91 XXXXX XXXXX, 10-digit Indian numbers, international formats
- Clean output: Remove spaces, dashes, brackets
- ❌ Do NOT pick years, roll numbers, IDs
- If no valid phone found, use null

5️⃣ LOCATION (Country, City, Address):
- Priority order: Explicit address section → Header line near name
- City: Single word or known city names
- Country: Infer if mentioned (India, USA, etc.), else keep blank
- ❌ Do NOT infer city from college/company location

6️⃣ ADDRESS:
- Extract ONLY if street/area keywords present (St, Rd, Ave, Nagar, Colony, Street, Road)
- Else: Leave address empty (ATS-friendly)
- Must contain address-like keywords

7️⃣ POSTCODE/ZIP CODE:
- India → 6 digits (must be near address/location text)
- USA → 5 digits (must be near address/location text)
- Must be numeric pattern near address/location

8️⃣ VALIDATION RULES:
- Email → Required field (if not found, use null)
- Phone → Optional but validated
- Name → Must be alphabetic (no numbers, no job titles)
- City/Country → Text only
- ❌ If confidence < threshold → leave field empty (don't hallucinate)

9️⃣ MULTIPLE SOURCES:
- If contact info appears in header, footer, sidebar → Merge + deduplicate
- Choose most complete version

🔟 SOCIAL LINKS:
- Extract LinkedIn URL (linkedin_url) even if shown as icons or short URLs
- Extract GitHub URL (github_url) even if shown as icons or short URLs  
- Extract LeetCode URL (leetcode_url) if present
- Prefer full URLs, but accept partial URLs if clearly identifiable
- Field names: linkedin_url, github_url, leetcode_url (not nested in links object)

Return JSON in this EXACT format (no extra keys, no markdown, no comments):
{{
  "full_name": "string or null",
  "desired_job_title": "string or null",
  "email": "string or null",
  "phone": "string or null",
  "location": "string or null",
  "country": "string or null",
  "city": "string or null",
  "address": "string or null",
  "post_code": "string or null",
  "linkedin_url": "string or null",
  "github_url": "string or null",
  "leetcode_url": "string or null"
}}

CRITICAL: 
- If you're not confident about a field (confidence < 0.6), use null
- Never guess personal data
- Only extract what is clearly present
- Return ONLY valid JSON"""
    
    try:
        try:
            response = _call_openrouter(prompt)
            data = _extract_json_from_response(response)
        except ValueError as api_error:
            # If API call fails (e.g., 402 Payment Required), use regex fallback
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"OpenRouter API call failed: {str(api_error)}. Using regex fallback extraction.")
            
            # Return Contacts with regex-extracted data only (including URLs)
            return Contacts(
                email=email_fallback,
                phone=phone_fallback,
                github_url=urls_fallback.get("github_url"),
                leetcode_url=urls_fallback.get("leetcode_url"),
                linkedin_url=urls_fallback.get("linkedin_url"),
            )
        
        # Extract and validate full_name
        full_name = data.get("full_name")
        if full_name:
            full_name = full_name.strip()
            # Try to extract name even if validation is lenient
            # Only reject if it's clearly not a name (contains numbers, job keywords, etc.)
            if _is_likely_name(full_name):
                first_name, last_name = _split_name(full_name)
            elif len(full_name.split()) <= 4 and not any(char.isdigit() for char in full_name):
                # If it looks like a name (no digits, reasonable length), try extracting anyway
                # This handles cases where validation might be too strict
                first_name, last_name = _split_name(full_name)
            else:
                first_name, last_name = None, None
        else:
            first_name, last_name = None, None
        
        # Validate email (mandatory field) - use AI result or fallback
        email_ai = _validate_email(data.get("email"))
        email = email_ai if email_ai else email_fallback
        
        # Validate and clean phone - use AI result or fallback
        phone_raw = data.get("phone")
        phone_ai = _validate_phone(phone_raw) if phone_raw else None
        phone = phone_ai if phone_ai else phone_fallback
        
        # Extract location components
        location = data.get("location")  # Combined location string
        country = data.get("country")
        city = data.get("city")
        address = data.get("address")
        post_code = data.get("post_code")  # Note: post_code not postcode
        
        # Validate postcode format
        if post_code:
            post_code_clean = post_code.strip()
            # Check if it matches India (6 digits) or USA (5 digits) format
            if not (POSTCODE_INDIA.match(post_code_clean) or POSTCODE_USA.match(post_code_clean)):
                post_code = None
        
        # Extract desired job title
        desired_job_title = data.get("desired_job_title")
        if desired_job_title:
            desired_job_title = desired_job_title.strip()
            # Normalize common abbreviations
            desired_job_title = desired_job_title.replace("S/W", "Software").replace("Engg", "Engineer")
        
        # Extract social links (flat structure for frontend)
        # Use AI-extracted URLs, fallback to regex-extracted URLs if not found
        linkedin_url = data.get("linkedin_url") or urls_fallback.get("linkedin_url")
        github_url = data.get("github_url") or urls_fallback.get("github_url")
        leetcode_url = data.get("leetcode_url") or urls_fallback.get("leetcode_url")
        
        # Build combined location string if not provided but city/country are
        if not location and (city or country):
            location_parts = [p for p in [city, country] if p]
            location = ", ".join(location_parts) if location_parts else None
        
        # Always return Contacts object, even if some fields are None
        # This ensures the contact tab gets populated with whatever we can extract
        contacts = Contacts(
            first_name=first_name,
            last_name=last_name,
            desired_job_title=desired_job_title,
            email=email,
            phone=phone,
            location=location,
            country=country,
            city=city,
            address=address,
            post_code=post_code,
            linkedin_url=linkedin_url,
            github_url=github_url,
            leetcode_url=leetcode_url,
        )
        
        # Always return the contacts object if we have any data
        # Even if AI extraction didn't find name, we might have email/phone
        if email or first_name or phone or desired_job_title or location or city or country:
            return contacts
        
        # If AI extraction failed completely, try fallback regex extraction
        # and return minimal Contacts object with whatever we can extract
        fallback_contacts = Contacts(
            email=email_fallback,
            phone=phone_fallback,
            github_url=urls_fallback.get("github_url"),
            leetcode_url=urls_fallback.get("leetcode_url"),
            linkedin_url=urls_fallback.get("linkedin_url"),
        )
        
        # Return fallback if we have at least email or phone
        if email_fallback or phone_fallback:
            return fallback_contacts
        
        # Return empty contacts object as last resort
        return Contacts()
    except Exception as e:
        # Log error but still return Contacts with fallback data
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error parsing personal details: {str(e)}", exc_info=True)
        
        # Return Contacts with fallback regex extraction (including URLs)
        fallback_contacts = Contacts(
            email=email_fallback,
            phone=phone_fallback,
            github_url=urls_fallback.get("github_url"),
            leetcode_url=urls_fallback.get("leetcode_url"),
            linkedin_url=urls_fallback.get("linkedin_url"),
        )
        
        # Return fallback if we have any data, otherwise return empty
        if email_fallback or phone_fallback:
            return fallback_contacts
        
        return Contacts()


def _parse_experience_section(section_text: str) -> Optional[list[ExperienceEntry]]:
    """Parse experience section using OpenRouter. Extracts ALL work experience entries including internships, traineeships, apprenticeships, and freelance work.
    
    Returns experience entries in reverse chronological order (most recent first).
    """
    import logging
    logger = logging.getLogger(__name__)
    
    if not section_text or not section_text.strip():
        logger.warning("Experience section text is empty")
        return None
    
    normalized_text = _normalize_text(section_text)
    
    # Limit text length to avoid token issues
    if len(normalized_text) > 3000:
        normalized_text = normalized_text[:3000] + "..."
    
    logger.info(f"Parsing experience section: {len(normalized_text)} characters")
    
    prompt = f"""Extract ALL work experience entries from this resume section. Include full-time, part-time, internships, traineeships, apprenticeships, and freelance work.

RESUME SECTION:
{normalized_text}

Return JSON in this EXACT format (no markdown, no explanations):
{{
  "experience": [
    {{
      "job_title": "string",
      "employer": "string",
      "location": "string or null",
      "start_date": "string or null",
      "end_date": "string or null",
      "description": "string"
    }}
  ]
}}

RULES:
1. Extract ALL experience entries (no limit)
2. Sort in reverse chronological order (most recent first)
3. Each role = separate object (do NOT merge)
4. If end_date is "Present", "Current", "Now" → set to null
5. Dates: normalize to readable format (MM/YYYY, Month Year, or Year)
6. Description: clean text, remove icons/emojis, merge into readable sentences
7. Missing fields → use null (do NOT guess)
8. If no experience found → return {{"experience": null}}

Return ONLY valid JSON."""
    
    try:
        response = _call_openrouter(prompt)
        logger.info(f"OpenRouter response received: {len(response)} characters")
        
        data = _extract_json_from_response(response)
        logger.info(f"Parsed JSON data type: {type(data)}")
        
        # Handle both formats: direct array or wrapped in "experience" key
        experience_list = None
        if isinstance(data, list):
            experience_list = data
            logger.info(f"Found direct array with {len(experience_list)} entries")
        elif isinstance(data, dict):
            if "experience" in data:
                experience_list = data["experience"]
                logger.info(f"Found experience key with value type: {type(experience_list)}")
            else:
                logger.warning(f"Dict response missing 'experience' key. Keys: {list(data.keys())}")
                # Try to find any array in the dict
                for key, value in data.items():
                    if isinstance(value, list):
                        experience_list = value
                        logger.info(f"Using array from key '{key}' with {len(experience_list)} entries")
                        break
        
        if experience_list is None:
            logger.warning("No experience list found in response")
            return None
        
        # If experience is null or empty, return None
        if experience_list is None:
            logger.info("Experience list is None")
            return None
        
        if not isinstance(experience_list, list):
            logger.warning(f"Experience list is not a list, got: {type(experience_list)}")
            return None
        
        if len(experience_list) == 0:
            logger.info("Experience list is empty")
            return None
        
        logger.info(f"Processing {len(experience_list)} experience entries")
        
        entries = []
        for idx, item in enumerate(experience_list):
            if not isinstance(item, dict):
                logger.warning(f"Entry {idx} is not a dict, skipping")
                continue
            
            # Extract and clean job_title
            job_title = item.get("job_title") or item.get("title") or item.get("position")
            if job_title:
                job_title = str(job_title).strip()
                if not job_title:
                    job_title = None
            
            # Extract and clean employer
            employer = item.get("employer") or item.get("company") or item.get("organization")
            if employer:
                employer = str(employer).strip()
                if not employer:
                    employer = None
            
            # Extract and clean location
            location = item.get("location") or item.get("city")
            if location:
                location = str(location).strip()
                if not location:
                    location = None
            
            # Extract and clean start_date
            start_date = item.get("start_date") or item.get("start")
            if start_date:
                start_date = str(start_date).strip()
                if not start_date:
                    start_date = None
            
            # Handle end_date: convert "Present", "Current", etc. to null
            end_date = item.get("end_date") or item.get("end")
            if end_date:
                end_date_str = str(end_date).strip()
                end_date_lower = end_date_str.lower()
                if end_date_lower in ["present", "current", "now", "ongoing", "till date", "till now", "till present"]:
                    end_date = None
                else:
                    end_date = end_date_str
            else:
                end_date = None
            
            # Extract and clean description
            description = item.get("description") or item.get("responsibilities") or item.get("duties")
            if description:
                # Clean description: remove excessive special characters but keep punctuation
                # Remove emojis and unusual symbols but keep standard punctuation
                description = re.sub(r'[^\w\s\.,;:!?\-()\[\]{}\n•\*]', '', str(description))
                # Normalize whitespace
                description = _normalize_text(description)
                # Preserve bullet points
                description = re.sub(r'\n\s*[•\*\-]\s*', '\n• ', description)
                description = description.strip()
                if not description:
                    description = None
            else:
                description = None
            
            # Only add entry if we have at least job_title or employer
            if job_title or employer:
                entries.append(ExperienceEntry(
                    job_title=job_title,
                    employer=employer,
                    location=location,
                    start_date=start_date,
                    end_date=end_date,
                    description=description,
                ))
                logger.info(f"Added entry {idx+1}: {job_title} at {employer}")
            else:
                logger.warning(f"Skipping entry {idx+1}: missing both job_title and employer")
        
        if entries:
            logger.info(f"Successfully parsed {len(entries)} experience entries")
            return entries
        else:
            logger.warning("No valid experience entries created")
            return None
            
    except ValueError as e:
        logger.error(f"JSON parsing error: {str(e)}")
        logger.error(f"Response was: {response[:500] if 'response' in locals() else 'N/A'}")
        return None
    except Exception as e:
        logger.error(f"Error parsing experience section: {str(e)}", exc_info=True)
        return None


def _parse_education_section(section_text: str) -> Optional[list[EducationEntry]]:
    """Parse education section using OpenAI GPT-4o-mini. Extracts ALL education details with strict formatting rules.
    
    Uses OpenAI GPT-4o-mini via OpenRouter for structured data extraction.
    Follows ATS resume parsing standards with strict validation.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    if not section_text or not section_text.strip():
        logger.warning("Education section text is empty")
        return None
    
    normalized_text = _normalize_text(section_text)
    
    # Limit text length to avoid token issues
    if len(normalized_text) > 4000:
        normalized_text = normalized_text[:4000] + "..."
    
    logger.info(f"Parsing education section: {len(normalized_text)} characters")
    
    prompt = f"""TASK:
Extract ALL EDUCATION details from the resume text below and return them in a structured JSON format.

CRITICAL: Extract ALL fields for EACH education entry. Do NOT skip any fields.

IMPORTANT EXTRACTION RULES (FOLLOW STRICTLY):

1. EDUCATION_HEADINGS = [
    "education",
    "academic",
    "academics",
    "academic background",
    "educational background",
    "educational qualifications",
    "qualification",
    "qualifications",
    "education & qualifications",
    "academic qualifications",
    "schooling",
    "education details",
    "education history"
]

2. Consider the following as EDUCATION:
   ✓ Schools, colleges, universities
   ✓ Degrees (Bachelor, Master, Diploma, PhD, Class X/XII, Higher Secondary, SSLC, HSC)
   ✓ Academic programs, branches, specializations
   ✓ High schools, secondary schools

3. DO NOT extract:
   ✗ Internships
   ✗ Projects
   ✗ Courses or certifications (unless part of a degree program)
   ✗ Work experience
   ✗ Training programs

4. If multiple education entries exist, extract ALL of them (no limit).

5. Normalize years to YYYY format when possible:
   - "2020-2024" → start_date: "2020", end_date: "2024"
   - "2020 to 2024" → start_date: "2020", end_date: "2024"
   - "2024" (if only one year) → end_date: "2024", start_date: "" (if not mentioned)
   - "Expected 2025" → end_date: "2025"
   - "Present" or "Current" → leave end_date empty string ""

6. Preserve original wording for degree names exactly as written.

FIELD EXTRACTION REQUIREMENTS (EXTRACT ALL FIELDS):

For EACH education entry, you MUST extract:

a) school_name (REQUIRED):
   - Institution / School / College / University name
   - Examples: "MIT", "Harvard Business School", "UCLA", "ABC School"
   - Extract from context even if not explicitly labeled
   - If institution name appears anywhere in the entry, extract it

b) location (OPTIONAL but extract if available):
   - City, State, Country if mentioned
   - Examples: "Boston, MA", "New York", "Delhi, India"
   - Look for location patterns: city names, state abbreviations, country names
   - Extract even if it appears after the institution name

c) degree (REQUIRED):
   - Degree name + specialization
   - Examples: "B.E in Computer Science Engineering", "MBA in Finance", "HSC", "B.Tech"
   - Preserve exact wording as written in resume
   - Include specialization if mentioned (e.g., "in Computer Science")

d) start_date (OPTIONAL but extract if available):
   - Start year in YYYY format only
   - Extract from date ranges like "2020-2024" or "2020 to 2024"
   - If only one year is mentioned, it's usually the end_date
   - If not found, return empty string ""

e) end_date (OPTIONAL but extract if available):
   - End year / Expected graduation year in YYYY format only
   - Extract from date ranges
   - Handle "Present", "Current", "Ongoing" → return empty string ""
   - If not found, return empty string ""

f) description (OPTIONAL but extract if available):
   - Honors, CGPA, percentage, achievements
   - Examples: "GPA: 3.8", "Graduated with honors", "Dean's List (2022)", "85%"
   - Extract any academic achievements or grades mentioned
   - If not found, return empty string ""

OUTPUT FORMAT (STRICT JSON ONLY — NO TEXT):
{{
  "education": [
    {{
      "school_name": "string (REQUIRED - cannot be empty)",
      "location": "string (empty string if not found)",
      "degree": "string (REQUIRED - cannot be empty)",
      "start_date": "YYYY (empty string if not found)",
      "end_date": "YYYY (empty string if not found)",
      "description": "string (empty string if not found)"
    }}
  ]
}}

VALIDATION RULES:
- JSON must be valid and parseable
- Do NOT include explanations
- Do NOT add extra keys
- If no education is found, return: {{"education": []}}
- Each educational institution must be a SEPARATE object
- Do NOT merge multiple institutions into one entry
- school_name and degree are REQUIRED fields (cannot be empty)
- All other fields can be empty strings if not found
- Dates must be in YYYY format only (4 digits) or empty string ""
- Extract ALL available information - do not skip fields

EXAMPLES OF COMPLETE EXTRACTION:

Example 1:
Input: "Bachelor of Technology in Computer Science, MIT, Boston, MA, 2020-2024, GPA: 3.8"
Output:
{{
  "school_name": "MIT",
  "location": "Boston, MA",
  "degree": "Bachelor of Technology in Computer Science",
  "start_date": "2020",
  "end_date": "2024",
  "description": "GPA: 3.8"
}}

Example 2:
Input: "B.E in Computer Science Engineering, UCLA, New York, 2018-2022"
Output:
{{
  "school_name": "UCLA",
  "location": "New York",
  "degree": "B.E in Computer Science Engineering",
  "start_date": "2018",
  "end_date": "2022",
  "description": ""
}}

Example 3:
Input: "HSC, ABC School, Delhi"
Output:
{{
  "school_name": "ABC School",
  "location": "Delhi",
  "degree": "HSC",
  "start_date": "",
  "end_date": "",
  "description": ""
}}

RESUME TEXT:
{normalized_text}

CRITICAL: Extract ALL fields for each education entry. Do NOT return entries with only degree field filled.
Return ONLY the JSON object with education array (no markdown, no explanations)."""
    
    try:
        response = _call_openrouter(prompt, model="openai/gpt-4o-mini")
        logger.info(f"OpenRouter response received: {len(response)} characters")
        
        data = _extract_json_from_response(response)
        logger.info(f"Parsed JSON data type: {type(data)}")
        
        # Handle both formats: direct array or wrapped in "education" key
        education_list = None
        if isinstance(data, list):
            education_list = data
            logger.info(f"Found direct array with {len(education_list)} entries")
        elif isinstance(data, dict):
            if "education" in data:
                education_list = data["education"]
                logger.info(f"Found education key with value type: {type(education_list)}")
            else:
                logger.warning(f"Dict response missing 'education' key. Keys: {list(data.keys())}")
                # Try to find any array in the dict
                for key, value in data.items():
                    if isinstance(value, list):
                        education_list = value
                        logger.info(f"Using array from key '{key}' with {len(education_list)} entries")
                        break
        
        if education_list is None:
            logger.warning("No education list found in response")
            logger.warning(f"Response data: {data}")
            logger.warning(f"Response preview: {response[:500] if 'response' in locals() else 'N/A'}")
            return None
        
        if not isinstance(education_list, list):
            logger.warning(f"Education list is not a list, got: {type(education_list)}")
            logger.warning(f"Education list value: {education_list}")
            return None
        
        if len(education_list) == 0:
            logger.info("Education list is empty - no education entries found in resume")
            return None
        
        logger.info(f"Processing {len(education_list)} education entries")
        
        entries = []
        for idx, item in enumerate(education_list):
            if not isinstance(item, dict):
                logger.warning(f"Entry {idx} is not a dict, skipping")
                continue
            
            # Initialize all variables at the top (defensive coding - prevents UnboundLocalError)
            school_name = None
            degree = None
            field_of_study = None
            location = ""
            start_date = ""
            end_date = ""
            description = ""
            
            # Extract and clean school_name (try multiple field names)
            school_name = (
                item.get("school_name") or 
                item.get("institution") or 
                item.get("university") or 
                item.get("college") or
                item.get("school") or
                item.get("institution_name")
            )
            if school_name:
                school_name = str(school_name).strip()
                # Remove common prefixes/suffixes
                school_name = re.sub(r'^(university|college|school|institute)[:\s]*', '', school_name, flags=re.IGNORECASE)
                school_name = school_name.strip()
                if not school_name or len(school_name) < 2:
                    school_name = None
            
            # Extract and clean degree (preserve original wording)
            degree = (
                item.get("degree") or 
                item.get("qualification") or
                item.get("program") or
                item.get("course")
            )
            if degree:
                degree = str(degree).strip()
                # Prevent garbage values like "Degree", "Qualification", "Program" (common LLM mistake)
                if degree.lower() in ["degree", "qualification", "program", "course", "education"]:
                    degree = None
                elif not degree:
                    degree = None
            else:
                degree = None
            
            # Auto-fill Indian school degrees if missing (safe inference, not hallucination)
            if not degree and school_name:
                school_name_lower = str(school_name).lower()
                if "matric" in school_name_lower or "sslc" in school_name_lower:
                    degree = "SSLC"
                elif "higher secondary" in school_name_lower or "hr.sec" in school_name_lower or "hsc" in school_name_lower:
                    degree = "HSC"
            
            # Extract field_of_study (may be in degree or separate)
            # If degree already contains specialization, don't duplicate
            field_of_study = item.get("field_of_study") or item.get("major") or item.get("specialization") or item.get("branch")
            if field_of_study:
                field_of_study = str(field_of_study).strip()
                # If degree already contains the field of study, don't duplicate
                if degree and field_of_study.lower() in degree.lower():
                    field_of_study = None
                elif not field_of_study:
                    field_of_study = None
            else:
                field_of_study = None
            
            # Extract and normalize start_date to YYYY format
            start_date = (
                item.get("start_date") or 
                item.get("start") or
                item.get("start_year") or
                item.get("from")
            )
            if start_date:
                start_date_str = str(start_date).strip()
                # Remove common prefixes
                start_date_str = re.sub(r'^(from|start|since)[:\s]*', '', start_date_str, flags=re.IGNORECASE)
                # Extract year from various formats (YYYY, MM/YYYY, Month YYYY, etc.)
                year_match = re.search(r'\b(19|20)\d{2}\b', start_date_str)
                if year_match:
                    start_date = year_match.group(0)
                else:
                    start_date = ""  # Empty string if no valid year found
            else:
                start_date = ""  # Empty string for missing dates
            
            # Extract and normalize end_date to YYYY format
            end_date = (
                item.get("end_date") or 
                item.get("end") or 
                item.get("graduation_date") or
                item.get("end_year") or
                item.get("to") or
                item.get("graduated") or
                item.get("completed")
            )
            if end_date:
                end_date_str = str(end_date).strip()
                # Handle "Present", "Current", "Ongoing"
                end_date_lower = end_date_str.lower()
                if end_date_lower in ["present", "current", "ongoing", "till date", "till now"]:
                    # Leave empty for current/ongoing education
                    end_date = ""
                else:
                    # Remove common prefixes
                    end_date_str = re.sub(r'^(to|end|until|graduated|completed)[:\s]*', '', end_date_str, flags=re.IGNORECASE)
                    # Extract year from various formats
                    year_match = re.search(r'\b(19|20)\d{2}\b', end_date_str)
                    if year_match:
                        end_date = year_match.group(0)
                    else:
                        end_date = ""  # Empty string if no valid year found
            else:
                end_date = ""  # Empty string for missing dates
            
            # Extract location (try multiple field names and variations)
            location = (
                item.get("location") or 
                item.get("city") or 
                item.get("address") or
                item.get("city_state") or
                item.get("location_city") or
                item.get("place") or
                item.get("city_state_country")
            )
            if location:
                location = str(location).strip()
                if not location or len(location) < 1:
                    location = ""  # Empty string if empty after stripping
            else:
                location = ""  # Empty string if not mentioned
            
            # Extract and clean description FIRST (before logging - prevents UnboundLocalError)
            description = item.get("description") or item.get("details") or item.get("achievements")
            if description:
                description = _normalize_text(str(description))
                description = description.strip()
                if not description:
                    description = ""  # Empty string if empty after processing
            else:
                description = ""  # Empty string if not present
            
            # NOW safe to log (all variables are defined)
            logger.info(
                f"Entry {idx+1} extracted - "
                f"school_name: {school_name}, "
                f"location: {location}, "
                f"degree: {degree}, "
                f"start_date: {start_date}, "
                f"end_date: {end_date}, "
                f"description: {description[:50] if description else ''}"
            )
            
            # Only add entry if we have at least school_name or degree
            if school_name or degree:
                # Convert empty strings to None for optional fields (except location, start_date, end_date, description which can be empty strings)
                entry = EducationEntry(
                    school_name=school_name if school_name else None,
                    degree=degree if degree else None,
                    field_of_study=field_of_study,
                    location=location if location else None,  # None if empty string
                    start_date=start_date if start_date else None,  # None if empty string
                    end_date=end_date if end_date else None,  # None if empty string
                    description=description if description else None,  # None if empty string
                )
                entries.append(entry)
                logger.info(f"Added entry {idx+1}: {degree} from {school_name} (location: {location or 'N/A'}, dates: {start_date or 'N/A'}-{end_date or 'N/A'})")
            else:
                logger.warning(f"Skipping entry {idx+1}: missing both school_name and degree. Item keys: {list(item.keys()) if isinstance(item, dict) else 'N/A'}")
        
        # Sort entries from most recent to oldest (by end_date, then start_date)
        if entries:
            def sort_key(entry):
                # Use end_date first, then start_date for sorting
                end_year = entry.end_date if entry.end_date and entry.end_date.isdigit() else "0"
                start_year = entry.start_date if entry.start_date and entry.start_date.isdigit() else "0"
                # Sort descending (most recent first)
                return (int(end_year) if end_year.isdigit() else 0, int(start_year) if start_year.isdigit() else 0)
            
            entries.sort(key=sort_key, reverse=True)
            logger.info(f"Successfully parsed {len(entries)} education entries (sorted from most recent to oldest)")
            return entries
        else:
            logger.warning("No valid education entries created")
            return None
            
    except ValueError as e:
        logger.error(f"JSON parsing error: {str(e)}")
        logger.error(f"Response was: {response[:500] if 'response' in locals() else 'N/A'}")
        return None
    except Exception as e:
        logger.error(f"Error parsing education section: {str(e)}", exc_info=True)
        return None


def _parse_skills_section(section_text: str) -> Optional[Skills]:
    """Parse skills section using OpenRouter. Categorizes into technical, soft, tools, languages."""
    if not section_text or not section_text.strip():
        return None
    
    normalized_text = _normalize_text(section_text)
    
    prompt = f"""Extract and categorize skills from the following resume section. Categorize into technical, soft, tools, and languages.

Section text:
{normalized_text}

Return JSON in this EXACT format:
{{
  "technical": [],
  "soft": [],
  "tools": [],
  "languages": []
}}

Categorization rules:
- technical: programming languages, frameworks, technologies, technical skills
- soft: communication, leadership, teamwork, problem-solving, interpersonal skills
- tools: software tools, development tools, platforms, IDEs
- languages: spoken languages (English, Spanish, etc.)

If a category has no skills, use empty array [].
Do NOT invent skills. Only extract what is explicitly present."""
    
    try:
        response = _call_openrouter(prompt)
        data = _extract_json_from_response(response)
        
        return Skills(
            technical=data.get("technical", []),
            soft=data.get("soft", []),
            tools=data.get("tools", []),
            languages=data.get("languages", []),
        )
    except Exception:
        return None


def _parse_projects_section(section_text: str) -> Optional[list[ProjectEntry]]:
    """Parse projects section using OpenRouter."""
    if not section_text or not section_text.strip():
        return None
    
    normalized_text = _normalize_text(section_text)
    
    prompt = f"""Extract project entries from the following resume section.

Section text:
{normalized_text}

Return JSON as an array (empty array [] if no projects found):
[
  {{
    "project_name": "string",
    "description": "string",
    "technologies": [],
    "link": "string or null"
  }}
]

Rules:
- Combine multiline descriptions into a single clean paragraph
- Extract technologies as an array of strings
- Extract links even if shown as icons or short URLs
- If no projects found, return empty array []
- Do NOT invent information"""
    
    try:
        response = _call_openrouter(prompt)
        data = _extract_json_from_response(response)
        
        if not isinstance(data, list):
            return None
        
        entries = []
        for item in data:
            description = item.get("description", "")
            if description:
                description = _normalize_text(description)
            
            entries.append(ProjectEntry(
                project_name=item.get("project_name"),
                description=description if description else None,
                technologies=item.get("technologies", []),
                link=item.get("link"),
            ))
        
        return entries if entries else None
    except Exception:
        return None


def _parse_achievements_section(section_text: str) -> Optional[list[str]]:
    """Parse achievements section. Returns array of strings."""
    if not section_text or not section_text.strip():
        return None
    
    normalized_text = _normalize_text(section_text)
    
    prompt = f"""Extract achievements from the following resume section. Return as a simple array of achievement descriptions.

Section text:
{normalized_text}

Return JSON as an array of strings (empty array [] if no achievements found):
["Achievement 1", "Achievement 2"]

Rules:
- Each achievement should be a clean, readable string
- Combine multiline achievements into single strings
- If no achievements found, return empty array []
- Do NOT invent achievements"""
    
    try:
        response = _call_openrouter(prompt)
        data = _extract_json_from_response(response)
        
        if not isinstance(data, list):
            return None
        
        # Normalize each achievement
        achievements = [_normalize_text(str(item)) for item in data if item and str(item).strip()]
        
        return achievements if achievements else None
    except Exception:
        return None


def _remove_header_content(text: str) -> str:
    """Remove header-like content from text (name, contact info, URLs that appear at the start).
    
    This helps ensure summary sections don't include header information.
    """
    if not text:
        return text
    
    lines = text.split('\n')
    cleaned_lines = []
    
    # Skip first few lines if they look like header content
    # Header typically contains: name, contact info, URLs, separators
    skip_count = 0
    for i, line in enumerate(lines[:5]):  # Check first 5 lines
        line_stripped = line.strip()
        if not line_stripped:
            continue
        
        # Check if line looks like header content
        has_url = bool(re.search(r'https?://|www\.|github\.com|leetcode\.com|linkedin\.com', line_stripped, re.IGNORECASE))
        has_email = bool(re.search(r'@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', line_stripped))
        has_phone = bool(re.search(r'\+?\d[\d\s().-]{7,}\d', line_stripped))
        has_separator = bool(re.search(r'[◇•|]', line_stripped))
        is_short_capitalized = len(line_stripped.split()) <= 4 and line_stripped.isupper()
        
        # If line has multiple header indicators, it's likely header content
        header_indicators = sum([has_url, has_email, has_phone, has_separator, is_short_capitalized])
        if header_indicators >= 2:
            skip_count = i + 1
        elif header_indicators == 1 and (has_url or has_email or has_phone):
            # Single URL/email/phone in first lines is likely header
            skip_count = i + 1
    
    # Return text without header lines
    return '\n'.join(lines[skip_count:]).strip()


def _remove_personal_info(text: str) -> str:
    """Remove personal information (phone numbers, emails, addresses, names, locations, URLs) from text.
    
    This function filters out:
    - Phone numbers (various formats)
    - Email addresses
    - URLs (GitHub, LeetCode, LinkedIn, portfolio, etc.)
    - Physical addresses
    - Common location patterns (city, state, country)
    - Names (capitalized words that look like names)
    - Special separator characters (◇, |, etc.)
    """
    if not text:
        return text
    
    # Remove phone numbers (various formats)
    # Matches: +91 1234567890, (123) 456-7890, 123-456-7890, etc.
    text = re.sub(r'\+?\d[\d\s().-]{7,}\d', '', text)
    
    # Remove email addresses
    text = re.sub(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '', text)
    
    # Remove URLs (GitHub, LeetCode, LinkedIn, portfolio, etc.)
    # Matches: http://, https://, www., and common domain patterns
    url_patterns = [
        r'https?://[^\s]+',  # http:// or https:// URLs
        r'www\.[^\s]+',  # www. URLs
        r'github\.com/[^\s]+',  # GitHub URLs (with or without protocol)
        r'leetcode\.com/[^\s]+',  # LeetCode URLs
        r'linkedin\.com/[^\s]+',  # LinkedIn URLs
        r'[a-zA-Z0-9-]+\.[a-zA-Z]{2,}/[^\s]+',  # Other domain URLs
    ]
    for pattern in url_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
    # Remove special separator characters commonly used in headers (◇, |, •, etc.)
    text = re.sub(r'[◇•|]\s*', ' ', text)  # Remove separator chars with optional space
    text = re.sub(r'\s+[◇•|]\s*', ' ', text)  # Remove separator chars with spaces around
    
    # Remove common address patterns (street, road, avenue, etc.)
    address_patterns = [
        r'\d+\s+[A-Za-z\s]+(?:Street|St|Road|Rd|Avenue|Ave|Lane|Ln|Drive|Dr|Boulevard|Blvd|Nagar|Colony|Area)',
        r'[A-Za-z\s]+(?:Street|St|Road|Rd|Avenue|Ave|Lane|Ln|Drive|Dr|Boulevard|Blvd|Nagar|Colony|Area)[\s,]+[A-Za-z\s]+',
    ]
    for pattern in address_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
    # Remove postcodes/zip codes (6 digits for India, 5 digits for USA) when near location keywords
    # Only remove if they appear near location-related words
    location_keywords = r'(?:near|at|in|from|to|address|location|city|state|country|postal|zip|pin)'
    text = re.sub(rf'{location_keywords}\s*\d{{5,6}}\b', '', text, flags=re.IGNORECASE)
    text = re.sub(rf'\b\d{{5,6}}\s*{location_keywords}', '', text, flags=re.IGNORECASE)
    
    # Remove common location patterns (City, State, Country format)
    # Pattern: "CITY STATENAME" or "CITY, STATENAME" or "CITY STATENAME COUNTRY"
    # Match common Indian states and cities
    indian_states = r'(?:TAMILNADU|KARNATAKA|MAHARASHTRA|DELHI|GUJARAT|RAJASTHAN|PUNJAB|WEST BENGAL|BIHAR|ODISHA|ANDHRA PRADESH|TELANGANA|KERALA|HARYANA|UTTAR PRADESH|MADHYA PRADESH|ASSAM|JHARKHAND|CHHATTISGARH|HIMACHAL PRADESH|UTTARAKHAND|TRIPURA|MEGHALAYA|MANIPUR|MIZORAM|NAGALAND|SIKKIM|ARUNACHAL PRADESH|GOA|PUDUCHERRY|DAMAN|DIU|DADRA|NAGAR HAVELI|LAKSHADWEEP|ANDAMAN|NICOBAR)'
    indian_cities = r'(?:COIMBATORE|CHENNAI|BANGALORE|MUMBAI|DELHI|HYDERABAD|PUNE|KOLKATA|AHMEDABAD|JAIPUR|LUCKNOW|KANPUR|NAGPUR|INDORE|THANE|BHOPAL|VISAKHAPATNAM|PATNA|VADODARA|GHAZIABAD|LUDHIANA|AGRA|NASHIK|FARIDABAD|MEERUT|RAJKOT|VARANASI|SRINAGAR|AMRITSAR|ALLAHABAD|RANCHI|GWALIOR|CHANDIGARH|JODHPUR|RAIPUR|KOTA|GUWAHATI|MYSORE|BHUBANESWAR|COCHIN|TRIVANDRUM|MADURAI|SURAT|JAMSHEDPUR|JABALPUR|ASANSOL|DHANBAD|AURANGABAD|JALANDHAR|GUNTUR|WARANGAL|BAREILLY|MORADABAD|DHARWAD|KARNAL|ROHTAK|BHAGALPUR|MUZAFFARPUR|BOKARO|GULBARGA|BELLARY|MUZAFFARNAGAR|BHIWANDI|SAHARANPUR|GORAKHPUR|BHIWANI|PANIPAT|BATHINDA|HISAR|SONIPAT|PANCHKULA|AMBALA|YAMUNANAGAR|KURUKSHETRA|KAITHAL|JIND|FATEHABAD|SIRSA|REWARI|MAHENDRAGARH|CHARKHI DADRI|JHAJJAR|PALWAL|MEWAT|GURGAON)'
    
    location_patterns = [
        rf'\b{indian_cities}\s+{indian_states}\s+INDIA\b',
        rf'\b{indian_cities}\s+{indian_states}\b',
        rf'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*,\s*{indian_states}\s+INDIA\b',
        rf'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*,\s*[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*,\s*INDIA\b',
    ]
    for pattern in location_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
    # Remove lines that are likely names (standalone capitalized words, 2-4 words)
    # But be careful not to remove job titles or common words
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        words = line.split()
        # Skip lines that are likely names (all words capitalized, 2-4 words, no common words)
        if 2 <= len(words) <= 4:
            if all(word and word[0].isupper() for word in words):
                # Check if it contains common non-name words or job-related words
                common_words = ['the', 'and', 'or', 'of', 'in', 'at', 'to', 'for', 'with', 'on', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should', 'could', 'may', 'might', 'must', 'can']
                job_words = ['engineer', 'developer', 'manager', 'analyst', 'designer', 'specialist', 'consultant', 'director', 'lead', 'senior', 'junior', 'associate', 'architect', 'scientist', 'researcher', 'coordinator', 'executive']
                line_lower = line.lower()
                if not any(word.lower() in common_words for word in words) and not any(job_word in line_lower for job_word in job_words):
                    # Likely a name line, skip it
                    continue
        cleaned_lines.append(line)
    text = '\n'.join(cleaned_lines)
    
    # Clean up multiple spaces and normalize
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\n\s*\n', '\n', text)
    
    return text.strip()


def _parse_summary_section(section_text: str) -> Optional[str]:
    """Parse summary section using OpenRouter. Extracts ONLY from sections with specific headings.
    
    ONLY extracts from these headings:
    - summary, professional summary, career summary
    - profile, about me, about
    - objective, career objective, professional objective
    - personal statement, overview, executive summary
    
    IMPORTANT: 
    - Filters out ALL personal information (phone numbers, emails, addresses, names, locations, URLs)
    - Only extracts professional summary/objective content
    """
    if not section_text or not section_text.strip():
        return None
    
    normalized_text = _normalize_text(section_text)
    
    # Remove header content first (name, contact info, URLs at the start)
    normalized_text = _remove_header_content(normalized_text)
    
    # Remove personal information before processing
    normalized_text = _remove_personal_info(normalized_text)
    
    # Limit text length to avoid token issues
    if len(normalized_text) > 1500:
        normalized_text = normalized_text[:1500] + "..."
    
    # Define the exact headings we accept
    valid_headings = [
        "summary", "professional summary", "career summary",
        "profile", "about me", "about",
        "objective", "career objective", "professional objective",
        "personal statement", "overview", "executive summary"
    ]
    
    prompt = f"""You are extracting a professional summary/objective from a resume section.

IMPORTANT: Only extract content from sections with these EXACT headings:
{', '.join(valid_headings)}

Section text:
{normalized_text}

Return JSON in this EXACT format:
{{
  "summary": "string or null"
}}

STRICT EXTRACTION RULES:
1. ONLY extract if the section has one of these headings: {', '.join(valid_headings)}
2. Extract ONLY the professional summary/objective content (career goals, skills, experience highlights, professional background)
3. Combine multiline text into a single clean paragraph
4. Remove excessive whitespace and normalize spacing
5. Preserve the meaning and professional content

CRITICAL EXCLUSIONS - Remove ALL of the following:
- Phone numbers (any format: +91, (123) 456-7890, etc.)
- Email addresses (any email format)
- URLs (GitHub, LeetCode, LinkedIn, portfolio, website links, any http:// or https://)
- Physical addresses (street, road, avenue, etc.)
- Location information (city, state, country, postal codes, zip codes)
- Personal names (first name, last name, full name, any person's name)
- Contact details (any contact information)
- Header information (anything that appears in the resume header)
- Special separator characters (◇, |, •, etc.)
- Any personal identifying information

VALIDATION:
- If the text contains only personal information/header content with no actual summary, return null
- If no valid summary content found after removing personal info, return null
- If the section doesn't match one of the valid headings, return null
- Do NOT invent or add content
- Return ONLY valid JSON (no markdown, no explanations, no comments)"""
    
    try:
        try:
            response = _call_openrouter(prompt)
            data = _extract_json_from_response(response)
            
            summary = data.get("summary")
            if summary:
                # Clean and normalize the summary text
                summary = _normalize_text(str(summary))
                # Remove personal information again as a safety measure
                summary = _remove_personal_info(summary)
                # Remove excessive newlines but preserve paragraph structure
                summary = re.sub(r'\n{3,}', '\n\n', summary)
                summary_cleaned = summary.strip() if summary.strip() else None
                if summary_cleaned:
                    return summary_cleaned
            
            # If API returned null or empty, return None (don't use fallback with personal info)
            return None
        except ValueError as api_error:
            # If API call fails (e.g., 402 Payment Required), log and return None
            # We don't want to return text that might contain personal info
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"OpenRouter API call failed for summary: {str(api_error)}. Returning None to avoid personal info leakage.")
            return None
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error parsing summary section: {str(e)}", exc_info=True)
        # Return None on error - don't risk returning personal info
        return None


def parse_resume(text: str) -> ResumeData:
    """High-level parsing pipeline that extracts structured resume data from ANY type of resume.
    
    Handles:
    - ATS-friendly text resumes
    - Design resumes (tables, columns, icons)
    - Scanned resumes (OCR output)
    - Incomplete or unstructured resumes
    
    Rules:
    - Only fill sections that exist in the resume
    - Return null for empty/missing sections
    - Use empty arrays [] for missing lists
    - Do not invent content
    - Normalize and clean text while preserving meaning
    """
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    try:
        # Normalize the input text first
        normalized_text = _normalize_text(text)
        
        if not normalized_text or len(normalized_text.strip()) < 10:
            logger.warning("Input text is too short or empty")
            return ResumeData(contacts=Contacts())
        
        logger.info(f"Parsing resume with {len(normalized_text)} characters")
        
        # Detect sections first
        sections = section_detection_service.detect_sections(normalized_text)
        logger.info(f"Detected sections: {list(sections.keys())}")
        # Log section lengths for debugging
        for section_key, section_content in sections.items():
            if section_content:
                logger.info(f"Section '{section_key}': {len(section_content)} characters")
            else:
                logger.info(f"Section '{section_key}': EMPTY")
        
        # Log summary section detection details
        summary_section = sections.get("summary", "")
        if summary_section:
            logger.info(f"Summary section detected: {len(summary_section)} characters")
        else:
            logger.info("No summary section detected by section detection")
        
        # Parse contacts (always attempt from header)
        # This is critical - always try to extract contact info
        logger.info("Extracting contacts...")
        contacts = _parse_personal_details(normalized_text)
        
        # Ensure we always have a Contacts object (even if empty)
        if contacts is None:
            logger.warning("Contacts extraction returned None, creating empty object")
            contacts = Contacts()
        
        # Log detailed contact extraction results
        logger.info(f"Contacts extracted: email={contacts.email is not None} ({contacts.email}), "
                   f"phone={contacts.phone is not None} ({contacts.phone}), "
                   f"first_name={contacts.first_name is not None} ({contacts.first_name}), "
                   f"last_name={contacts.last_name is not None} ({contacts.last_name}), "
                   f"job_title={contacts.desired_job_title is not None} ({contacts.desired_job_title}), "
                   f"location={contacts.location is not None} ({contacts.location}), "
                   f"city={contacts.city is not None} ({contacts.city}), "
                   f"country={contacts.country is not None} ({contacts.country})")
        
        # Parse experience (only if section exists)
        experience = None
        experience_section = sections.get("experience", "")
        if experience_section and experience_section.strip():
            logger.info(f"Experience section detected: {len(experience_section)} characters")
            logger.info(f"Experience section preview: {experience_section[:200]}...")
            experience = _parse_experience_section(experience_section)
            if experience:
                logger.info(f"Successfully parsed {len(experience)} experience entries")
            else:
                logger.warning("Experience parsing returned None or empty")
        else:
            logger.warning("No experience section detected or section is empty")
            # Fallback: try to find experience in the full text if section detection failed
            if "experience" in normalized_text.lower() or "work" in normalized_text.lower() or "employment" in normalized_text.lower():
                logger.info("Attempting fallback: parsing experience from full text")
                experience = _parse_experience_section(normalized_text)
                if experience:
                    logger.info(f"Fallback parsing succeeded: {len(experience)} entries")
        
        # Parse education (only if section exists)
        education = None
        education_section = sections.get("education", "")
        if education_section and education_section.strip():
            logger.info(f"Education section detected: {len(education_section)} characters")
            logger.info(f"Education section preview: {education_section[:200]}...")
            education = _parse_education_section(education_section)
            if education:
                logger.info(f"Successfully parsed {len(education)} education entries")
            else:
                logger.warning("Education parsing returned None or empty")
                # Fallback: try parsing from full text
                logger.info("Attempting fallback: parsing education from full text")
                education = _parse_education_section(normalized_text)
                if education:
                    logger.info(f"Fallback parsing succeeded: {len(education)} entries")
        else:
            logger.warning("No education section detected or section is empty")
            # Fallback: try to find education in the full text if section detection failed
            if "education" in normalized_text.lower() or "university" in normalized_text.lower() or "college" in normalized_text.lower() or "degree" in normalized_text.lower():
                logger.info("Attempting fallback: parsing education from full text")
                education = _parse_education_section(normalized_text)
                if education:
                    logger.info(f"Fallback parsing succeeded: {len(education)} entries")
        
        # Parse skills (only if section exists)
        skills = None
        if sections.get("skills") and sections["skills"].strip():
            skills = _parse_skills_section(sections["skills"])
        
        # Parse projects (only if section exists)
        projects = None
        if sections.get("projects") and sections["projects"].strip():
            logger.info(f"Projects section detected: {len(sections['projects'])} characters")
            projects = _parse_projects_section(sections["projects"])
            if projects:
                logger.info(f"Successfully parsed {len(projects)} projects")
            else:
                logger.warning("Project parsing returned None or empty")
        else:
            logger.warning("No projects section detected or section is empty")
            # Fallback: try to find projects in the full text if section detection failed
            if any(keyword in normalized_text.lower() for keyword in ["project", "portfolio", "github"]):
                logger.info("Attempting fallback: parsing projects from full text")
                projects = _parse_projects_section(normalized_text)
                if projects:
                    logger.info(f"Fallback parsing succeeded: {len(projects)} entries")
        
        # Parse certifications using detailed extraction service (only if section exists)
        certifications = None
        certifications_section = sections.get("certifications", "").strip()
        if certifications_section:
            logger.info(f"Certifications section detected: {len(certifications_section)} characters")
            certifications = certification_extraction_service.extract_certifications(certifications_section)
            if certifications:
                logger.info(f"Successfully extracted {len(certifications)} certifications")
            else:
                logger.warning("Certification extraction returned None or empty")
        else:
            # Fallback: try to extract from full text if section detection failed
            if any(keyword in normalized_text.lower() for keyword in ["certificate", "certification", "license", "credential"]):
                logger.info("Attempting fallback: extracting certifications from full text")
                certifications = certification_extraction_service.extract_certifications(normalized_text)
                if certifications:
                    logger.info(f"Fallback extraction succeeded: {len(certifications)} entries")
        
        # Parse achievements (only if section exists)
        achievements = None
        if sections.get("achievements") and sections["achievements"].strip():
            achievements = _parse_achievements_section(sections["achievements"])
        
        # Parse summary (ONLY from sections with SUMMARY_HEADINGS - no fallback)
        summary = None
        summary_section_text = sections.get("summary", "").strip()
        if summary_section_text:
            logger.info(f"Extracting summary from section ({len(summary_section_text)} chars)...")
            try:
                summary = _parse_summary_section(summary_section_text)
                logger.info(f"Summary extracted: {summary is not None}, length: {len(summary) if summary else 0}")
                if summary:
                    logger.info(f"Summary preview: {summary[:100]}...")
            except Exception as e:
                logger.error(f"Error extracting summary: {str(e)}", exc_info=True)
                # Only use cleaned section text if it's from a valid summary section
                # Remove all personal info as safety measure
                if summary_section_text:
                    summary = _normalize_text(summary_section_text)
                    summary = _remove_header_content(summary)
                    summary = _remove_personal_info(summary).strip()
                    # If after cleaning there's no meaningful content, set to None
                    if not summary or len(summary.strip()) < 10:
                        summary = None
                else:
                    summary = None
        else:
            logger.info("No summary section detected with valid SUMMARY_HEADINGS - skipping summary extraction")
            # No fallback - only extract from sections with valid headings
            summary = None
        
        # Always return ResumeData with at least contacts
        result = ResumeData(
            contacts=contacts,
            experience=experience,
            education=education,
            skills=skills,
            projects=projects,
            certifications=certifications,
            achievements=achievements,
            summary=summary,
        )
        
        logger.info(f"Resume parsing complete. Contacts: {contacts.email is not None or contacts.first_name is not None}")
        return result
        
    except Exception as e:
        logger.error(f"Error in parse_resume: {str(e)}", exc_info=True)
        # Always return ResumeData with at least empty contacts
        return ResumeData(contacts=Contacts())
