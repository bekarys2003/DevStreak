// src/features/auth/LogoutButton.tsx
import React from 'react'
import { useAppDispatch } from '../../app/hooks'
import { clearCredentials } from '../authSlice'
import { clearUser } from './userSlice'
import { useNavigate } from 'react-router-dom'

export const LogoutButton: React.FC = () => {
  const dispatch = useAppDispatch()
  const navigate = useNavigate()

  const onLogout = () => {
    dispatch(clearCredentials())
    dispatch(clearUser())
    localStorage.removeItem('authTokens')
    navigate('/login')
  }

  return (
    <button
      onClick={onLogout}
      className="mt-4 px-4 py-2 border rounded hover:bg-gray-100"
    >
      Log out
    </button>
  )
}
