import { useState } from 'react'
import ResumeBuilderLayout from './ResumeBuilderLayout'

const languageLevelLabel = (value) => {
  if (value === 4) return 'Native'
  if (value === 3) return 'Advanced'
  if (value === 2) return 'Intermediate'
  return 'Basic'
}

const Finalize = () => {
  const [languages, setLanguages] = useState([
    { name: 'Tamil', level: 4 },
    { name: 'English', level: 3 },
    { name: 'German', level: 2 },
    { name: 'Hindi', level: 2 },
  ])

  const [links, setLinks] = useState([
    { title: 'Microsoft Azure AZ-900', url: '' },
    { title: 'Prompt Design in Vertex AI', url: '' },
  ])

  const [hobbies, setHobbies] = useState([
    { name: 'Photography' },
    { name: 'Video Editing' },
  ])

  const [awards, setAwards] = useState([
    "2nd Runner up in International KaniTamil'24 Conference for AI Based Tamil Palmleaf Manuscript Reader.",
  ])

  const [customSections, setCustomSections] = useState([
    { name: '', description: '' },
  ])

  const [certificates, setCertificates] = useState([
    {
      name: 'Microsoft Azure AZ-900',
      organization: 'Microsoft',
      completionDate: '',
      credentialId: '',
      credentialUrl: '',
    },
  ])

  const [openSections, setOpenSections] = useState({
    languages: true,
    certifications: false,
    websites: false,
    hobbies: false,
    awards: false,
    custom: false,
  })

  const handleLanguageChange = (index, field, value) => {
    setLanguages((prev) =>
      prev.map((lang, i) => (i === index ? { ...lang, [field]: value } : lang)),
    )
  }

  const handleLanguageAdd = () => {
    setLanguages((prev) => [...prev, { name: '', level: 2 }])
  }

  const handleLanguageRemove = (index) => {
    setLanguages((prev) => prev.filter((_, i) => i !== index))
  }

  const handleLinkChange = (index, field, value) => {
    setLinks((prev) =>
      prev.map((link, i) => (i === index ? { ...link, [field]: value } : link)),
    )
  }

  const handleLinkAdd = () => {
    setLinks((prev) => [...prev, { title: '', url: '' }])
  }

  const handleLinkRemove = (index) => {
    setLinks((prev) => prev.filter((_, i) => i !== index))
  }

  const handleHobbyChange = (index, value) => {
    setHobbies((prev) =>
      prev.map((hob, i) => (i === index ? { ...hob, name: value } : hob)),
    )
  }

  const handleHobbyAdd = () => {
    setHobbies((prev) => [...prev, { name: '' }])
  }

  const handleHobbyRemove = (index) => {
    setHobbies((prev) => prev.filter((_, i) => i !== index))
  }

  const handleAwardChange = (index, value) => {
    setAwards((prev) => prev.map((a, i) => (i === index ? value : a)))
  }

  const handleAwardAdd = () => {
    setAwards((prev) => [...prev, ''])
  }

  const handleAwardRemove = (index) => {
    setAwards((prev) => prev.filter((_, i) => i !== index))
  }

  const handleCustomSectionChange = (index, field, value) => {
    setCustomSections((prev) =>
      prev.map((sec, i) => (i === index ? { ...sec, [field]: value } : sec)),
    )
  }

  const handleCustomSectionAdd = () => {
    setCustomSections((prev) => [...prev, { name: '', description: '' }])
  }

  const handleCustomSectionRemove = (index) => {
    setCustomSections((prev) => prev.filter((_, i) => i !== index))
  }

  const handleCertificateChange = (index, field, value) => {
    setCertificates((prev) =>
      prev.map((cert, i) => (i === index ? { ...cert, [field]: value } : cert)),
    )
  }

  const handleCertificateAdd = () => {
    setCertificates((prev) => [
      ...prev,
      { name: '', organization: '', completionDate: '', credentialId: '', credentialUrl: '' },
    ])
  }

  const handleCertificateRemove = (index) => {
    setCertificates((prev) => prev.filter((_, i) => i !== index))
  }

  const toggleSection = (key) => {
    setOpenSections((prev) => ({ ...prev, [key]: !prev[key] }))
  }

  return (
    <ResumeBuilderLayout>
      <h1 className="text-2xl font-bold text-gray-900 mb-2">Additional Sections</h1>
      <p className="text-gray-600 mb-6">
        Add certifications, languages, awards, or any extra details you want recruiters to
        see.
      </p>

      <div className="space-y-8">
        {/* Languages */}
        <section className="border border-gray-200 rounded-2xl p-4">
          <button
            type="button"
            className="w-full flex items-center justify-between"
            onClick={() => toggleSection('languages')}
          >
            <div className="flex items-center gap-3 text-left">
              <div className="w-9 h-9 rounded-lg bg-blue-50 flex items-center justify-center text-blue-600">
                <span className="text-lg">🌐</span>
              </div>
              <div>
                <h2 className="text-sm font-semibold text-gray-900">Languages</h2>
                <p className="text-xs text-gray-600">
                  If relevant, add your native language and any foreign languages you know.
                </p>
              </div>
            </div>
            <span className="text-gray-400 text-xl">
              {openSections.languages ? '▾' : '▸'}
            </span>
          </button>

          {openSections.languages && (
            <div className="mt-4 pt-4 border-t border-gray-100 space-y-4">
              {languages.map((lang, index) => (
                <div
                  key={index}
                  className="border-t border-gray-100 pt-4 mt-2 first:border-t-0 first:pt-0 first:mt-0"
                >
                  <div className="grid md:grid-cols-2 gap-6 items-center">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Language
                      </label>
                      <input
                        type="text"
                        className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        value={lang.name}
                        onChange={(e) =>
                          handleLanguageChange(index, 'name', e.target.value)
                        }
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Level —{' '}
                        <span className="text-blue-600">
                          {languageLevelLabel(lang.level)}
                        </span>
                      </label>
                      <div className="flex items-center gap-3">
                        <div className="flex-1">
                          <div className="w-full h-3 rounded-full bg-blue-100 overflow-hidden">
                            <div
                              className="h-full bg-blue-500 transition-all"
                              style={{ width: `${(lang.level / 4) * 100}%` }}
                            />
                          </div>
                        </div>
                        <input
                          type="range"
                          min="1"
                          max="4"
                          value={lang.level}
                          onChange={(e) =>
                            handleLanguageChange(
                              index,
                              'level',
                              Number(e.target.value),
                            )
                          }
                          className="w-24"
                        />
                      </div>
                    </div>
                  </div>

                  {languages.length > 1 && (
                    <button
                      type="button"
                      className="mt-2 text-xs text-gray-400 hover:text-red-500"
                      onClick={() => handleLanguageRemove(index)}
                    >
                      Remove language
                    </button>
                  )}
                </div>
              ))}

              <button
                type="button"
                className="text-sm font-medium text-blue-600 hover:text-blue-700"
                onClick={handleLanguageAdd}
              >
                + Add language
              </button>
            </div>
          )}
        </section>

        {/* Certifications and licenses */}
        <section className="border border-gray-200 rounded-2xl p-4">
          <button
            type="button"
            className="w-full flex items-center justify-between"
            onClick={() => toggleSection('certifications')}
          >
            <div className="flex items-center gap-3 text-left">
              <div className="w-9 h-9 rounded-lg bg-blue-50 flex items-center justify-center text-blue-600">
                <span className="text-lg">🎓</span>
              </div>
              <div>
                <h2 className="text-sm font-semibold text-gray-900">
                  Certifications and licenses
                </h2>
                <p className="text-xs text-gray-600">
                  Add credentials that back up your expertise.
                </p>
              </div>
            </div>
            <span className="text-gray-400 text-xl">
              {openSections.certifications ? '▾' : '▸'}
            </span>
          </button>

          {openSections.certifications && (
            <div className="mt-4 pt-4 border-t border-gray-100 space-y-4">
              {certificates.map((cert, index) => (
                <div
                  key={index}
                  className="border-t border-gray-100 pt-4 mt-2 first:border-t-0 first:pt-0 first:mt-0"
                >
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
                          handleCertificateChange(index, 'name', e.target.value)
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
                          handleCertificateChange(
                            index,
                            'organization',
                            e.target.value,
                          )
                        }
                      />
                    </div>
                  </div>

                  <div className="grid md:grid-cols-3 gap-6 mb-2">
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
                          handleCertificateChange(
                            index,
                            'completionDate',
                            e.target.value,
                          )
                        }
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Credential ID{' '}
                        <span className="text-gray-400">(optional)</span>
                      </label>
                      <input
                        type="text"
                        className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="Credential ID"
                        value={cert.credentialId}
                        onChange={(e) =>
                          handleCertificateChange(
                            index,
                            'credentialId',
                            e.target.value,
                          )
                        }
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Credential URL{' '}
                        <span className="text-gray-400">(optional)</span>
                      </label>
                      <input
                        type="url"
                        className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="https://"
                        value={cert.credentialUrl}
                        onChange={(e) =>
                          handleCertificateChange(
                            index,
                            'credentialUrl',
                            e.target.value,
                          )
                        }
                      />
                    </div>
                  </div>

                  {certificates.length > 1 && (
                    <button
                      type="button"
                      className="mt-2 text-xs text-gray-400 hover:text-red-500"
                      onClick={() => handleCertificateRemove(index)}
                    >
                      Remove certificate
                    </button>
                  )}
                </div>
              ))}

              <button
                type="button"
                className="text-sm font-medium text-blue-600 hover:text-blue-700"
                onClick={handleCertificateAdd}
              >
                + Add certificate
              </button>
            </div>
          )}
        </section>

        {/* Websites and social media */}
        <section className="border border-gray-200 rounded-2xl p-4">
          <button
            type="button"
            className="w-full flex items-center justify-between"
            onClick={() => toggleSection('websites')}
          >
            <div className="flex items-center gap-3 text-left">
              <div className="w-9 h-9 rounded-lg bg-blue-50 flex items-center justify-center text-blue-600">
                <span className="text-lg">🔗</span>
              </div>
              <div>
                <h2 className="text-sm font-semibold text-gray-900">
                  Websites and social media
                </h2>
                <p className="text-xs text-gray-600">
                  Share your portfolio, blog, LinkedIn, or other related websites.
                </p>
              </div>
            </div>
            <span className="text-gray-400 text-xl">
              {openSections.websites ? '▾' : '▸'}
            </span>
          </button>

          {openSections.websites && (
            <div className="mt-4 pt-4 border-t border-gray-100 space-y-4">
              {links.map((link, index) => (
                <div
                  key={index}
                  className="border-t border-gray-100 pt-4 mt-2 first:border-t-0 first:pt-0 first:mt-0"
                >
                  <div className="grid md:grid-cols-2 gap-6 items-center">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Link title
                      </label>
                      <input
                        type="text"
                        className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        value={link.title}
                        onChange={(e) =>
                          handleLinkChange(index, 'title', e.target.value)
                        }
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        URL
                      </label>
                      <input
                        type="url"
                        className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        value={link.url}
                        onChange={(e) =>
                          handleLinkChange(index, 'url', e.target.value)
                        }
                      />
                    </div>
                  </div>
                  {links.length > 1 && (
                    <button
                      type="button"
                      className="mt-2 text-xs text-gray-400 hover:text-red-500"
                      onClick={() => handleLinkRemove(index)}
                    >
                      Remove link
                    </button>
                  )}
                </div>
              ))}

              <button
                type="button"
                className="text-sm font-medium text-blue-600 hover:text-blue-700"
                onClick={handleLinkAdd}
              >
                + Add another link
              </button>
            </div>
          )}
        </section>

        {/* Hobbies and interests */}
        <section className="border border-gray-200 rounded-2xl p-4">
          <button
            type="button"
            className="w-full flex items-center justify-between"
            onClick={() => toggleSection('hobbies')}
          >
            <div className="flex items-center gap-3 text-left">
              <div className="w-9 h-9 rounded-lg bg-blue-50 flex items-center justify-center text-blue-600">
                <span className="text-lg">🎮</span>
              </div>
              <div>
                <h2 className="text-sm font-semibold text-gray-900">
                  Hobbies and interests
                </h2>
                <p className="text-xs text-gray-600">
                  Include activities relevant to your job or industry.
                </p>
              </div>
            </div>
            <span className="text-gray-400 text-xl">
              {openSections.hobbies ? '▾' : '▸'}
            </span>
          </button>

          {openSections.hobbies && (
            <div className="mt-4 pt-4 border-t border-gray-100 space-y-4">
              {hobbies.map((hob, index) => (
                <div
                  key={index}
                  className="border-t border-gray-100 pt-4 mt-2 first:border-t-0 first:pt-0 first:mt-0"
                >
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Hobby or interest
                  </label>
                  <div className="flex items-center gap-3">
                    <input
                      type="text"
                      className="flex-1 rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                      value={hob.name}
                      onChange={(e) =>
                        handleHobbyChange(index, e.target.value)
                      }
                    />
                    {hobbies.length > 1 && (
                      <button
                        type="button"
                        className="text-xs text-gray-400 hover:text-red-500"
                        onClick={() => handleHobbyRemove(index)}
                      >
                        Remove
                      </button>
                    )}
                  </div>
                </div>
              ))}

              <button
                type="button"
                className="text-sm font-medium text-blue-600 hover:text-blue-700"
                onClick={handleHobbyAdd}
              >
                + Add hobby or interest
              </button>
            </div>
          )}
        </section>

        {/* Awards and honors */}
        <section className="border border-gray-200 rounded-2xl p-4">
          <button
            type="button"
            className="w-full flex items-center justify-between"
            onClick={() => toggleSection('awards')}
          >
            <div className="flex items-center gap-3 text-left">
              <div className="w-9 h-9 rounded-lg bg-blue-50 flex items-center justify-center text-blue-600">
                <span className="text-lg">🏆</span>
              </div>
              <div>
                <h2 className="text-sm font-semibold text-gray-900">
                  Awards and honors
                </h2>
                <p className="text-xs text-gray-600">
                  Share achievements and milestones you&apos;re proud of.
                </p>
              </div>
            </div>
            <span className="text-gray-400 text-xl">
              {openSections.awards ? '▾' : '▸'}
            </span>
          </button>

          {openSections.awards && (
            <div className="mt-4 pt-4 border-t border-gray-100 space-y-4">
              {awards.map((award, index) => (
                <div
                  key={index}
                  className="border-t border-gray-100 pt-4 mt-2 first:border-t-0 first:pt-0 first:mt-0"
                >
                  <textarea
                    rows={3}
                    className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    value={award}
                    onChange={(e) =>
                      handleAwardChange(index, e.target.value)
                    }
                    placeholder="2nd Runner up in International KaniTamil'24 Conference for AI Based Tamil Palmleaf Manuscript Reader..."
                  />
                  {awards.length > 1 && (
                    <button
                      type="button"
                      className="mt-2 text-xs text-gray-400 hover:text-red-500"
                      onClick={() => handleAwardRemove(index)}
                    >
                      Remove award
                    </button>
                  )}
                </div>
              ))}

              <button
                type="button"
                className="text-sm font-medium text-blue-600 hover:text-blue-700"
                onClick={handleAwardAdd}
              >
                + Add award or honor
              </button>
            </div>
          )}
        </section>

        {/* Custom section */}
        <section className="border border-gray-200 rounded-2xl p-4">
          <button
            type="button"
            className="w-full flex items-center justify-between"
            onClick={() => toggleSection('custom')}
          >
            <div className="flex items-center gap-3 text-left">
              <div className="w-9 h-9 rounded-lg bg-blue-50 flex items-center justify-center text-blue-600">
                <span className="text-lg">➕</span>
              </div>
              <div>
                <h2 className="text-sm font-semibold text-gray-900">
                  Custom section
                </h2>
                <p className="text-xs text-gray-600">
                  Create a custom section for any extra info you&apos;d like to add.
                </p>
              </div>
            </div>
            <span className="text-gray-400 text-xl">
              {openSections.custom ? '▾' : '▸'}
            </span>
          </button>

          {openSections.custom && (
            <div className="mt-4 pt-4 border-t border-gray-100 space-y-6">
              {customSections.map((section, index) => (
                <div
                  key={index}
                  className="border-t border-gray-100 pt-4 mt-2 first:border-t-0 first:pt-0 first:mt-0"
                >
                  <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Section name
                    </label>
                    <input
                      type="text"
                      className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                      value={section.name}
                      onChange={(e) =>
                        handleCustomSectionChange(index, 'name', e.target.value)
                      }
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Description
                    </label>
                    <textarea
                      rows={3}
                      className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Volunteering, conference participation, internships, etc."
                      value={section.description}
                      onChange={(e) =>
                        handleCustomSectionChange(
                          index,
                          'description',
                          e.target.value,
                        )
                      }
                    />
                  </div>
                  {customSections.length > 1 && (
                    <button
                      type="button"
                      className="mt-2 text-xs text-gray-400 hover:text-red-500"
                      onClick={() => handleCustomSectionRemove(index)}
                    >
                      Remove section
                    </button>
                  )}
                </div>
              ))}

              <button
                type="button"
                className="text-sm font-medium text-blue-600 hover:text-blue-700"
                onClick={handleCustomSectionAdd}
              >
                + Add custom section
              </button>
            </div>
          )}
        </section>
      </div>
    </ResumeBuilderLayout>
  )
}

export default Finalize
