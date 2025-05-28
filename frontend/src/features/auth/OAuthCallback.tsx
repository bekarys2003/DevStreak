import React, { useEffect, useState } from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'
import { useAppDispatch } from '../../app/hooks'
import { setCredentials } from '../authSlice'
import api from '../../api/axios'

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
    ;(async () => {
      try {
        const { data } = await api.post('/auth/github/', { code })
        dispatch(setCredentials({ access: data.access, refresh: data.refresh }))
        // persist tokens
        localStorage.setItem('authTokens', JSON.stringify({
          access: data.access,
          refresh: data.refresh
        }))
        navigate('/')  // or wherever
      } catch (e) {
        setError('Login failed')
      }
    })()
  }, [searchParams, dispatch, navigate])

  if (error) return <p className="text-red-600">{error}</p>
  return <p>Signing you in…</p>
}
