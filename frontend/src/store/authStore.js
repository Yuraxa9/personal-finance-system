import { create } from 'zustand'
import * as authApi from '../api/auth'

const useAuthStore = create((set) => ({
  user: null,
  token: localStorage.getItem('token') ?? null,
  isAuthenticated: false,
  isLoading: false,

  loginAction: async (email, password) => {
    set({ isLoading: true })
    try {
      const { data } = await authApi.login(email, password)
      localStorage.setItem('token', data.access_token)
      const { data: user } = await authApi.getMe()
      set({ token: data.access_token, user, isAuthenticated: true })
    } finally {
      set({ isLoading: false })
    }
  },

  registerAction: async (full_name, email, password) => {
    set({ isLoading: true })
    try {
      await authApi.register(full_name, email, password)
      const { data: tokenData } = await authApi.login(email, password)
      localStorage.setItem('token', tokenData.access_token)
      const { data: user } = await authApi.getMe()
      set({ token: tokenData.access_token, user, isAuthenticated: true })
    } finally {
      set({ isLoading: false })
    }
  },

  logoutAction: () => {
    localStorage.removeItem('token')
    set({ user: null, token: null, isAuthenticated: false })
  },

  loadUser: async () => {
    const token = localStorage.getItem('token')
    if (!token) return
    set({ isLoading: true })
    try {
      const { data: user } = await authApi.getMe()
      set({ user, isAuthenticated: true })
    } catch {
      localStorage.removeItem('token')
      set({ token: null, isAuthenticated: false })
    } finally {
      set({ isLoading: false })
    }
  },
}))

export default useAuthStore
