import { defineStore } from 'pinia'
import { api, setToken } from '../api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    loading: false,
    ready: false,
  }),
  getters: {
    isAuthenticated: (s) => !!s.user,
  },
  actions: {
    async bootstrap() {
      const token = localStorage.getItem('evacode_token')
      if (!token) {
        this.ready = true
        return
      }
      try {
        this.user = await api('/api/auth/me/')
      } catch {
        setToken('')
        this.user = null
      } finally {
        this.ready = true
      }
    },
    async login(username, password) {
      this.loading = true
      try {
        const data = await api('/api/auth/login/', {
          method: 'POST',
          body: JSON.stringify({ username, password }),
        })
        setToken(data.token)
        this.user = data.user
      } finally {
        this.loading = false
      }
    },
    async logout() {
      try {
        await api('/api/auth/logout/', { method: 'POST' })
      } catch {
        /* ignore */
      }
      setToken('')
      this.user = null
    },
  },
})
