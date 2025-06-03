// src/pages/CreateTeamPage.tsx
import React, { useState } from "react"
import { useNavigate } from "react-router-dom"
import api from "../api/axios"

export const CreateTeamPage: React.FC = () => {
  const [teamName, setTeamName]     = useState<string>("")
  const [membersCSV, setMembersCSV] = useState<string>("")
  const [error, setError]           = useState<string | null>(null)
  const [successMsg, setSuccessMsg] = useState<string | null>(null)
  const [loading, setLoading]       = useState<boolean>(false)
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setSuccessMsg(null)

    const trimmedName = teamName.trim()
    if (!trimmedName) {
      setError("Team name cannot be empty.")
      return
    }

    const membersList = membersCSV
      .split(",")
      .map((u) => u.trim())
      .filter((u) => u.length > 0)

    setLoading(true)
    try {
      // POST to /api/teams/create/
      const response = await api.post("/teams/create/", {
        name: trimmedName,
        members: membersList,
      })

      if (response.status === 201) {
        setSuccessMsg(`Team "${trimmedName}" created!`)
        // Reset fields
        setTeamName("")
        setMembersCSV("")
        // Navigate to /team/<trimmedName> after a short delay (or immediately)
        navigate(`/team/${trimmedName}`)
      } else {
        setError(response.data.detail || "Failed to create team.")
      }
    } catch (err: any) {
      if (err.response) {
        setError(err.response.data?.detail || `Error ${err.response.status}`)
      } else {
        setError("Network error. Could not reach server.")
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-4 max-w-md mx-auto">
      <h2 className="text-2xl font-bold mb-4">Create New Team</h2>

      {error && (
        <div className="mb-2 text-red-600">{error}</div>
      )}
      {successMsg && (
        <div className="mb-2 text-green-600">{successMsg}</div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block mb-1 font-medium">Team Name</label>
          <input
            type="text"
            value={teamName}
            onChange={(e) => setTeamName(e.target.value)}
            className="w-full border px-2 py-1 rounded"
            placeholder="e.g. devops_squad"
          />
        </div>

        <div>
          <label className="block mb-1 font-medium">
            Members (comma-separated usernames)
          </label>
          <input
            type="text"
            value={membersCSV}
            onChange={(e) => setMembersCSV(e.target.value)}
            className="w-full border px-2 py-1 rounded"
            placeholder="alice, bob, charlie"
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? "Creating…" : "Create Team"}
        </button>
      </form>
    </div>
  )
}

export default CreateTeamPage
