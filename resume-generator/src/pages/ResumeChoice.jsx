import { useNavigate } from 'react-router-dom';

const ResumeChoice = () => {
  const navigate = useNavigate();

  const handleCreateNew = () => {
    navigate('/dashboard?mode=scratch');
  };

  const handleImproveExisting = () => {
    navigate('/dashboard?mode=upload');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-white">
      <div className="container mx-auto px-4 py-16 md:py-24">
        <div className="flex flex-col md:flex-row items-center justify-between gap-12">
          {/* Left Side - Content */}
          <div className="w-full md:w-1/2 space-y-8">
            <div className="max-w-md mx-auto md:mx-0">
              <h1 className="text-4xl md:text-5xl font-bold text-gray-900 leading-tight mb-6">
                Build a Resume That Gets You Hired
              </h1>
              <p className="text-lg text-gray-600 mb-8">
                Create a professional resume in minutes with our easy-to-use builder. 
                Get expert suggestions to improve your resume and land your dream job faster.
              </p>
              
              <div className="flex flex-col sm:flex-row gap-4 mb-8">
                <button
                  onClick={handleCreateNew}
                  className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-8 rounded-lg transition-all duration-200 transform hover:scale-105 shadow-lg"
                >
                  Create New Resume
                </button>
                <button
                  onClick={handleImproveExisting}
                  className="border-2 border-blue-600 text-blue-600 hover:bg-blue-50 font-medium py-3 px-8 rounded-lg transition-all duration-200"
                >
                  Improve Existing Resume
                </button>
              </div>
              
              <div className="space-y-3 text-sm text-gray-600">
                <div className="flex items-center">
                  <svg className="w-5 h-5 text-green-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  Higher chance of getting hired
                </div>
                <div className="flex items-center">
                  <svg className="w-5 h-5 text-green-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  Better salary opportunities
                </div>
                <div className="flex items-center">
                  <svg className="w-5 h-5 text-green-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  ATS-optimized templates
                </div>
              </div>
            </div>
          </div>

          {/* Right Side - Resume Preview */}
          <div className="w-full md:w-1/2 relative">
            <div className="bg-white rounded-xl shadow-2xl overflow-hidden transform rotate-1 hover:rotate-0 transition-transform duration-300 max-w-md mx-auto">
              {/* Resume Header */}
              <div className="bg-blue-600 text-white p-6">
                <div className="flex items-center">
                  <div className="w-16 h-16 rounded-full bg-blue-400 flex items-center justify-center text-2xl font-bold text-white">
                    JD
                  </div>
                  <div className="ml-4">
                    <h2 className="text-xl font-bold">John Doe</h2>
                    <p className="text-blue-100">Senior Product Designer</p>
                  </div>
                </div>
              </div>
              
              {/* Resume Content */}
              <div className="p-6 space-y-6">
                <div>
                  <h3 className="text-sm font-semibold text-blue-600 uppercase tracking-wider mb-2">Summary</h3>
                  <p className="text-sm text-gray-700">
                    Experienced product designer with 5+ years in creating user-centered digital experiences. 
                    Passionate about solving complex problems through clean and intuitive design.
                  </p>
                </div>
                
                <div>
                  <h3 className="text-sm font-semibold text-blue-600 uppercase tracking-wider mb-2">Experience</h3>
                  <div className="space-y-4">
                    <div>
                      <div className="flex justify-between">
                        <span className="font-medium">Senior Product Designer</span>
                        <span className="text-sm text-gray-500">2020 - Present</span>
                      </div>
                      <p className="text-sm text-gray-600">TechCorp Inc.</p>
                    </div>
                    <div>
                      <div className="flex justify-between">
                        <span className="font-medium">UI/UX Designer</span>
                        <span className="text-sm text-gray-500">2018 - 2020</span>
                      </div>
                      <p className="text-sm text-gray-600">DesignHub</p>
                    </div>
                  </div>
                </div>
                
                <div>
                  <h3 className="text-sm font-semibold text-blue-600 uppercase tracking-wider mb-2">Skills</h3>
                  <div className="flex flex-wrap gap-2">
                    {['UX Research', 'UI Design', 'Figma', 'Sketch', 'Prototyping', 'User Testing', 'HTML/CSS', 'Design Systems'].map((skill) => (
                      <span key={skill} className="px-3 py-1 bg-blue-50 text-blue-700 text-xs rounded-full">
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
              
              {/* Floating Badges */}
              <div className="absolute -top-4 -right-4 bg-green-100 text-green-800 text-xs font-semibold px-3 py-1 rounded-full shadow-md">
                ATS Friendly
              </div>
              <div className="absolute -bottom-4 -left-4 bg-purple-100 text-purple-800 text-xs font-semibold px-3 py-1 rounded-full shadow-md">
                AI Suggestions
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResumeChoice;
