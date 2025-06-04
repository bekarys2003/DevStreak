// src/pages/ProfilePage.tsx

import React, { useEffect, useState } from 'react'
import api from '../api/axios'

// (Optional) If you want to guard this page against unauthenticated access,
// you can import your selectors/hooks here. But in most setups, the <PrivateRoute>
// wrapper in App.tsx already protects this route.
import { useAppSelector } from '../app/hooks'

interface Profile {
  username:   string
  email:      string
  bio:        string
  avatar_url: string
  location:   string
}

const ProfilePage: React.FC = () => {
  const [profile, setProfile]           = useState<Profile | null>(null)
  const [formData, setFormData]         = useState({ bio: '', avatar_url: '', location: '' })
  const [loading, setLoading]           = useState(true)
  const [saving, setSaving]             = useState(false)
  const [error, setError]               = useState<string | null>(null)
  const [success, setSuccess]           = useState<string | null>(null)

  // If you already protect this route at the router level (with <PrivateRoute>),
  // you don’t strictly need the following. But if you want to redirect on missing token:
  // const accessToken = useAppSelector(state => state.auth.accessToken)
  // if (!accessToken) return <p className="p-4 text-red-600">You must be logged in.</p>

  useEffect(() => {
    // 1) Fetch the current profile
    api
      .get<Profile>('/profile/me/')
      .then(res => {
        setProfile(res.data)
        setFormData({
          bio:         res.data.bio,
          avatar_url:  res.data.avatar_url,
          location:    res.data.location,
        })
      })
      .catch(() => {
        setError('Failed to load profile.')
      })
      .finally(() => {
        setLoading(false)
      })
  }, [])

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setSuccess(null)
    setSaving(true)

    try {
      const res = await api.patch<Profile>('/profile/me/', formData)
      setProfile(res.data)
      setFormData({
        bio:         res.data.bio,
        avatar_url:  res.data.avatar_url,
        location:    res.data.location,
      })
      setSuccess('Profile updated!')
    } catch {
      setError('Failed to update profile.')
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return <p className="p-4">Loading profile…</p>
  }

  return (
    <div className="p-4 max-w-lg mx-auto">
      <h2 className="text-2xl font-bold mb-4">My Profile</h2>

      {error && <p className="mb-2 text-red-600">{error}</p>}
      {success && <p className="mb-2 text-green-600">{success}</p>}

      <div className="mb-6">
        <p>
          <strong>Username:</strong> {profile?.username}
        </p>
        <p>
          <strong>Email:</strong> {profile?.email}
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <label className="block">
          <span className="font-medium">Bio</span>
          <textarea
            name="bio"
            value={formData.bio}
            onChange={handleChange}
            className="mt-1 block w-full border rounded px-2 py-1"
            rows={3}
          />
        </label>

        <label className="block">
          <span className="font-medium">Avatar URL</span>
          <input
            type="text"
            name="avatar_url"
            value={formData.avatar_url}
            onChange={handleChange}
            className="mt-1 block w-full border rounded px-2 py-1"
            placeholder="https://example.com/avatar.jpg"
          />
        </label>

        <label className="block">
          <span className="font-medium">Location</span>
          <input
            type="text"
            name="location"
            value={formData.location}
            onChange={handleChange}
            className="mt-1 block w-full border rounded px-2 py-1"
            placeholder="e.g. Vancouver"
          />
        </label>

        <button
          type="submit"
          disabled={saving}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
        >
          {saving ? 'Saving…' : 'Save Changes'}
        </button>
      </form>
    </div>
  )
}

export default ProfilePage
