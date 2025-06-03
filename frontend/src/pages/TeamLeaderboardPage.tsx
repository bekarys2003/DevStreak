// src/pages/TeamLeaderboardPage.tsx
import React, { useState } from "react"
import { useParams, useNavigate } from "react-router-dom"
import { useAppSelector } from "../app/hooks"
import { useTeamXPsocket, XPEntry } from "../features/github/useTeamXPsocket"

export const TeamLeaderboardPage: React.FC = () => {
  // 1) Get the `teamName` from the URL (e.g. /team/my_team)
  const { teamName } = useParams<{ teamName: string }>()
  const navigate     = useNavigate()

  // 2) If not logged in, show a message
  const accessToken = useAppSelector(state => state.auth.accessToken)
  if (!accessToken) {
    return (
      <div className="p-4">
        <p className="text-red-600">You must be logged in to see this page.</p>
      </div>
    )
  }

  // 3) Use the WebSocket hook to subscribe to this team’s XP
  //    (the hook does nothing if `teamName` is undefined or empty)
  const data: XPEntry[] | null = useTeamXPsocket(teamName || "")

  return (
    <div className="p-4">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-bold">🏆 Team: {teamName}</h2>
        <button
          onClick={() => navigate("/team/create")}
          className="text-sm text-red-600 hover:underline"
        >
          ← Create or join a different team
        </button>
      </div>

      {data === null ? (
        <p>Loading team leaderboard…</p>
      ) : data.length === 0 ? (
        <p>No entries for today (or team has no members).</p>
      ) : (
        <ol className="list-decimal pl-6 space-y-2">
          {data.map((entry, idx) => (
            <li key={entry.username} className="flex justify-between">
              <span>
                {idx + 1}. <strong>{entry.username}</strong>
              </span>
              <span className="ml-2">
                {entry.xp} XP
              </span>
            </li>
          ))}
        </ol>
      )}
    </div>
  )
}

export default TeamLeaderboardPage
