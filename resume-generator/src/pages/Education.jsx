import { useState, useEffect } from 'react'
import ResumeBuilderLayout from './ResumeBuilderLayout'
import { useResume } from '../context/ResumeContext'

const emptyEducation = () => ({
  institution: '',
  location: '',
  degree: '',
  start_year: '',
  end_year: '',
  description: '',
})

const Education = () => {
  const { resumeData, updateEducation } = useResume()
  const [educations, setEducations] = useState(
    resumeData.education && resumeData.education.length > 0
      ? resumeData.education.map((edu) => ({
          institution: edu.institution || '',
          location: edu.location || '',
          degree: edu.degree || '',
          start_year: edu.start_year || '',
          end_year: edu.end_year || '',
          description: edu.description || '',
        }))
      : [emptyEducation()]
  )

  // Update local state when resumeData changes (from backend parsing)
  useEffect(() => {
    if (resumeData.education && resumeData.education.length > 0) {
      setEducations(
        resumeData.education.map((edu) => ({
          institution: edu.institution || '',
          location: edu.location || '',
          degree: edu.degree || '',
          start_year: edu.start_year || '',
          end_year: edu.end_year || '',
          description: edu.description || '',
        }))
      )
    }
  }, [resumeData.education])

  const handleChange = (index, field, value) => {
    const updated = educations.map((edu, i) =>
      i === index ? { ...edu, [field]: value } : edu
    )
    setEducations(updated)
    updateEducation(updated)
  }

  const handleAdd = () => {
    const updated = [...educations, emptyEducation()]
    setEducations(updated)
    updateEducation(updated)
  }

  const handleRemove = (index) => {
    const updated = educations.filter((_, i) => i !== index)
    setEducations(updated.length > 0 ? updated : [emptyEducation()])
    updateEducation(updated.length > 0 ? updated : [emptyEducation()])
  }

  return (
    <ResumeBuilderLayout>
      <h1 className="text-2xl font-bold text-gray-900 mb-2">Education</h1>
      <p className="text-gray-600 mb-8">
        Add your education details – even if you haven&apos;t graduated yet.
      </p>

      <div className="space-y-6">
        {educations.map((edu, index) => (
          <div
            key={index}
            className="border border-gray-200 rounded-xl p-5 bg-gray-50 relative"
          >
            {educations.length > 1 && (
              <button
                type="button"
                className="absolute top-3 right-3 text-xs text-gray-400 hover:text-red-500"
                onClick={() => handleRemove(index)}
              >
                Remove
              </button>
            )}

            <div className="grid md:grid-cols-2 gap-6 mb-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  School name
                </label>
                <input
                  type="text"
                  className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g., MIT, Harvard University"
                  value={edu.institution}
                  onChange={(e) =>
                    handleChange(index, 'institution', e.target.value)
                  }
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Location
                </label>
                <input
                  type="text"
                  className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g., Boston, MA"
                  value={edu.location}
                  onChange={(e) =>
                    handleChange(index, 'location', e.target.value)
                  }
                />
              </div>
            </div>

            <div className="grid md:grid-cols-2 gap-6 mb-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Degree
                </label>
                <input
                  type="text"
                  className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="BA in Finance and Banking"
                  value={edu.degree}
                  onChange={(e) =>
                    handleChange(index, 'degree', e.target.value)
                  }
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Start date
                  </label>
                  <input
                    type="text"
                    className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="YYYY"
                    value={edu.start_year}
                    onChange={(e) =>
                      handleChange(index, 'start_year', e.target.value)
                    }
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    End date
                  </label>
                  <input
                    type="text"
                    className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="YYYY"
                    value={edu.end_year}
                    onChange={(e) =>
                      handleChange(index, 'end_year', e.target.value)
                    }
                  />
                </div>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Description
              </label>
              <textarea
                rows={3}
                className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="e.g., Graduated with honors, Dean&apos;s List (2022)"
                value={edu.description}
                onChange={(e) =>
                  handleChange(index, 'description', e.target.value)
                }
              />
            </div>
          </div>
        ))}

        <button
          type="button"
          className="text-sm font-medium text-blue-600 hover:text-blue-700"
          onClick={handleAdd}
        >
          + Add education
        </button>
      </div>
    </ResumeBuilderLayout>
  )
}

export default Education
