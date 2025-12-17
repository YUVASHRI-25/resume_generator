import { useState } from 'react'
import ResumeBuilderLayout from './ResumeBuilderLayout'

const levelLabel = (value) => {
  if (value <= 1) return 'Beginner'
  if (value === 2) return 'Intermediate'
  if (value === 3) return 'Advanced'
  return 'Expert'
}

const Skills = () => {
  const [showLevel, setShowLevel] = useState(true)
  const [skills, setSkills] = useState([
    { name: 'Quick and Smart Learner', level: 4 },
    { name: 'Leadership', level: 4 },
  ])

  const handleSkillChange = (index, field, value) => {
    setSkills((prev) =>
      prev.map((skill, i) => (i === index ? { ...skill, [field]: value } : skill)),
    )
  }

  const handleAddSkill = () => {
    setSkills((prev) => [...prev, { name: '', level: 2 }])
  }

  const handleRemoveSkill = (index) => {
    setSkills((prev) => prev.filter((_, i) => i !== index))
  }

  return (
    <ResumeBuilderLayout>
      <h1 className="text-2xl font-bold text-gray-900 mb-2">Skills</h1>
      <p className="text-gray-600 mb-6">
        Add your most relevant professional skills.
      </p>

      <div className="flex items-center mb-6">
        <label className="mr-3 text-sm font-medium text-gray-700">
          Show experience level
        </label>
        <button
          type="button"
          onClick={() => setShowLevel((prev) => !prev)}
          className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
            showLevel ? 'bg-blue-600' : 'bg-gray-300'
          }`}
        >
          <span
            className={`inline-block h-5 w-5 transform rounded-full bg-white transition-transform ${
              showLevel ? 'translate-x-5' : 'translate-x-1'
            }`}
          />
        </button>
      </div>

      <div className="space-y-4">
        {skills.map((skill, index) => (
          <div
            key={index}
            className="border border-gray-200 rounded-xl p-4 flex flex-col md:flex-row md:items-center gap-4 relative"
          >
            {skills.length > 1 && (
              <button
                type="button"
                className="absolute top-3 right-3 text-xs text-gray-400 hover:text-red-500"
                onClick={() => handleRemoveSkill(index)}
              >
                Remove
              </button>
            )}

            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Skill
              </label>
              <input
                type="text"
                className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Skill"
                value={skill.name}
                onChange={(e) =>
                  handleSkillChange(index, 'name', e.target.value)
                }
              />
            </div>

            {showLevel && (
              <div className="flex-1">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Level —{' '}
                  <span className="text-blue-600">{levelLabel(skill.level)}</span>
                </label>
                <div className="flex items-center gap-3">
                  <div className="flex-1">
                    <div className="w-full h-3 rounded-full bg-blue-100 overflow-hidden">
                      <div
                        className="h-full bg-blue-500 transition-all"
                        style={{ width: `${(skill.level / 4) * 100}%` }}
                      />
                    </div>
                  </div>
                  <input
                    type="range"
                    min="1"
                    max="4"
                    value={skill.level}
                    onChange={(e) =>
                      handleSkillChange(index, 'level', Number(e.target.value))
                    }
                    className="w-24"
                  />
                </div>
              </div>
            )}
          </div>
        ))}

        <button
          type="button"
          className="text-sm font-medium text-blue-600 hover:text-blue-700"
          onClick={handleAddSkill}
        >
          + Add skill
        </button>
      </div>
    </ResumeBuilderLayout>
  )
}

export default Skills
