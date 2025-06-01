// src/pages/TeamLeaderboard.tsx
import React, { useState } from 'react'
import { CreateTeamForm } from '../components/CreateTeamForm'
import { useTeamXPsocket, XPEntry } from '../features/github/useTeamXPsocket'
import { useNavigate } from 'react-router-dom'
import { useAppSelector } from '../app/hooks'

export const TeamLeaderboard: React.FC = () => {
  // 1) Local state
  const [teamName, setTeamName] = useState<string>("")
  const [connectedTeam, setConnectedTeam] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const navigate = useNavigate()

  // 2) Pull accessToken from Redux (authSlice)
  const accessToken = useAppSelector(state => state.auth.accessToken)

  // 3) Call the hook UNCONDITIONALLY, passing either the real team or "".
  //    The hook itself will do nothing if teamName is an empty string.
  const data: XPEntry[] | null = useTeamXPsocket(connectedTeam || "")

  // 4) If not logged in, show a message.
  if (!accessToken) {
    return (
      <div className="p-4">
        <p className="text-red-600">You must be logged in to view team leaderboards.</p>
      </div>
    )
  }

  // 5) If no team has been chosen yet, show the create/join UI.
  if (!connectedTeam) {
    return (
      <div className="p-4 space-y-6">
        <CreateTeamForm
          accessToken={accessToken}
          onTeamCreated={(newTeam) => {
            setConnectedTeam(newTeam)
            setError(null)
          }}
        />

        <div className="p-4 border rounded">
          <h3 className="text-lg font-semibold mb-2">Join Existing Team</h3>

          <label className="block mb-2">
            Team Name
            <input
              type="text"
              value={teamName}
              onChange={(e) => setTeamName(e.target.value)}
              className="mt-1 block w-full border px-2 py-1 rounded"
              placeholder="Enter existing team name"
            />
          </label>

          <button
            onClick={async () => {
              const trimmed = teamName.trim()
              if (!trimmed) {
                setError("Please enter a team name.")
                return
              }
              try {
                const resp = await fetch(
                  `/api/teams/${trimmed}/leaderboard/`,
                  {
                    headers: {
                      Authorization: `Bearer ${accessToken}`,
                    },
                  }
                )
                if (resp.status === 200) {
                  setConnectedTeam(trimmed)
                  setError(null)
                } else if (resp.status === 403) {
                  setError("You are not a member of that team.")
                } else if (resp.status === 404) {
                  setError("Team not found.")
                } else {
                  setError("Could not join team (unexpected error).")
                }
              } catch {
                setError("Network error. Please try again.")
              }
            }}
            className="px-4 py-1 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
          >
            Join Team
          </button>

          {error && <p className="mt-2 text-red-600">{error}</p>}
        </div>
      </div>
    )
  }

  // 6) Once connectedTeam is set, show the live leaderboard.
  return (
    <div className="p-4">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-bold">🏆 Team: {connectedTeam}</h2>
        <button
          onClick={() => {
            setConnectedTeam(null)
            setTeamName("")
            setError(null)
          }}
          className="text-sm text-red-600 hover:underline"
        >
          ← Back
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
              <span>{entry.xp} XP</span>
            </li>
          ))}
        </ol>
      )}
    </div>
  )
}

export default TeamLeaderboard
