import { useEffect } from 'react'
import { Routes, Route, useNavigate } from 'react-router'
import { LandingPage } from './routes/LandingPage'
import { LoginPage } from './routes/LoginPage'
import { VerifyPage } from './routes/VerifyPage'

export default function App() {
  const navigate = useNavigate();

  useEffect(() => {
    function handleUnauthorized() {
      navigate("/login");
    }
    window.addEventListener("auth:unauthorized", handleUnauthorized);
    return () => window.removeEventListener("auth:unauthorized", handleUnauthorized);
  }, [navigate]);

  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/auth/verify" element={<VerifyPage />} />
    </Routes>
  )
}