import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { BrowserRouter } from 'react-router'

// TODO: invert wrapping order — StrictMode should be outermost so it catches
// effects/ref issues in the router itself: <StrictMode><BrowserRouter>...</BrowserRouter></StrictMode>
createRoot(document.getElementById('root')!).render(
  <BrowserRouter><StrictMode>
    <App />
  </StrictMode>
  </BrowserRouter>,
)
