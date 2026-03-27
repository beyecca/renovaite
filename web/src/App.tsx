import { Routes, Route } from 'react-router'
import { LandingPage } from './routes/LandingPage'
import { LoginPage } from './routes/LoginPage'
import { VerifyPage } from './routes/VerifyPage'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/auth/verify" element={<VerifyPage />} />
    </Routes>
  )
}