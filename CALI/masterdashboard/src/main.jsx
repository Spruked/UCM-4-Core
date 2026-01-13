import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import ParityDashboard from './pages/ParityDashboard.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <ParityDashboard />
  </StrictMode>,
)
