import { useNavigate } from 'react-router-dom'

const Dashboard = () => {
  const navigate = useNavigate()

  const handleUploadClick = () => {
    console.log('Upload resume clicked')
    // In a real app, this would open a file upload dialog
    alert('Upload resume functionality would go here')
  }

  const handleCreateNewClick = () => {
    console.log('Create new resume clicked')
    // In a real app, this would navigate to the resume builder
    alert('Create new resume functionality would go here')
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-10 text-center">Create Your Resume</h1>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl mx-auto">
          {/* Upload Resume Card */}
          <div 
            className="card p-8 text-center cursor-pointer hover:shadow-xl transition-shadow duration-300 h-full flex flex-col"
            onClick={handleUploadClick}
          >
            <div className="bg-blue-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-6">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Upload a Resume</h3>
            <p className="text-gray-600 mb-6">Upload an existing resume to improve or analyze</p>
            <div className="mt-auto">
              <button className="btn-secondary">Choose File</button>
            </div>
          </div>

          {/* Create New Resume Card */}
          <div 
            className="card p-8 text-center cursor-pointer hover:shadow-xl transition-shadow duration-300 h-full flex flex-col"
            onClick={handleCreateNewClick}
          >
            <div className="bg-green-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-6">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Start From Scratch</h3>
            <p className="text-gray-600 mb-6">Create a resume step-by-step from scratch</p>
            <div className="mt-auto">
              <button className="btn-primary">Get Started</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
