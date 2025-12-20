import { createContext, useContext, useState, useEffect } from 'react'

const ResumeContext = createContext()

export const useResume = () => {
  const context = useContext(ResumeContext)
  if (!context) {
    throw new Error('useResume must be used within ResumeProvider')
  }
  return context
}

const API_BASE_URL = 'http://127.0.0.1:8000'

export const ResumeProvider = ({ children }) => {
  const [resumeId, setResumeId] = useState(null)
  const [templateId, setTemplateId] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)

  // Resume data structure matching backend schema
  const [resumeData, setResumeData] = useState({
    contacts: {
      first_name: '',
      last_name: '',
      email: '',
      phone: '',
      location: '',
      desired_job_title: '',
      country: '',
      city: '',
      address: '',
      post_code: '',
      leetcode_url: '',
      github_url: '',
      linkedin_url: '',
    },
    experience: [],
    education: [],
    skills: [],
    languages: [],
    certifications: [],
    summary: '',
  })

  // Upload resume PDF and parse it
  const uploadResume = async (file, selectedTemplateId) => {
    setIsLoading(true)
    setError(null)

    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('template_id', selectedTemplateId || 'template_1')

      const response = await fetch(`${API_BASE_URL}/upload-resume`, {
        method: 'POST',
        body: formData,
        // Don't set Content-Type header - let browser set it with boundary
      })

      if (!response.ok) {
        let errorMessage = 'Failed to upload resume'
        try {
          const errorData = await response.json()
          errorMessage = errorData.detail || errorMessage
        } catch {
          // If response is not JSON, use status text
          errorMessage = `Server error: ${response.status} ${response.statusText}`
        }
        throw new Error(errorMessage)
      }

      const result = await response.json()
      
      // Ensure we have a proper resume ID and template ID
      const resumeId = result.resume_id || result.id || Date.now().toString()
      const templateId = result.template_id || 'template_1'
      
      // Ensure all required fields exist in the response
      const defaultResumeData = {
        contacts: {
          first_name: '',
          last_name: '',
          email: '',
          phone: '',
          location: '',
          desired_job_title: '',
          country: '',
          city: '',
          address: '',
          post_code: '',
          leetcode_url: '',
          github_url: '',
          linkedin_url: '',
          ...result.data?.contacts
        },
        experience: Array.isArray(result.data?.experience) ? result.data.experience : [],
        education: Array.isArray(result.data?.education) ? result.data.education : [],
        skills: Array.isArray(result.data?.skills) ? result.data.skills : [],
        languages: Array.isArray(result.data?.languages) ? result.data.languages : [],
        certifications: Array.isArray(result.data?.certifications) ? result.data.certifications : [],
        summary: result.data?.summary || ''
      }
      
      setResumeId(resumeId)
      setTemplateId(templateId)
      setResumeData(defaultResumeData)
      
      // Return the processed data
      return { resume_id: resumeId, template_id: templateId, data: defaultResumeData }

      return result
    } catch (err) {
      // Handle network errors specifically
      let errorMsg = err.message || 'Failed to upload resume. Please try again.'
      
      if (err.message === 'Failed to fetch' || err.name === 'TypeError') {
        errorMsg = 'Cannot connect to backend server. Please ensure the backend is running at http://127.0.0.1:8000'
      }
      
      setError(errorMsg)
      console.error('Upload error:', err)
      throw new Error(errorMsg)
    } finally {
      setIsLoading(false)
    }
  }

  // Change template without re-parsing
  const changeTemplate = async (newTemplateId) => {
    setIsLoading(true)
    setError(null)

    try {
      if (!resumeId) {
        // If no resume uploaded yet, just update template ID
        setTemplateId(newTemplateId)
        setIsLoading(false)
        return { template_id: newTemplateId, data: resumeData }
      }

      const response = await fetch(`${API_BASE_URL}/change-template`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          resume_id: resumeId,
          template_id: newTemplateId,
        }),
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Template change failed' }))
        throw new Error(errorData.detail || 'Failed to change template')
      }

      const result = await response.json()
      setTemplateId(result.template_id)
      // Data remains the same, only template changes

      return result
    } catch (err) {
      setError(err.message)
      throw err
    } finally {
      setIsLoading(false)
    }
  }

  // Update specific section of resume data
  const updateContacts = (contacts) => {
    setResumeData((prev) => ({ ...prev, contacts: { ...prev.contacts, ...contacts } }))
  }

  const updateExperience = (experience) => {
    setResumeData((prev) => ({ ...prev, experience }))
  }
  

  const updateEducation = (education) => {
    setResumeData((prev) => ({ ...prev, education }))
  }

  const updateSkills = (skills) => {
    setResumeData((prev) => ({ ...prev, skills }))
  }

  const updateLanguages = (languages) => {
    setResumeData((prev) => ({ ...prev, languages }))
  }

  const updateCertifications = (certifications) => {
    setResumeData((prev) => ({ ...prev, certifications }))
  }

  const updateSummary = (summary) => {
    setResumeData((prev) => ({ ...prev, summary }))
  }

  // Load existing resume from backend
  const loadResume = async (id) => {
    setIsLoading(true)
    setError(null)

    try {
      const response = await fetch(`${API_BASE_URL}/resume/${id}`)

      if (!response.ok) {
        throw new Error('Failed to load resume')
      }

      const result = await response.json()
      setResumeId(result.resume_id)
      setTemplateId(result.template_id)
      setResumeData(result.data)

      return result
    } catch (err) {
      setError(err.message)
      throw err
    } finally {
      setIsLoading(false)
    }
  }

  // Reset all data
  const resetResume = () => {
    setResumeId(null)
    setTemplateId(null)
    setResumeData({
      contacts: {
        first_name: '',
        last_name: '',
        email: '',
        phone: '',
        location: '',
        desired_job_title: '',
        country: '',
        city: '',
        address: '',
        post_code: '',
        leetcode_url: '',
        github_url: '',
        linkedin_url: '',
      },
      experience: [],
      education: [],
      skills: [],
      languages: [],
      certifications: [],
      projects: [],
      summary: '',
    })
  }

  const value = {
    resumeId,
    templateId,
    resumeData,
    isLoading,
    error,
    uploadResume,
    changeTemplate,
    loadResume,
    updateContacts,
    updateExperience,
    updateEducation,
    updateSkills,
    updateLanguages,
    updateCertifications,
    updateSummary,
    resetResume,
    setTemplateId, // For direct template selection
  }

  return <ResumeContext.Provider value={value}>{children}</ResumeContext.Provider>
}
