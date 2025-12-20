import { Routes, Route, Navigate } from 'react-router-dom'
import LandingPage from './pages/LandingPage'
import Login from './pages/Login'
import Signup from './pages/Signup'
import Dashboard from './pages/Dashboard'
import ResumeChoice from './pages/ResumeChoice'
import AtsTemplates from './pages/AtsTemplates'
import Contacts from './pages/Contacts'
import Projects from './pages/Projects'
import Education from './pages/Education'
import Skills from './pages/Skills'
import Certificates from './pages/Certificates'
import Summary from './pages/Summary'
import JobDescription from './pages/JobDescription'
import Finalize from './pages/Finalize'

function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/resume-choice" element={<ResumeChoice />} />
        <Route path="/templates/ats" element={<AtsTemplates />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/builder/contacts" element={<Contacts />} />
        <Route path="/builder/experience" element={<Projects />} />
        <Route path="/builder/education" element={<Education />} />
        <Route path="/builder/skills" element={<Skills />} />
        <Route path="/builder/certificates" element={<Certificates />} />
        <Route path="/builder/summary" element={<Summary />} />
        <Route path="/builder/job-description" element={<JobDescription />} />
        <Route path="/builder/finalize" element={<Finalize />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </div>
  )
}

export default App
