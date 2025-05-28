// src/features/auth/OAuthCallback.tsx
import React, { useEffect, useState } from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'
import { useAppDispatch } from '../../app/hooks'
import { setCredentials } from '../authSlice'
import api from '../../api/axios'
import axios from 'axios'

export const OAuthCallback: React.FC = () => {
  const [error, setError] = useState<string | null>(null)
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const dispatch = useAppDispatch()

  useEffect(() => {
    const code = searchParams.get('code')
    if (!code) {
      setError('OAuth code missing')
      return
    }

    // IIFE to handle async logic
    ;(async () => {
      try {
        const { data } = await api.post('/auth/github/', { code })
        dispatch(setCredentials({
          access: data.access,
          refresh: data.refresh
        }))
        localStorage.setItem(
          'authTokens',
          JSON.stringify({ access: data.access, refresh: data.refresh })
        )
        navigate('/')
      } catch (err: unknown) {
        console.error('GitHub login error:', err)

        // Decide on the error message
        let message: string

        if (axios.isAxiosError(err) && err.response) {
          // Server returned a JSON { detail: "..." }
          message = err.response.data.detail || `Error ${err.response.status}`
        } else if (err instanceof Error) {
          // Native JS Error
          message = err.message
        } else {
          // Fallback for anything else
          message = String(err)
        }

        setError(message)
      }
    })()
  }, [searchParams, dispatch, navigate])

  if (error) {
    return <p className="text-red-600">{error}</p>
  }

  return <p>Signing you in…</p>
}
