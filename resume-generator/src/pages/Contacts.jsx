import { useState, useEffect } from 'react'
import ResumeBuilderLayout from './ResumeBuilderLayout'
import { useResume } from '../context/ResumeContext'

const Contacts = () => {
  const { resumeData, updateContacts } = useResume()
  const [contacts, setContacts] = useState(resumeData.contacts || {
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    location: '',
    desired_job_title: '',
    country: '',
    city: '',
    address: '',
    post_code: '',
    leetcode_url: '',
    github_url: '',
    linkedin_url: '',
  })

  // Update local state when resumeData changes (from backend parsing)
  useEffect(() => {
    if (resumeData && resumeData.contacts) {
      // Ensure all contact fields are initialized with empty strings if undefined
      const updatedContacts = {
        first_name: '',
        last_name: '',
        email: '',
        phone: '',
        location: '',
        desired_job_title: '',
        country: '',
        city: '',
        address: '',
        post_code: '',
        leetcode_url: '',
        github_url: '',
        linkedin_url: '',
        ...resumeData.contacts
      }
      setContacts(updatedContacts)
    }
  }, [resumeData])

  const handleChange = (field, value) => {
    const updated = { ...contacts, [field]: value }
    setContacts(updated)
    // Only update the specific contact field in the context
    updateContacts({
      [field]: value
    })
  }

  return (
    <ResumeBuilderLayout>
      <h1 className="text-2xl font-bold text-gray-900 mb-2">Contacts</h1>
      <p className="text-gray-600 mb-8">
        Add your up-to-date contact information so employers and recruiters can easily
        reach you.
      </p>

      <div className="space-y-6">
        <div className="grid md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              First name
            </label>
            <input
              type="text"
              className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Hari Hare"
              value={contacts.first_name || ''}
              onChange={(e) => handleChange('first_name', e.target.value)}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Last name
            </label>
            <input
              type="text"
              className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Sudhan"
              value={contacts.last_name || ''}
              onChange={(e) => handleChange('last_name', e.target.value)}
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Desired job title
          </label>
          <input
            type="text"
            className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Developer"
            value={contacts.desired_job_title || ''}
            onChange={(e) => handleChange('desired_job_title', e.target.value)}
          />
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Phone
            </label>
            <input
              type="tel"
              className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="+91 - 7548850173"
              value={contacts.phone || ''}
              onChange={(e) => handleChange('phone', e.target.value)}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Email
            </label>
            <input
              type="email"
              className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="hariharesudhan04@gmail.com"
              value={contacts.email || ''}
              onChange={(e) => handleChange('email', e.target.value)}
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Location
          </label>
          <input
            type="text"
            className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="City, State, Country"
            value={contacts.location || ''}
            onChange={(e) => handleChange('location', e.target.value)}
          />
        </div>

        <details className="mt-4 border-t border-gray-200 pt-4">
          <summary className="text-sm font-medium text-blue-600 cursor-pointer">
            Additional information
          </summary>
          <div className="mt-4 space-y-4">
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Country
                </label>
                <input
                  type="text"
                  className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="India"
                  value={contacts.country || ''}
                  onChange={(e) => handleChange('country', e.target.value)}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  City
                </label>
                <input
                  type="text"
                  className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Salem"
                  value={contacts.city || ''}
                  onChange={(e) => handleChange('city', e.target.value)}
                />
              </div>
            </div>
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Address
                </label>
                <input
                  type="text"
                  className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="2/1, Mulluvadi South Street, Near NSR"
                  value={contacts.address || ''}
                  onChange={(e) => handleChange('address', e.target.value)}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Post code
                </label>
                <input
                  type="text"
                  className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="636006"
                  value={contacts.post_code || ''}
                  onChange={(e) => handleChange('post_code', e.target.value)}
                />
              </div>
            </div>

            {/* Social links */}
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  LeetCode profile URL
                </label>
                <input
                  type="url"
                  className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="https://leetcode.com/username"
                  value={contacts.leetcode_url || ''}
                  onChange={(e) => handleChange('leetcode_url', e.target.value)}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  GitHub profile URL
                </label>
                <input
                  type="url"
                  className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="https://github.com/username"
                  value={contacts.github_url || ''}
                  onChange={(e) => handleChange('github_url', e.target.value)}
                />
              </div>
            </div>
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  LinkedIn profile URL
                </label>
                <input
                  type="url"
                  className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="https://www.linkedin.com/in/username"
                  value={contacts.linkedin_url || ''}
                  onChange={(e) => handleChange('linkedin_url', e.target.value)}
                />
              </div>
            </div>
          </div>
        </details>
      </div>
    </ResumeBuilderLayout>
  )
}

export default Contacts
