// src/pages/DailyLeaderboard.tsx
import React from 'react'
import { useDailyCommitsSocket } from '../features/github/useDailyCommitsSocket'

interface CommitEntry {
  username: string
  commits: number
}

export const DailyLeaderboard: React.FC = () => {
  // Annotate the return from your hook so TS knows it’s CommitEntry[] | null
  const data: CommitEntry[] | null = useDailyCommitsSocket()

  if (!data) {
    return <p className="p-4">Loading daily commits leaderboard…</p>
  }

  return (
    <div className="p-4">
      <h2 className="text-2xl font-bold mb-4">🏆 Daily Commits Leaderboard</h2>
      <ol className="list-decimal pl-6 space-y-2">
        {data.map((entry, index) => (
          <li key={entry.username} className="flex justify-between">
            <span>
              {index + 1}. <strong>{entry.username}</strong>
            </span>
            <span>
              {entry.commits} commit{entry.commits !== 1 && 's'}
            </span>
          </li>
        ))}
      </ol>
    </div>
  )
}

export default DailyLeaderboard