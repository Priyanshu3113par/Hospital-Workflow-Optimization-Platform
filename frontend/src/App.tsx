import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { AnimatePresence } from 'framer-motion'
import { HospitalProvider } from '@/context/HospitalContext'
import Layout from '@/components/Layout/Layout'
import Dashboard    from '@/pages/Dashboard'
import Forecasting  from '@/pages/Forecasting'
import Scheduling   from '@/pages/Scheduling'
import Employees    from '@/pages/Employees'
import Departments  from '@/pages/Departments'
import Monitoring   from '@/pages/Monitoring'
import Reports      from '@/pages/Reports'

export default function App() {
  return (
    <HospitalProvider>
      <BrowserRouter>
        <Layout>
          <AnimatePresence mode="wait">
            <Routes>
              <Route path="/"            element={<Dashboard   />} />
              <Route path="/forecasting" element={<Forecasting />} />
              <Route path="/scheduling"  element={<Scheduling  />} />
              <Route path="/employees"   element={<Employees   />} />
              <Route path="/departments" element={<Departments />} />
              <Route path="/monitoring"  element={<Monitoring  />} />
              <Route path="/reports"     element={<Reports     />} />
            </Routes>
          </AnimatePresence>
        </Layout>
      </BrowserRouter>
    </HospitalProvider>
  )
}
