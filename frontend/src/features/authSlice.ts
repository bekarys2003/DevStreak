// src/features/auth/authSlice.ts
import { createSlice, PayloadAction } from '@reduxjs/toolkit'

interface AuthState {
  accessToken: string | null
  refreshToken: string | null
}

// 🔍 Grab tokens synchronously from localStorage:
const saved = localStorage.getItem('authTokens')
let initial: AuthState = { accessToken: null, refreshToken: null }
if (saved) {
  try {
    const { access, refresh } = JSON.parse(saved)
    initial = { accessToken: access, refreshToken: refresh }
  } catch { /* ignore malformed JSON */ }
}

const authSlice = createSlice({
  name: 'auth',
  initialState: initial,
  reducers: {
    setCredentials(state, action: PayloadAction<{ access: string; refresh: string }>) {
      state.accessToken = action.payload.access
      state.refreshToken = action.payload.refresh
    },
    clearCredentials: () => initial,
  },
})

export const { setCredentials, clearCredentials } = authSlice.actions
export default authSlice.reducer
