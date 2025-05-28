import React from 'react'

const CLIENT_ID = import.meta.env.VITE_GH_CLIENT_ID
const REDIRECT_URI = import.meta.env.VITE_GH_REDIRECT_URI
const SCOPE = 'user:email'

export const LoginButton = () => {
    const url = new URL('https://github.com/login/oauth/authorize')
    url.searchParams.set('client_id', CLIENT_ID)
    url.searchParams.set('redirect_uri', REDIRECT_URI)
    url.searchParams.set('scope', SCOPE)

    return (
      <button
        onClick={() => window.location.href = url.toString()}
        className="px-4 py-2 bg-black text-white rounded"
      >
        Sign in with GitHub
      </button>
    )
  }