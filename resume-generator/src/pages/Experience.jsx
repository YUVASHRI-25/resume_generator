import { useState } from 'react'
import ResumeBuilderLayout from './ResumeBuilderLayout'

const emptyExperience = () => ({
  jobTitle: '',
  employer: '',
  location: '',
  startDate: '',
  endDate: '',
  description: '',
})

const Experience = () => {
  const [experiences, setExperiences] = useState([emptyExperience()])

  const handleChange = (index, field, value) => {
    setExperiences((prev) =>
      prev.map((exp, i) => (i === index ? { ...exp, [field]: value } : exp)),
    )
  }

  const handleAdd = () => {
    setExperiences((prev) => [...prev, emptyExperience()])
  }

  const handleRemove = (index) => {
    setExperiences((prev) => prev.filter((_, i) => i !== index))
  }

  return (
    <ResumeBuilderLayout>
      <h1 className="text-2xl font-bold text-gray-900 mb-2">Experience</h1>
      <p className="text-gray-600 mb-8">
        List your work experience starting with the most recent position first.
      </p>

      <div className="space-y-6">
        {experiences.map((exp, index) => (
          <div
            key={index}
            className="border border-gray-200 rounded-xl p-5 bg-gray-50 relative"
          >
            {experiences.length > 1 && (
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
                  Job title
                </label>
                <input
                  type="text"
                  className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Junior Accountant"
                  value={exp.jobTitle}
                  onChange={(e) =>
                    handleChange(index, 'jobTitle', e.target.value)
                  }
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Employer
                </label>
                <input
                  type="text"
                  className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Company name"
                  value={exp.employer}
                  onChange={(e) =>
                    handleChange(index, 'employer', e.target.value)
                  }
                />
              </div>
            </div>

            <div className="grid md:grid-cols-3 gap-6 mb-4">
              <div className="md:col-span-1">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Location
                </label>
                <input
                  type="text"
                  className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="San Francisco, CA, USA"
                  value={exp.location}
                  onChange={(e) =>
                    handleChange(index, 'location', e.target.value)
                  }
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Start date
                </label>
                <input
                  type="text"
                  className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="MM/YYYY"
                  value={exp.startDate}
                  onChange={(e) =>
                    handleChange(index, 'startDate', e.target.value)
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
                  placeholder="MM/YYYY"
                  value={exp.endDate}
                  onChange={(e) =>
                    handleChange(index, 'endDate', e.target.value)
                  }
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Description
              </label>
              <textarea
                rows={4}
                className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="• Helped with monthly financial reports and data entry&#10;• Watched over team budgets and reported issues&#10;• Entered 150+ invoices weekly using accounting software"
                value={exp.description}
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
          + Add work experience
        </button>
      </div>
    </ResumeBuilderLayout>
  )
}

export default Experience
