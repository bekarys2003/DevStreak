import React from 'react'
import { useAppSelector } from '../app/hooks'
import { useFetchUser } from '../features/auth/useFetchUser'
import { LogoutButton } from '../features/auth/LogoutButton'
const Home: React.FC = () => {
  useFetchUser()
  const profile = useAppSelector(state => state.user.user)
  const username = profile?.username
  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold">Welcome to DevStreak!</h1>
      {username ? (
        <>
            <p>
            You’re signed in as <strong>{username}</strong> 🎉
            </p>
            <LogoutButton />
        </>
      ) : (
        <p>Loading your profile…</p>
      )}
    </div>
  )
}

export default Home