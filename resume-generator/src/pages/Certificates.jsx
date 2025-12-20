import { useState, useEffect } from 'react'
import ResumeBuilderLayout from './ResumeBuilderLayout'
import { useResume } from '../context/ResumeContext'

const emptyCertificate = () => ({
  name: '',
  organization: '',
  completionDate: '',
  credentialId: '',
  credentialUrl: '',
})

const Certificates = () => {
  const { resumeData, updateCertifications } = useResume()
  const [certificates, setCertificates] = useState(
    resumeData.certifications && resumeData.certifications.length > 0
      ? resumeData.certifications.map((cert) =>
          typeof cert === 'string'
            ? { ...emptyCertificate(), name: cert }
            : { ...emptyCertificate(), name: cert.name || cert }
        )
      : [emptyCertificate()]
  )

  // Update local state when resumeData changes (from backend parsing)
  useEffect(() => {
    if (resumeData.certifications && resumeData.certifications.length > 0) {
      setCertificates(
        resumeData.certifications.map((cert) => {
          if (typeof cert === 'string') {
            return { ...emptyCertificate(), name: cert }
          } else if (cert.certificate_name || cert.issuing_organization) {
            // Map backend format to frontend format
            return {
              name: cert.certificate_name || '',
              organization: cert.issuing_organization || '',
              completionDate: cert.date_of_completion || '',
              credentialId: cert.credential_id || '',
              credentialUrl: cert.credential_url || ''
            }
          } else {
            // Fallback to existing format
            return { ...emptyCertificate(), name: cert.name || cert }
          }
        })
      )
    }
  }, [resumeData.certifications])

  const handleChange = (index, field, value) => {
    const updated = certificates.map((cert, i) =>
      i === index ? { ...cert, [field]: value } : cert
    )
    setCertificates(updated)
    updateCertifications(updated.map((c) => c.name))
  }

  const handleAdd = () => {
    const updated = [...certificates, emptyCertificate()]
    setCertificates(updated)
    updateCertifications(updated.map((c) => c.name))
  }

  const handleRemove = (index) => {
    const updated = certificates.filter((_, i) => i !== index)
    setCertificates(updated.length > 0 ? updated : [emptyCertificate()])
    updateCertifications(
      updated.length > 0 ? updated.map((c) => c.name) : []
    )
  }

  return (
    <ResumeBuilderLayout>
      <h1 className="text-2xl font-bold text-gray-900 mb-2">Certificates</h1>
      <p className="text-gray-600 mb-8">
        Add certifications and courses you&apos;ve completed.
      </p>

      <div className="space-y-6">
        {certificates.map((cert, index) => (
          <div
            key={index}
            className="border border-gray-200 rounded-xl p-5 bg-gray-50 relative"
          >
            {certificates.length > 1 && (
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
                  Certificate name
                </label>
                <input
                  type="text"
                  className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g., Microsoft Azure AZ-900"
                  value={cert.name}
                  onChange={(e) =>
                    handleChange(index, 'name', e.target.value)
                  }
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Issuing organization
                </label>
                <input
                  type="text"
                  className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g., Microsoft"
                  value={cert.organization}
                  onChange={(e) =>
                    handleChange(index, 'organization', e.target.value)
                  }
                />
              </div>
            </div>

            <div className="grid md:grid-cols-3 gap-6 mb-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Date of completion
                </label>
                <input
                  type="text"
                  className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="MM/YYYY"
                  value={cert.completionDate}
                  onChange={(e) =>
                    handleChange(index, 'completionDate', e.target.value)
                  }
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Credential ID <span className="text-gray-400">(optional)</span>
                </label>
                <input
                  type="text"
                  className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Credential ID"
                  value={cert.credentialId}
                  onChange={(e) =>
                    handleChange(index, 'credentialId', e.target.value)
                  }
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Credential URL <span className="text-gray-400">(optional)</span>
                </label>
                <input
                  type="url"
                  className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="https://"
                  value={cert.credentialUrl}
                  onChange={(e) =>
                    handleChange(index, 'credentialUrl', e.target.value)
                  }
                />
              </div>
            </div>
          </div>
        ))}

        <button
          type="button"
          className="text-sm font-medium text-blue-600 hover:text-blue-700"
          onClick={handleAdd}
        >
          + Add certificate
        </button>
      </div>
    </ResumeBuilderLayout>
  )
}

export default Certificates
