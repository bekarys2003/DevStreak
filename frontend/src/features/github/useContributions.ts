// src/features/github/useContributions.ts
import { useEffect, useState } from 'react'
import api from '../../api/axios'

interface Contribs {
  commits: number
  pull_requests: number
  reviews: number
}

export function useContributions() {
  const [data, setData] = useState<Contribs | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api.get<Contribs>('/users/contrib/')
      .then(res => setData(res.data))
      .catch(err => {
        setError(
          err.response?.data?.detail ||
          err.response?.data?.message ||
          err.message
        )
      })
  }, [])

  return { data, error }
}
