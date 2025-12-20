import { useState, useEffect } from 'react'
import ResumeBuilderLayout from './ResumeBuilderLayout'
import { useResume } from '../context/ResumeContext'

const Summary = () => {
  const { resumeData, updateSummary } = useResume()
  const [summary, setSummary] = useState(resumeData.summary || '')
  const [error, setError] = useState(null)

  // Update local state when resumeData changes (from backend parsing)
  useEffect(() => {
    if (resumeData.summary) {
      setSummary(resumeData.summary)
    }
  }, [resumeData.summary])

  const handleChange = (value) => {
    setSummary(value)
    updateSummary(value)
  }

  return (
    <ResumeBuilderLayout>
      <h1 className="text-2xl font-bold text-gray-900 mb-2">Summary</h1>
      <p className="text-gray-600 mb-6">
        Write a short professional summary that highlights your strengths.
      </p>

      {/* Error Message */}
      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
          {error}
        </div>
      )}

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Professional summary
        </label>
        <textarea
          rows={5}
          className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Motivated developer with a passion for building scalable web applications..."
          value={summary}
          onChange={(e) => handleChange(e.target.value)}
          maxLength={500}
        />
        <div className="text-right text-sm text-gray-500 mt-1">
          {summary.length}/500 characters
        </div>
      </div>
    </ResumeBuilderLayout>
  )
}

export default Summary
