import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'

const Signup = () => {
  const navigate = useNavigate()
  
  // Redirect to login page with signup mode
  useEffect(() => {
    navigate('/login', { state: { showSignup: true } })
  }, [navigate])

  return null
}

export default Signup
