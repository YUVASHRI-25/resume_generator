import { useNavigate } from 'react-router-dom'

const LandingPage = () => {
  const navigate = useNavigate()

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-blue-50 to-white p-6">
      <div className="text-center max-w-3xl mx-auto">
        <h1 className="text-5xl font-bold text-gray-900 mb-6">Resume Generator</h1>
        <p className="text-xl text-gray-600 mb-10">Create professional resumes in minutes</p>
        <button
          onClick={() => navigate('/login')}
          className="btn-primary text-lg px-8 py-3"
        >
          Get Started
        </button>
      </div>
    </div>
  )
}

export default LandingPage
