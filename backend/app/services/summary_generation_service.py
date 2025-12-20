from __future__ import annotations

import os
import json
from typing import Optional

import httpx
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Hugging Face API configuration
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "")

# OpenRouter configuration (primary method since HF API has issues)
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if OPENROUTER_API_KEY:
    openrouter_client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
    )
else:
    openrouter_client = None


def _generate_template_summary(job_description: str, resume_data: Optional[dict] = None) -> str:
    """Fallback template-based summary generation when API is unavailable."""
    # Extract key information
    job_keywords = []
    job_lower = job_description.lower()
    
    # Common job-related keywords
    tech_keywords = ["java", "python", "javascript", "react", "node", "sql", "aws", "docker", "kubernetes"]
    for keyword in tech_keywords:
        if keyword in job_lower:
            job_keywords.append(keyword.title())
    
    # Build summary from resume data if available
    experience_text = ""
    skills_text = ""
    
    if resume_data:
        if resume_data.get("experience") and len(resume_data["experience"]) > 0:
            exp = resume_data["experience"][0]
            job_title = exp.get("job_title", "")
            if job_title:
                experience_text = f"Experienced {job_title.lower()}"
        
        if resume_data.get("skills"):
            skills = resume_data.get("skills", {})
            tech_skills = skills.get("technical", [])
            if tech_skills:
                skills_text = f" with expertise in {', '.join(tech_skills[:3])}"
    
    # Generate template summary
    if experience_text:
        summary = f"{experience_text}{skills_text}. "
    else:
        summary = "Experienced professional "
        if job_keywords:
            summary += f"with skills in {', '.join(job_keywords[:3])}. "
    
    summary += "Passionate about delivering high-quality solutions and continuously learning new technologies. "
    summary += "Strong problem-solving abilities and commitment to excellence."
    
    return summary


def _extract_generated_text(result) -> str:
    """Extract generated text from Hugging Face API response."""
    if isinstance(result, list) and len(result) > 0:
        return result[0].get("generated_text", "")
    elif isinstance(result, dict):
        return result.get("generated_text", result.get("summary", ""))
    elif isinstance(result, str):
        return result
    else:
        return str(result)


def _format_summary(generated_text: str, prompt: str) -> str:
    """Clean and format the generated summary text."""
    if not generated_text:
        return "Experienced professional with a strong background in relevant skills and expertise."
    
    # Remove prompt artifacts if present
    generated_text = generated_text.replace(prompt, "").strip()
    # Remove any leading/trailing quotes
    generated_text = generated_text.strip('"\'')
    # Take first 2-3 sentences
    sentences = [s.strip() for s in generated_text.split(". ") if s.strip()]
    if len(sentences) > 3:
        generated_text = ". ".join(sentences[:3]) + "."
    elif len(sentences) > 0:
        generated_text = ". ".join(sentences) + ("." if not generated_text.endswith(".") else "")
    else:
        generated_text = generated_text.strip()
    
    # Ensure minimum length
    if len(generated_text) < 20:
        generated_text = "Experienced professional with a strong background in relevant skills and expertise."
    
    return generated_text


async def generate_summary_from_job_description(
    job_description: str,
    resume_data: Optional[dict] = None
) -> str:
    """
    Generate a professional summary based on job description.
    Tries google/flan-t5-base via Hugging Face API first, then falls back to OpenRouter.
    
    Args:
        job_description: The job description text
        resume_data: Optional resume data (experience, skills, etc.) to tailor the summary
    
    Returns:
        Generated professional summary text
    """
    if not job_description or not job_description.strip():
        raise ValueError("Job description cannot be empty")
    
    # Build context from resume data if available
    context_parts = []
    if resume_data:
        if resume_data.get("experience") and len(resume_data["experience"]) > 0:
            exp = resume_data["experience"][0]  # Use most recent experience
            job_title = exp.get("job_title", "")
            employer = exp.get("employer", "")
            if job_title or employer:
                context_parts.append(f"Current role: {job_title} at {employer}" if job_title and employer else f"{job_title or employer}")
        
        if resume_data.get("skills"):
            skills = resume_data.get("skills", {})
            tech_skills = skills.get("technical", [])
            if tech_skills:
                context_parts.append(f"Key skills: {', '.join(tech_skills[:5])}")
    
    context = " | ".join(context_parts) if context_parts else ""
    
    # Create prompt for summary generation
    job_desc_limited = job_description[:800]
    
    # Try Hugging Face API first (for google/flan-t5-base)
    try:
        headers = {}
        if HUGGINGFACE_API_KEY:
            headers["Authorization"] = f"Bearer {HUGGINGFACE_API_KEY}"
        
        prompt = f"Write a professional resume summary for this job: {job_desc_limited}"
        if context:
            prompt += f" Background: {context}"
        prompt += " Summary:"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            api_url = "https://api-inference.huggingface.co/models/google/flan-t5-base"
            response = await client.post(
                api_url,
                headers=headers,
                json={"inputs": prompt},
            )
            
            if response.status_code == 200:
                result = response.json()
                generated_text = _extract_generated_text(result)
                if generated_text:
                    return _format_summary(generated_text, prompt)
            
            elif response.status_code == 503:
                # Model is loading, wait and retry once
                import asyncio
                await asyncio.sleep(5)
                response = await client.post(
                    api_url,
                    headers=headers,
                    json={"inputs": prompt},
                )
                if response.status_code == 200:
                    result = response.json()
                    generated_text = _extract_generated_text(result)
                    if generated_text:
                        return _format_summary(generated_text, prompt)
    except Exception:
        # Hugging Face API failed, try OpenRouter
        pass
    
    # Fallback to OpenRouter if available (uses GPT models which work better)
    if openrouter_client:
        try:
            # Create a better prompt for GPT models
            system_prompt = "You are a professional resume writer. Generate a concise 2-3 sentence professional summary that matches the job description and highlights relevant experience and skills."
            
            user_prompt = f"Job Description:\n{job_desc_limited}"
            if context:
                user_prompt += f"\n\nResume Context: {context}"
            user_prompt += "\n\nGenerate a professional resume summary:"
            
            response = openrouter_client.chat.completions.create(
                model="openai/gpt-3.5-turbo",  # Using GPT-3.5 as it's reliable and cost-effective
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=150,
            )
            generated_text = response.choices[0].message.content.strip()
            if generated_text:
                return generated_text
        except Exception as e:
            # OpenRouter failed, use template fallback
            pass
    
    # Final fallback: template-based summary
    return _generate_template_summary(job_description, resume_data)
