import React, { useEffect } from 'react'
import { useAppDispatch } from './app/hooks'
import { setCredentials } from './features/authSlice'  // ← fixed path
import { Routes, Route } from 'react-router-dom'

import { LoginButton } from './features/auth/LoginButton'
import { OAuthCallback } from './features/auth/OAuthCallback'
import { PrivateRoute } from './components/PrivateRoute'
import Home from './pages/Home'

import './App.css'

const App: React.FC = () => {
  const dispatch = useAppDispatch()

  useEffect(() => {
    const stored = localStorage.getItem('authTokens')
    if (stored) {
      const { access, refresh } = JSON.parse(stored)
      dispatch(setCredentials({ access, refresh }))
    }
  }, [dispatch])

  return (
    <Routes>
      <Route path="/login" element={<LoginButton />} />
      <Route path="/oauth/callback" element={<OAuthCallback />} />

      <Route element={<PrivateRoute />}>
        <Route path="/" element={<Home />} />
        {/* other protected routes */}
      </Route>
    </Routes>
  )
}

export default App
