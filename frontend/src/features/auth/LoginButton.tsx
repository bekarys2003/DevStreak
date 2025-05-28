import React from 'react'

const CLIENT_ID = import.meta.env.VITE_GH_CLIENT_ID
const REDIRECT_URI = `${window.location.origin}/oauth/callback`
const SCOPE = 'user:email'

export const LoginButton = () => {
  const githubUrl =
    `https://github.com/login/oauth/authorize` +
    `?client_id=${CLIENT_ID}` +
    `&scope=${encodeURIComponent(SCOPE)}` +
    `&redirect_uri=${encodeURIComponent(REDIRECT_URI)}`

  return (
    <button
      onClick={() => { window.location.href = githubUrl }}
      className="px-4 py-2 bg-black text-white rounded"
    >
      Sign in with GitHub
    </button>
  )
}
