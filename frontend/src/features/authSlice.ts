import { createSlice, PayloadAction } from '@reduxjs/toolkit'

interface AuthState {
  accessToken: string | null
  refreshToken: string | null
}

const initialState: AuthState = {
  accessToken: null,
  refreshToken: null,
}

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    setCredentials: (
      _,
      { payload }: PayloadAction<{ access: string; refresh: string }>
    ) => ({
      accessToken: payload.access,
      refreshToken: payload.refresh,
    }),
    clearCredentials: () => initialState,
  },
})

export const { setCredentials, clearCredentials } = authSlice.actions
export default authSlice.reducer
