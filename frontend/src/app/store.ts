import { configureStore } from '@reduxjs/toolkit'
import authReducer from '../features/authSlice'
import userReducer from '../features/auth/userSlice'

export const store = configureStore({
  reducer: {
    auth: authReducer,
    user: userReducer,
  },
})

// these types will be inferred from your store
export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch
