import { useLocation, useNavigate } from 'react-router-dom'

const steps = [
  { id: 'contacts', label: 'Contacts' },
  { id: 'experience', label: 'Experience' },
  { id: 'education', label: 'Education' },
  { id: 'skills', label: 'Skills' },
  { id: 'certificates', label: 'Certificates' },
  { id: 'summary', label: 'Summary' },
  { id: 'finalize', label: 'Finalize' },
]

const ResumeBuilderLayout = ({ children }) => {
  const navigate = useNavigate()
  const location = useLocation()

  const currentId = location.pathname.split('/').pop()
  const currentIndex = steps.findIndex((s) => s.id === currentId)

  const goToStep = (index) => {
    if (index < 0 || index >= steps.length) return
    navigate(`/builder/${steps[index].id}`)
  }

  return (
    <div className="min-h-screen bg-white">
      <div className="max-w-5xl mx-auto px-4 py-8">
        {/* Stepper */}
        <div className="flex items-center justify-between mb-10">
          {steps.map((step, index) => {
            const isActive = index === currentIndex
            const isCompleted = index < currentIndex
            return (
              <div key={step.id} className="flex-1 flex items-center">
                <button
                  type="button"
                  className={`flex flex-col items-center text-xs md:text-sm font-medium focus:outline-none ${
                    isActive
                      ? 'text-blue-600'
                      : isCompleted
                      ? 'text-green-600'
                      : 'text-gray-400'
                  }`}
                  onClick={() => goToStep(index)}
                >
                  <div
                    className={`w-8 h-8 rounded-full flex items-center justify-center border-2 mb-1 ${
                      isActive
                        ? 'border-blue-600 bg-blue-50'
                        : isCompleted
                        ? 'border-green-500 bg-green-50'
                        : 'border-gray-300 bg-white'
                    }`}
                  >
                    <span className="text-xs">
                      {isCompleted ? '✓' : index + 1}
                    </span>
                  </div>
                  <span>{step.label}</span>
                </button>
                {index !== steps.length - 1 && (
                  <div className="hidden md:block flex-1 h-px bg-gray-200 mx-2" />
                )}
              </div>
            )
          })}
        </div>

        <div className="bg-white border border-gray-200 rounded-2xl shadow-sm p-6 md:p-8">
          {children}
          <div className="mt-8 flex justify-between">
            <button
              type="button"
              className="px-4 py-2 text-sm font-medium text-gray-600 hover:text-gray-900 disabled:opacity-40"
              disabled={currentIndex <= 0}
              onClick={() => goToStep(currentIndex - 1)}
            >
              Back
            </button>
            <button
              type="button"
              className="px-6 py-2 text-sm font-semibold rounded-lg bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-40"
              disabled={currentIndex >= steps.length - 1}
              onClick={() => goToStep(currentIndex + 1)}
            >
              Next
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ResumeBuilderLayout


