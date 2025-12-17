import { useNavigate } from 'react-router-dom';
import { Shield, ArrowRight, Check } from 'lucide-react';

// Dummy template data
const templates = [
  {
    id: 1,
    name: 'Professional ATS',
    preview: 'professional-ats',
    category: 'ats',
  },
  {
    id: 2,
    name: 'Minimal ATS',
    preview: 'minimal-ats',
    category: 'ats',
  },
  {
    id: 3,
    name: 'Classic ATS',
    preview: 'classic-ats',
    category: 'ats',
  },
  {
    id: 4,
    name: 'Executive ATS',
    preview: 'executive-ats',
    category: 'ats',
  },
  {
    id: 5,
    name: 'Modern ATS',
    preview: 'modern-ats',
    category: 'ats',
  },
  {
    id: 6,
    name: 'Technical ATS',
    preview: 'technical-ats',
    category: 'ats',
  }
];

// Compact JSX version of the HTML "Aether" resume for the Professional ATS preview
const ProfessionalAtsPreview = () => {
  return (
    <div className="h-full w-full bg-[#eef2f6] flex items-stretch justify-stretch">
      <div className="w-full h-full bg-white px-4 py-3 font-[Georgia,ui-serif] text-[8px] leading-snug overflow-hidden border border-gray-300">
        {/* Header */}
        <div className="flex justify-between items-start mb-2">
          <div>
            <h2 className="text-[11px] font-bold m-0">Jessie Smith</h2>
            <p className="text-[8px] text-gray-700 m-0">Human Resource Manager</p>
            <p className="text-[7px] text-gray-600 mt-1">
              New York, USA · 475 Sunnydale Lane, Plano, TX 75071
            </p>
            <p className="text-[7px] text-gray-600 m-0">(469) 385-2948</p>
          </div>
          <div className="text-[7px] text-gray-700 text-right">
            <p className="m-0">email@yourmail.com</p>
          </div>
        </div>

        {/* Summary */}
        <div className="mt-2">
          <p className="text-[8px] font-semibold border-b border-gray-700 pb-0.5 mb-1">
            Summary
          </p>
          <p className="text-[7px] text-gray-700 text-justify">
            Human resources generalist with 8 years of experience in HR, including hiring,
            terminating, employee development, and performance management. Skilled in training
            programs and workplace safety initiatives.
          </p>
        </div>

        {/* Experience */}
        <div className="mt-2">
          <p className="text-[8px] font-semibold border-b border-gray-700 pb-0.5 mb-1">
            Experience
          </p>

          <div className="mb-1.5">
            <div className="flex justify-between text-[7.5px] font-semibold">
              <span>Human Resource Manager</span>
              <span>Apr 2019 – Current</span>
            </div>
            <p className="italic text-[7px] text-gray-700 mb-0.5">
              Jim&apos;s Widget Factory, Plano, TX
            </p>
            <ul className="list-disc ml-4 text-[7px] text-gray-700 space-y-0.5">
              <li>Ensured HR compliance with labor and employment regulations.</li>
              <li>Increased retention by driving workplace satisfaction above 90%.</li>
            </ul>
          </div>

          <div className="mb-1.5">
            <div className="flex justify-between text-[7.5px] font-semibold">
              <span>Workplace Culture &amp; Compliance Specialist</span>
              <span>Sep 2016 – Mar 2019</span>
            </div>
            <p className="italic text-[7px] text-gray-700 mb-0.5">Acme Corp, Dallas, TX</p>
            <ul className="list-disc ml-4 text-[7px] text-gray-700 space-y-0.5">
              <li>Aligned HR policies with federal and state employment laws.</li>
              <li>Implemented conflict resolution and compliance audits.</li>
            </ul>
          </div>
        </div>

        {/* Education and Skills */}
        <div className="mt-2 grid grid-cols-2 gap-3">
          <div>
            <p className="text-[8px] font-semibold border-b border-gray-700 pb-0.5 mb-1">
              Education
            </p>
            <p className="text-[7px] text-gray-700 m-0">
              Master, Human Resources — Dallas, TX (2011)
            </p>
            <p className="text-[7px] text-gray-700 m-0">The University of Texas</p>
          </div>
          <div>
            <p className="text-[8px] font-semibold border-b border-gray-700 pb-0.5 mb-1">
              Skills
            </p>
            <ul className="list-disc ml-4 text-[7px] text-gray-700 space-y-0.5">
              <li>Detail-oriented</li>
              <li>Platform expertise</li>
              <li>Analytics</li>
              <li>Communication</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

const AtsTemplates = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
      {/* Progress Indicator */}
      <div className="max-w-3xl mx-auto mb-12">
        <div className="flex justify-between items-center">
          {/* Step 1 */}
          <div className="flex flex-col items-center">
            <div className="w-10 h-10 rounded-full bg-blue-600 text-white flex items-center justify-center font-medium">
              1
            </div>
            <span className="mt-2 text-sm font-medium text-blue-600">Choose Template</span>
          </div>
          
          {/* Connector */}
          <div className="flex-1 h-1 bg-gray-200">
            <div className="h-1 bg-blue-600 w-1/2"></div>
          </div>
          
          {/* Step 2 */}
          <div className="flex flex-col items-center">
            <div className="w-10 h-10 rounded-full border-2 border-gray-300 bg-white text-gray-400 flex items-center justify-center font-medium">
              2
            </div>
            <span className="mt-2 text-sm font-medium text-gray-500">Enter Details</span>
          </div>
          
          {/* Connector */}
          <div className="flex-1 h-1 bg-gray-200"></div>
          
          {/* Step 3 */}
          <div className="flex flex-col items-center">
            <div className="w-10 h-10 rounded-full border-2 border-gray-300 bg-white text-gray-400 flex items-center justify-center font-medium">
              3
            </div>
            <span className="mt-2 text-sm font-medium text-gray-500">Download</span>
          </div>
        </div>
      </div>

      {/* Page Header */}
      <div className="text-center max-w-3xl mx-auto mb-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">ATS Resume Templates</h1>
        <p className="text-lg text-gray-600 mb-6">
          Choose from professionally designed ATS-friendly resume templates optimized for applicant tracking systems.
        </p>
        <button 
          onClick={() => navigate('/dashboard')}
          className="text-blue-600 hover:text-blue-800 text-sm font-medium transition-colors"
        >
          Choose later
        </button>
      </div>

      {/* Category Filter */}
      <div className="max-w-4xl mx-auto mb-8">
        <div className="inline-flex items-center space-x-1 bg-white p-1 rounded-lg border border-gray-200">
          <button
            className="flex items-center space-x-2 px-4 py-2 rounded-md bg-blue-50 text-blue-700 font-medium"
          >
            <Shield className="w-5 h-5" />
            <span>ATS Friendly</span>
          </button>
        </div>
      </div>

      {/* Template Grid */}
      <div className="max-w-7xl mx-auto">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {templates.map((template) => (
            <div 
              key={template.id}
              onClick={() => navigate('/dashboard', { state: { templateId: template.id } })}
              className="group bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-all duration-200 cursor-pointer hover:-translate-y-1"
            >
              <div className="relative">
                <div className="aspect-[1/1.41] bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center">
                  {template.id === 1 ? (
                    <ProfessionalAtsPreview />
                  ) : (
                    <div className="text-gray-400 text-sm">
                      Template Preview: {template.preview}
                    </div>
                  )}
                </div>
                <div className="absolute top-3 right-3 bg-green-100 text-green-800 text-xs font-medium px-2.5 py-0.5 rounded-full flex items-center">
                  <Check className="w-3 h-3 mr-1" />
                  ATS Optimized
                </div>
              </div>
              <div className="p-4">
                <h3 className="font-medium text-gray-900">{template.name}</h3>
                <div className="mt-2 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button 
                    onClick={(e) => {
                      e.stopPropagation();
                      navigate('/dashboard', { state: { templateId: template.id } });
                    }}
                    className="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-md text-sm transition-colors"
                  >
                    Use This Template
                    <ArrowRight className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default AtsTemplates;
