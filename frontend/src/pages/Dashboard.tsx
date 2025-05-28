import React from 'react'
import { useContributions } from '../features/github/useContributions'
import { useStreak } from '../features/github/useStreak'

const Dashboard: React.FC = () => {
  const { data: contribs, error: cErr } = useContributions()
  const { streak, error: sErr }        = useStreak()

  if (cErr) return <p className="text-red-600">{cErr}</p>
  if (sErr) return <p className="text-red-600">{sErr}</p>
  if (!contribs || streak === null) return <p>Loading dashboard…</p>

  return (
    <div className="p-4 space-y-6">
      <section>
        <h2 className="text-xl font-bold mb-2">Today’s GitHub Activity</h2>
        <ul className="list-disc pl-5">
          <li>Commits: {contribs.commits}</li>
          <li>Pull Requests: {contribs.pull_requests}</li>
          <li>Reviews: {contribs.reviews}</li>
        </ul>
      </section>

      <section>
        <h2 className="text-xl font-bold mb-2">Current Streak</h2>
        <p className="text-2xl">{streak} day{streak !== 1 && 's'}</p>
      </section>
    </div>
  )
}

export default Dashboard
