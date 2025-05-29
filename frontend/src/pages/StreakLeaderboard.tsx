import React, { useEffect, useState } from 'react'
import api from '../api/axios'

export interface StreakEntry {
  username: string
  streak:   number
}

export const StreakLeaderboard: React.FC = () => {
  const [entries, setEntries] = useState<StreakEntry[] | null>(null)
  const [error,   setError]   = useState<string | null>(null)

  useEffect(() => {
    (async () => {
      try {
        const { data } = await api.get<StreakEntry[]>('users/streak-lb/')
        setEntries(data)
      } catch (err: any) {
        setError(err.response?.data?.detail || err.message)
      }
    })()
  }, [])

  if (error) {
    return <p className="text-red-600">Error: {error}</p>
  }
  if (!entries) {
    return <p>Loading streak leaderboard…</p>
  }

  return (
    <div className="p-4">
      <h2 className="text-xl font-bold mb-2">🏅 Streak Leaderboard</h2>
      <ol className="list-decimal list-inside">
        {entries.map((e, i) => (
          <li key={e.username} className="py-1">
            <strong>{e.username}</strong>: {e.streak} day{e.streak !== 1 ? 's' : ''}
          </li>
        ))}
      </ol>
    </div>
  )
}
