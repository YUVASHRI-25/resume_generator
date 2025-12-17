import { useNavigate } from 'react-router-dom';
import { ArrowRight, FileText, Upload, Home } from 'lucide-react';

const ResumeChoice = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-white">
      <div className="container mx-auto px-4 py-8 md:py-12">
        {/* Navigation */}
        <div className="flex justify-between items-center mb-8">
          <button
            onClick={() => navigate('/')}
            className="flex items-center gap-2 text-blue-600 hover:text-blue-800 transition-colors"
          >
            <Home size={20} />
            <span>Home</span>
          </button>
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full">Step 3 of 3</span>
          </div>
        </div>

        <div className="flex flex-col md:flex-row items-center justify-between gap-12">
          {/* Left Side - Content */}
          <div className="md:w-1/2 space-y-8">
            <div className="space-y-4">
              <h1 className="text-4xl md:text-5xl font-bold text-gray-900 leading-tight">
                Let's Build Your Resume
              </h1>
              <p className="text-lg text-gray-600">
                Choose how you'd like to create your professional resume. You can start from scratch or upload an existing one.
              </p>
            </div>

            <div className="space-y-4 pt-4">
              <div className="space-y-2">
                <button
                  onClick={() => navigate('/templates/ats')}
                  className="w-full flex items-center justify-between gap-4 bg-white hover:bg-gray-50 border border-gray-200 text-gray-800 font-medium py-4 px-6 rounded-lg transition-all duration-200 shadow-sm hover:shadow-md"
                >
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-blue-100 rounded-lg">
                      <FileText className="text-blue-600" size={20} />
                    </div>
                    <div className="text-left">
                      <div className="font-semibold">Create New Resume</div>
                      <div className="text-sm text-gray-500">Choose from ATS-optimized templates</div>
                    </div>
                  </div>
                  <ArrowRight size={18} className="text-gray-400" />
                </button>

                <button
                  onClick={() => navigate('/dashboard?mode=upload')}
                  className="w-full flex items-center justify-between gap-4 bg-white hover:bg-gray-50 border border-gray-200 text-gray-800 font-medium py-4 px-6 rounded-lg transition-all duration-200 shadow-sm hover:shadow-md"
                >
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-green-100 rounded-lg">
                      <Upload className="text-green-600" size={20} />
                    </div>
                    <div className="text-left">
                      <div className="font-semibold">Improve Existing Resume</div>
                      <div className="text-sm text-gray-500">Upload and enhance your current resume</div>
                    </div>
                  </div>
                  <ArrowRight size={18} className="text-gray-400" />
                </button>
              </div>

              <div className="pt-4">
                <button
                  onClick={() => navigate('/dashboard?mode=scratch')}
                  className="w-full py-3 px-4 bg-gray-100 hover:bg-gray-200 text-gray-700 font-medium rounded-lg transition-colors duration-200 flex items-center justify-center gap-2"
                >
                  Use Basic Template (No ATS Optimization)
                </button>
              </div>
            </div>

            <div className="pt-8 space-y-2">
              <div className="flex items-center gap-2 text-green-600">
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path
                    fillRule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                    clipRule="evenodd"
                  />
                </svg>
                <span className="text-sm font-medium">Higher chance of getting hired</span>
              </div>
              <div className="flex items-center gap-2 text-green-600">
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path
                    fillRule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                    clipRule="evenodd"
                  />
                </svg>
                <span className="text-sm font-medium">Better salary opportunities</span>
              </div>
            </div>
          </div>

          {/* Right Side - Resume Preview */}
          <div className="md:w-1/2 relative">
            <div className="bg-white rounded-xl shadow-2xl p-6 transform rotate-1 hover:rotate-0 transition-transform duration-300 max-w-md mx-auto">
              <div className="flex items-center gap-4 mb-6">
                <div className="w-16 h-16 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 text-2xl font-bold">
                  JD
                </div>
                <div>
                  <h3 className="text-xl font-bold text-gray-900">John Doe</h3>
                  <p className="text-gray-600">Senior Product Designer</p>
                </div>
              </div>

              <div className="space-y-4">
                <div>
                  <h4 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-2">Summary</h4>
                  <p className="text-gray-700 text-sm leading-relaxed">
                    Experienced product designer with 5+ years in creating beautiful and functional user experiences.
                  </p>
                </div>

                <div>
                  <h4 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-2">Skills</h4>
                  <div className="flex flex-wrap gap-2">
                    {['UI/UX Design', 'Figma', 'User Research', 'Prototyping', 'HTML/CSS', 'JavaScript'].map((skill) => (
                      <span key={skill} className="bg-blue-50 text-blue-700 text-xs px-3 py-1 rounded-full">
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>

                <div>
                  <h4 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-2">Experience</h4>
                  <div className="space-y-2">
                    <div>
                      <p className="font-medium text-gray-900">Senior Product Designer</p>
                      <p className="text-sm text-gray-600">TechCorp • 2020 - Present</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Floating Badges */}
              <div className="absolute -top-4 -right-4">
                <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                  ATS Friendly
                </span>
              </div>
              <div className="absolute -bottom-4 -left-4">
                <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                  AI Suggestions
                </span>
              </div>
            </div>

            {/* Decorative Elements */}
            <div className="absolute -z-10 w-64 h-64 bg-blue-200 rounded-full mix-blend-multiply filter blur-xl opacity-20 -top-20 -right-20" />
            <div className="absolute -z-10 w-72 h-72 bg-purple-200 rounded-full mix-blend-multiply filter blur-xl opacity-20 bottom-10 -left-10" />
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResumeChoice;
