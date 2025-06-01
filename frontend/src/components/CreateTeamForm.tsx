// src/components/CreateTeamForm.tsx
import React, { useState } from 'react'

interface CreateTeamFormProps {
  onTeamCreated: (teamName: string) => void
  accessToken: string
}

export const CreateTeamForm: React.FC<CreateTeamFormProps> = ({
  onTeamCreated,
  accessToken,
}) => {
  const [teamName, setTeamName] = useState<string>("")
  const [membersCSV, setMembersCSV] = useState<string>("")
  const [error, setError] = useState<string | null>(null)
  const [successMsg, setSuccessMsg] = useState<string | null>(null)
  const [loading, setLoading] = useState<boolean>(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setSuccessMsg(null)

    const trimmedName = teamName.trim()
    if (!trimmedName) {
      setError("Team name cannot be empty.")
      return
    }

    // Split on commas, trim whitespace, and filter out empty strings:
    const membersList = membersCSV
      .split(",")
      .map((u) => u.trim())
      .filter((u) => u.length > 0)

    setLoading(true)
    try {
      const resp = await fetch("/api/teams/create/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${accessToken}`,
        },
        body: JSON.stringify({
          name: trimmedName,
          members: membersList,
        }),
      })

      if (resp.status === 201) {
        setSuccessMsg(`Team "${trimmedName}" created!`)
        setTeamName("")
        setMembersCSV("")
        onTeamCreated(trimmedName)
      } else {
        const data = await resp.json()
        setError(data.detail || "Failed to create team.")
      }
    } catch (err: any) {
      console.error(err)
      setError("Network error. Could not reach server.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="p-4 border rounded-md">
      <h3 className="text-lg font-semibold mb-2">Create New Team</h3>
      {error && (
        <div className="mb-2 text-red-600">
          {error}
        </div>
      )}
      {successMsg && (
        <div className="mb-2 text-green-600">
          {successMsg}
        </div>
      )}

      <label className="block mb-1">
        Team Name
        <input
          type="text"
          value={teamName}
          onChange={(e) => setTeamName(e.target.value)}
          className="mt-1 block w-full border px-2 py-1 rounded"
          placeholder="e.g. devops_squad"
        />
      </label>

      <label className="block mb-1">
        Members (comma‐separated usernames)
        <input
          type="text"
          value={membersCSV}
          onChange={(e) => setMembersCSV(e.target.value)}
          className="mt-1 block w-full border px-2 py-1 rounded"
          placeholder="alice, bob, charlie"
        />
      </label>

      <button
        type="submit"
        disabled={loading}
        className="mt-3 px-4 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
      >
        {loading ? "Creating…" : "Create Team"}
      </button>
    </form>
  )
}
