import React from 'react'
import { Routes, Route } from 'react-router-dom'

import { LoginButton } from './features/auth/LoginButton'
import { OAuthCallback } from './features/auth/OAuthCallback'
import { PrivateRoute } from './components/PrivateRoute'
import Home from './pages/Home'
import Dashboard from './pages/Dashboard'
import DailyLeaderboard from './pages/DailyLeaderboard'  // ← import it

import './App.css'

const App: React.FC = () => {

  return (
    <Routes>
      <Route path="/login" element={<LoginButton />} />
      <Route path="/oauth/callback" element={<OAuthCallback />} />

      <Route element={<PrivateRoute />}>
        <Route path="/" element={<Home />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/daily-leaderboard" element={<DailyLeaderboard />} />  {/* ← add this */}

        {/* other protected routes */}
      </Route>
    </Routes>
  )
}

export default App
