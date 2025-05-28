import React from 'react'
import { useAppSelector } from '../app/hooks'
import { Navigate, Outlet } from 'react-router-dom'

export const PrivateRoute = () => {
  const token = useAppSelector(state => state.auth.accessToken)
  return token ? <Outlet /> : <Navigate to="/login" replace />
}
