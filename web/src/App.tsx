import { Routes, Route } from 'react-router'
import { LandingPage } from './routes/LandingPage'
import { LoginPage } from './routes/LoginPage'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/verify" element={<div>Verify page coming soon</div>} />
    </Routes>
  )
}