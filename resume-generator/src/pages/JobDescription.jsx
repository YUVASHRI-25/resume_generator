import { useState, useEffect } from 'react'
import ResumeBuilderLayout from './ResumeBuilderLayout'
import { useResume } from '../context/ResumeContext'

const JobDescription = () => {
  const { resumeData } = useResume()
  const [jobDescription, setJobDescription] = useState('')
  const [generatedSummary, setGeneratedSummary] = useState('')
  const [isGenerating, setIsGenerating] = useState(false)
  const [error, setError] = useState(null)
  const [showSummary, setShowSummary] = useState(false)

  const generateSummary = async () => {
    if (!jobDescription.trim()) {
      setError('Please enter a job description first')
      return
    }

    setIsGenerating(true)
    setError(null)
    setShowSummary(false)

    try {
      const response = await fetch('http://127.0.0.1:8000/generate-summary', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          job_description: jobDescription,
          resume_data: resumeData,
        }),
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Failed to generate summary' }))
        throw new Error(errorData.detail || 'Failed to generate summary')
      }

      const result = await response.json()
      const summary = result.summary || ''
      
      setGeneratedSummary(summary)
      setShowSummary(true)
      
      // Also update the main summary in the context
      const event = new CustomEvent('generateSummary', { 
        detail: { 
          jobDescription,
          summary 
        } 
      })
      window.dispatchEvent(event)
      
    } catch (err) {
      setError(err.message || 'Failed to generate summary. Please try again.')
      console.error('Error generating summary:', err)
    } finally {
      setIsGenerating(false)
    }
  }

  return (
    <ResumeBuilderLayout>
      <h1 className="text-2xl font-bold text-gray-900 mb-2">Job Description</h1>
      <p className="text-gray-600 mb-6">
        Enter a job description to generate a tailored summary for your resume.
      </p>

      {/* Job Description Input */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Job Description
        </label>
        <textarea
          rows={8}
          className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Paste the job description here to generate a tailored summary..."
          value={jobDescription}
          onChange={(e) => {
            setJobDescription(e.target.value)
            setError(null)
          }}
        />
      </div>

      {/* Action Button */}
      <div className="mb-6">
        <button
          onClick={generateSummary}
          disabled={isGenerating || !jobDescription.trim()}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
        >
          {isGenerating ? (
            <>
              <svg className="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Generating Summary...
            </>
          ) : (
            'Generate Summary'
          )}
        </button>
      </div>

      {/* Error Message */}
      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
          {error}
        </div>
      )}

      {/* Generated Summary */}
      {showSummary && generatedSummary && (
        <div className="mt-6 p-4 bg-gray-50 border border-gray-200 rounded-lg">
          <h3 className="text-lg font-medium text-gray-900 mb-3">Generated Summary</h3>
          <div className="prose max-w-none text-gray-700">
            {generatedSummary.split('\n').map((paragraph, index) => (
              <p key={index} className="mb-3">{paragraph}</p>
            ))}
          </div>
          <div className="mt-4 text-sm text-gray-500">
            This summary has been automatically generated based on the job description. 
            You can copy it to the Summary tab or modify it as needed.
          </div>
        </div>
      )}
    </ResumeBuilderLayout>
  )
}

export default JobDescription
