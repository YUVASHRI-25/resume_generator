from __future__ import annotations

import re
from typing import Dict, List, Tuple


CERTIFICATE_HEADINGS = [
    "certificate", "certificates", "certification", "certifications",
    "courses", "trainings", "achievements", "skill certifications",
    "online courses", "licenses", "credentials"
]

SKILL_HEADINGS = [
    "technical skills", "technical skill", "skills", "skillset", "tech skills",
    "core skills", "key skills", "hard skills", "professional skills",
    "technical proficiencies", "technical proficiency", "technical expertise",
    "software skills", "tools & technologies", "tools and technologies",
    "technologies", "tech stack", "technical toolkit", "programming skills",
    "programming languages", "programming language",
    "it skills", "computer skills", "domain skills", "specialized skills",
    "primary skills", "relevant skills", "development skills",
    "technical competencies", "skill highlights", "skills highlights",
    "languages", "language", "Languages", "Language",
    "tools", "tool", "technical tools", "software tools", "developer tools",
]

SUMMARY_HEADINGS = [
    "summary",
    "professional summary",
    "career summary",
    "profile",
    "about me",
    "about",
    "objective",
    "career objective",
    "professional objective",
    "personal statement",
    "overview",
    "executive summary"
]

EDUCATION_HEADINGS = [
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

EXPERIENCE_HEADINGS = [
    "experience",
    "work experience",
    "professional experience",
    "employment",
    "employment history",
    "work history",
    "career history",
    "job experience",
    "industry experience",
    # Internship-specific
    "internship",
    "internships",
    "internship experience",
    "industrial training",
    "training",
    "apprenticeship",
    "practical experience",
    "hands-on experience"
]

PROJECT_HEADINGS = [
    "projects",
    "project",
    "personal projects",
    "side projects",
    "portfolio projects",
    "key projects",
    "notable projects",
    "selected projects",
    "project experience",
    "project work"
]

ACHIEVEMENT_HEADINGS = [
    "achievements",
    "achievement",
    "awards",
    "award",
    "honors",
    "honor",
    "accomplishments",
    "accomplishment",
    "recognition",
    "recognitions",
    "awards & achievements",
    "honors & awards"
]

SECTION_HEADERS = {
    "summary": SUMMARY_HEADINGS,
    "experience": EXPERIENCE_HEADINGS,
    "education": EDUCATION_HEADINGS,
    "skills": SKILL_HEADINGS,
    "certifications": CERTIFICATE_HEADINGS,
    "projects": PROJECT_HEADINGS,
    "achievements": ACHIEVEMENT_HEADINGS,
}


def extract_skills_from_text(text: str, skill_headers: List[str]) -> List[str]:
    """Extract skills from resume text using provided section headers.
    
    Args:
        text: The resume text to extract skills from
        skill_headers: List of regex patterns to identify skill sections
        
    Returns:
        List of extracted skills
    """
    import re
    from typing import List, Set
    
    if not text or not skill_headers:
        return []
    
    # Normalize text for case-insensitive matching
    normalized_text = text.lower()
    skills = set()
    
    # Try to find skill sections using provided headers
    for header_pattern in skill_headers:
        # Look for section headers that match the pattern
        # This handles different formats like "Skills:", "TECHNICAL SKILLS", etc.
        pattern = fr'(?:^|\n)\s*({header_pattern})\s*[\-:]*\s*\n(.*?)(?=\n\s*\n|\n\s*[A-Z][^\n]*:|\Z)'
        
        for match in re.finditer(pattern, normalized_text, re.IGNORECASE | re.DOTALL):
            section_content = match.group(2).strip()
            if section_content:
                # Clean and split the content into individual skills
                # Remove bullet points, numbers, and other common formatting
                cleaned = re.sub(r'[•\-*]\s*', '', section_content)  # Remove bullet points
                cleaned = re.sub(r'\d+[.)]\s*', '', cleaned)  # Remove numbered lists
                
                # Split by common delimiters and clean up
                for line in cleaned.split('\n'):
                    line = line.strip()
                    if not line:
                        continue
                        
                    # Handle comma/semicolon/pipe separated skills
                    for skill in re.split(r'[,;|]', line):
                        skill = skill.strip()
                        if skill and len(skill) > 1:  # Skip empty or single-character "skills"
                            skills.add(skill)
    
    # Also look for skills mentioned in other contexts
    # This is a simple approach - in a real implementation, you might want to use NER or a skills database
    common_skills = [
        'python', 'javascript', 'java', 'c++', 'c#', 'ruby', 'php', 'swift', 'kotlin', 'go', 'rust',
        'django', 'flask', 'react', 'angular', 'vue', 'node.js', 'spring', 'laravel', 'rails',
        'sql', 'mongodb', 'postgresql', 'mysql', 'oracle', 'sql server', 'sqlite',
        'docker', 'kubernetes', 'aws', 'azure', 'google cloud', 'git', 'jenkins', 'ansible',
        'machine learning', 'ai', 'data science', 'big data', 'deep learning', 'nlp', 'computer vision'
    ]
    
    # Check for these skills in the text (case insensitive)
    for skill in common_skills:
        if re.search(r'\b' + re.escape(skill) + r'\b', normalized_text, re.IGNORECASE):
            skills.add(skill)
    
    return sorted(list(skills), key=lambda x: x.lower())


def detect_sections(text: str) -> Dict[str, str]:
    """Split resume text into logical sections based on headings.

    Works even if:
    - Sections appear in a different order.
    - Headings contain extra words (e.g. \"Professional Experience\").
    - Some sections are missing.
    
    Returns a dict with section keys and their content. Empty sections are returned as empty strings.
    """

    lines = text.splitlines()
    sections: Dict[str, str] = {k: "" for k in SECTION_HEADERS.keys()}

    # For each line, see if it looks like a section header
    header_spans: List[Tuple[str, int]] = []  # (section_key, line_index)
    for i, line in enumerate(lines):
        normalized = line.strip().lower()
        if not normalized:
            continue

        for key, variants in SECTION_HEADERS.items():
            for variant in variants:
                v_norm = variant.lower().strip()
                # Treat a line as a header if it matches the heading (case-insensitive)
                # Check for exact match, starts with, ends with, or contains the variant
                # Also check if the line contains the variant as a whole word
                if (normalized == v_norm or 
                    normalized.startswith(v_norm + " ") or 
                    normalized.endswith(" " + v_norm) or
                    f" {v_norm} " in f" {normalized} " or
                    normalized.startswith(v_norm + ":") or
                    normalized.startswith(v_norm + "-")):
                    # Avoid duplicates
                    if (key, i) not in header_spans:
                        header_spans.append((key, i))
                    break

    if not header_spans:
        # No explicit headers found
        return sections

    # Sort by appearance in the document
    header_spans.sort(key=lambda x: x[1])

    # Slice between successive headers and merge sections with the same key
    for idx, (key, line_idx) in enumerate(header_spans):
        start_line = line_idx + 1  # content starts after header line
        end_line = header_spans[idx + 1][1] if idx + 1 < len(header_spans) else len(lines)
        body = "\n".join(lines[start_line:end_line]).strip()
        
        # Merge content if section key already exists (e.g., "Experience" and "Internships" both map to "experience")
        if sections[key]:
            sections[key] = sections[key] + "\n\n" + body
        else:
            sections[key] = body

    return sections
