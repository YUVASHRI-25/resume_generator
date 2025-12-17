import { useNavigate } from 'react-router-dom'
import { useRef, useState } from 'react'

const Dashboard = () => {
  const navigate = useNavigate()
  const fileInputRef = useRef(null)
  const [selectedFile, setSelectedFile] = useState(null)
  const [isDragging, setIsDragging] = useState(false)
  const [showUploadCard, setShowUploadCard] = useState(false)
  const [error, setError] = useState('')

  const handleUploadClick = () => {
    setShowUploadCard(true)
  }

  const handleCreateNewClick = () => {
    // Start the guided resume builder flow from the Contacts step
    navigate('/builder/contacts')
  }

  const handleFileSelect = (file) => {
    if (!file) return

    const maxSizeBytes = 5 * 1024 * 1024 // 5MB
    if (file.size > maxSizeBytes) {
      setError('File size must be 5MB or less.')
      setSelectedFile(null)
      return
    }

    setError('')
    setSelectedFile(file)
  }

  const onFileInputChange = (event) => {
    const file = event.target.files?.[0]
    handleFileSelect(file)
  }

  const handleDrop = (event) => {
    event.preventDefault()
    event.stopPropagation()
    setIsDragging(false)

    const file = event.dataTransfer.files?.[0]
    handleFileSelect(file)
  }

  const handleDragOver = (event) => {
    event.preventDefault()
    event.stopPropagation()
    setIsDragging(true)
  }

  const handleDragLeave = (event) => {
    event.preventDefault()
    event.stopPropagation()
    setIsDragging(false)
  }

  const handleUploadResume = () => {
    if (!selectedFile) return

    // Here you could send the file to your backend/API.
    // After upload, navigate into the resume builder starting at Contacts.
    console.log('Uploading file:', selectedFile)
    navigate('/builder/contacts')
  }

  const formatFileSize = (bytes) => {
    if (!bytes && bytes !== 0) return ''
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-10 text-center">Create Your Resume</h1>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl mx-auto mb-10">
          {/* Upload Resume Card */}
          <div
            className="card p-8 text-center cursor-pointer hover:shadow-xl transition-shadow duration-300 h-full flex flex-col"
            onClick={handleUploadClick}
          >
            <div className="bg-blue-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-6">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-8 w-8 text-blue-600"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Upload a Resume</h3>
            <p className="text-gray-600 mb-6">Upload an existing resume to improve or analyze</p>
            <div className="mt-auto">
              <button
                className="btn-secondary"
                onClick={(event) => {
                  event.stopPropagation()
                  setShowUploadCard(true)
                  fileInputRef.current?.click()
                }}
              >
                Choose File
              </button>
            </div>
          </div>

          {/* Create New Resume Card */}
          <div
            className="card p-8 text-center cursor-pointer hover:shadow-xl transition-shadow duration-300 h-full flex flex-col"
            onClick={handleCreateNewClick}
          >
            <div className="bg-green-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-6">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-8 w-8 text-green-600"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
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

        {showUploadCard && (
          <div className="max-w-2xl mx-auto bg-white rounded-2xl shadow-lg border border-gray-200 p-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Upload Your Resume</h2>
            <p className="text-gray-600 mb-8">We&apos;ll help you create the perfect resume</p>

            {/* Hidden file input */}
            <input
              type="file"
              ref={fileInputRef}
              className="hidden"
              accept=".pdf,.doc,.docx,.html,.txt"
              onChange={onFileInputChange}
            />

            {/* Drag and drop area */}
            <div
              className={`border-2 border-dashed rounded-xl p-10 text-center mb-6 transition-colors ${
                isDragging ? 'border-blue-500 bg-blue-50' : 'border-gray-300 bg-gray-50'
              }`}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
            >
              <div className="flex flex-col items-center justify-center space-y-4">
                <div className="w-12 h-12 rounded-full bg-white flex items-center justify-center shadow-sm">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    className="h-6 w-6 text-blue-600"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1M8 12l4-4m0 0l4 4m-4-4v12" />
                  </svg>
                </div>
                <div>
                  <p className="text-blue-600 font-semibold">Drag and drop your resume here</p>
                  <p className="text-gray-500 text-sm mt-1">or</p>
                </div>
                <button
                  type="button"
                  className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-6 rounded-lg text-sm transition-colors"
                  onClick={() => fileInputRef.current?.click()}
                >
                  Upload from device
                </button>
                <p className="text-gray-400 text-xs mt-2">
                  Files we can read: PDF, DOCX, HTML, TXT (Max 5MB)
                </p>
              </div>
            </div>

            {/* Selected file info */}
            {selectedFile && (
              <div className="mb-6 border border-gray-200 rounded-xl p-4 flex items-center justify-between bg-gray-50">
                <div className="flex items-center gap-3">
                  <div className="w-9 h-9 rounded-lg bg-white flex items-center justify-center border border-gray-200">
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      className="h-5 w-5 text-gray-500"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M7 21h10a2 2 0 002-2V9.5a2 2 0 00-.586-1.414l-4.5-4.5A2 2 0 0012.5 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"
                      />
                    </svg>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-900 truncate max-w-xs">{selectedFile.name}</p>
                    <p className="text-xs text-gray-500">{formatFileSize(selectedFile.size)}</p>
                  </div>
                </div>
                <button
                  type="button"
                  className="text-gray-400 hover:text-gray-600"
                  onClick={() => setSelectedFile(null)}
                >
                  <span className="sr-only">Remove file</span>
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    className="h-5 w-5"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            )}

            {error && <p className="text-sm text-red-600 mb-4">{error}</p>}

            <button
              type="button"
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              disabled={!selectedFile}
              onClick={handleUploadResume}
            >
              Upload Resume
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

export default Dashboard
