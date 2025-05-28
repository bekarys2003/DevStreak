import { useEffect, useState } from 'react'
import api from '../../api/axios'

export function useStreak() {
  const [streak, setStreak] = useState<number | null>(null)
  const [error,  setError]  = useState<string | null>(null)

  useEffect(() => {
    api.get<{ streak: number }>('/users/streak/')
      .then(res => setStreak(res.data.streak))
      .catch(err => {
        setError(
          err.response?.data?.detail ||
          err.response?.data?.message ||
          err.message
        )
      })
  }, [])

  return { streak, error }
}
