// src/pages/DailyLeaderboard.tsx
import React from 'react'
import { useDailyCommitsSocket } from '../features/github/useDailyCommitsSocket'

interface LeaderboardEntry {
  username: string
  xp: number
}

const DailyLeaderboard: React.FC = () => {
  const data: LeaderboardEntry[] | null = useDailyCommitsSocket()

  if (!data) {
    return <p className="p-4">Loading daily XP leaderboard…</p>
  }

  return (
    <div className="p-4">
      <h2 className="text-2xl font-bold mb-4">🏆 Daily XP Leaderboard</h2>
      <ol className="list-decimal pl-6 space-y-2">
        {data.map((entry, index) => (
          <li key={entry.username} className="flex justify-between">
            <span>
              {index + 1}. <strong>{entry.username}</strong>
            </span>
            <span>
              {entry.xp} XP
            </span>
          </li>
        ))}
      </ol>
    </div>
  )
}

export default DailyLeaderboard
