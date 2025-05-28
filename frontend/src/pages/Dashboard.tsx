// src/pages/Dashboard.tsx
import React from 'react'
import { useContributions } from '../features/github/useContributions'

const Dashboard: React.FC = () => {
  const { data, error } = useContributions()

  if (error) return <p className="text-red-600">Error: {error}</p>
  if (!data) return <p>Loading today’s contributions…</p>

  return (
    <div className="p-4">
      <h2 className="text-xl font-bold mb-4">Today’s GitHub Activity</h2>
      <ul className="list-disc pl-5 space-y-1">
        <li>Commits: {data.commits}</li>
        <li>Pull Requests: {data.pull_requests}</li>
        <li>Reviews: {data.reviews}</li>
      </ul>
    </div>
  )
}

export default Dashboard
