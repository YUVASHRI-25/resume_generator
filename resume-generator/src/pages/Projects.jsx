import { useState, useEffect } from 'react'
import ResumeBuilderLayout from './ResumeBuilderLayout'
import { useResume } from '../context/ResumeContext'

const emptyProject = () => ({
  projectTitle: '',
  yourRole: '',
  technologiesUsed: '',
  projectDuration: '',
  projectDescription: '',
})

const Projects = () => {
  const { resumeData, updateExperience } = useResume()
  const [projects, setProjects] = useState(
    resumeData.experience && resumeData.experience.length > 0
      ? resumeData.experience.map(exp => ({
          projectTitle: exp.title || exp.role || '',
          yourRole: exp.role || exp.position || '',
          technologiesUsed: Array.isArray(exp.technologies) 
            ? exp.technologies.join(', ')
            : (exp.technologies || ''),
          projectDuration: exp.duration || '',
          projectDescription: Array.isArray(exp.description) 
            ? exp.description.join('\n')
            : (exp.description || '')
        }))
      : [emptyProject()]
  )

  // Update local state when resumeData changes (from backend parsing)
  useEffect(() => {
    if (resumeData.experience && resumeData.experience.length > 0) {
      setProjects(
        resumeData.experience.map(exp => ({
          projectTitle: exp.title || exp.role || '',
          yourRole: exp.role || exp.position || '',
          technologiesUsed: Array.isArray(exp.technologies) 
            ? exp.technologies.join(', ')
            : (exp.technologies || ''),
          projectDuration: exp.duration || '',
          projectDescription: Array.isArray(exp.description) 
            ? exp.description.join('\n')
            : (exp.description || '')
        }))
      )
    }
  }, [resumeData.experience])

  const handleChange = (index, field, value) => {
    const updated = projects.map((proj, i) =>
      i === index ? { ...proj, [field]: value } : proj
    )
    setProjects(updated)
    
    // Convert to the expected format for the backend
    const experienceData = updated.map(proj => ({
      title: proj.projectTitle,
      role: proj.yourRole,
      technologies: proj.technologiesUsed.split(',').map(t => t.trim()).filter(Boolean),
      duration: proj.projectDuration,
      description: proj.projectDescription.split('\n').filter(Boolean)
    }))
    
    updateExperience(experienceData)
  }

  const handleAdd = () => {
    const updated = [...projects, emptyProject()]
    setProjects(updated)
    
    const experienceData = updated.map(proj => ({
      title: proj.projectTitle,
      role: proj.yourRole,
      technologies: proj.technologiesUsed.split(',').map(t => t.trim()).filter(Boolean),
      duration: proj.projectDuration,
      description: proj.projectDescription.split('\n').filter(Boolean)
    }))
    
    updateExperience(experienceData)
  }

  const handleRemove = (index) => {
    const updated = projects.filter((_, i) => i !== index)
    setProjects(updated.length > 0 ? updated : [emptyProject()])
    
    const experienceData = updated.length > 0 
      ? updated.map(proj => ({
          title: proj.title,
          role: proj.role,
          technologies: Array.isArray(proj.technologies) ? proj.technologies : 
                       (proj.technologies ? [proj.technologies] : []),
          start_date: proj.start_date,
          end_date: proj.end_date,
          description: proj.description
        }))
      : []
    
    updateExperience(experienceData)
  }

  return (
    <ResumeBuilderLayout>
      <h1 className="text-2xl font-bold text-gray-900 mb-2">Projects</h1>
      <p className="text-gray-600 mb-8">
        List your projects with relevant details and technologies used.
      </p>

      <div className="space-y-6">
        {projects.map((proj, index) => (
          <div
            key={index}
            className="border border-gray-200 rounded-xl p-5 bg-gray-50 relative"
          >
            {projects.length > 1 && (
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
                  Project Title
                </label>
                <input
                  type="text"
                  className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter project title"
                  value={proj.title}
                  onChange={(e) => handleChange(index, 'title', e.target.value)}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Your Role
                </label>
                <input
                  type="text"
                  className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Your role in the project"
                  value={proj.role}
                  onChange={(e) => handleChange(index, 'role', e.target.value)}
                />
              </div>
            </div>

            <div className="grid md:grid-cols-2 gap-6 mb-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Technologies Used
                </label>
                <input
                  type="text"
                  className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Technologies used in the project"
                  value={proj.technologiesUsed}
                  onChange={(e) => handleChange(index, 'technologiesUsed', e.target.value)}
                />
                <p className="text-xs text-gray-500 mt-1">
                  Separate technologies with commas
                </p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Project Duration
                </label>
                <input
                  type="text"
                  className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Jan 2023 - Present"
                  value={proj.projectDuration}
                  onChange={(e) => handleChange(index, 'projectDuration', e.target.value)}
                />
                <p className="text-xs text-gray-500 mt-1">
                  Format: MMM YYYY - MMM YYYY or 'Present'
                </p>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Project Description
              </label>
              <textarea
                rows={4}
                className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="• Describe your project and your contributions\n• Highlight key features and technologies used\n• Mention any challenges you overcame"
                value={proj.projectDescription}
                onChange={(e) => handleChange(index, 'projectDescription', e.target.value)}
              />
              <p className="text-xs text-gray-500 mt-1">
                Use bullet points (•) for better readability. Focus on your contributions and achievements.
              </p>
            </div>
          </div>
        ))}

        <button
          type="button"
          className="text-sm font-medium text-blue-600 hover:text-blue-700"
          onClick={handleAdd}
        >
          + Add Another Project
        </button>
      </div>
    </ResumeBuilderLayout>
  )
}

export default Projects
