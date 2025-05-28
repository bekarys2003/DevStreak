// src/features/auth/useFetchUser.ts
import { useEffect } from 'react'
import api from '../../api/axios'
import { useAppDispatch } from '../../app/hooks'
import { setUser, User } from './userSlice'

export const useFetchUser = () => {
  const dispatch = useAppDispatch()

  useEffect(() => {
    api.get<User>('/users/me/')
       .then(res => dispatch(setUser(res.data)))
       .catch(() => {
         // e.g. token expired → clear credentials
       })
  }, [dispatch])
}
