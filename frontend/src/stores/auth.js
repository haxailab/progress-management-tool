import { defineStore } from 'pinia'
import axios from 'axios'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: localStorage.getItem('token') || null
  }),

  getters: {
    isAuthenticated: (state) => !!state.token,
    currentUser: (state) => state.user
  },

  actions: {
    async login(email, password) {
      try {
        const response = await axios.post('/api/auth/login', { email, password })
        this.token = response.data.access_token
        localStorage.setItem('token', this.token)
        axios.defaults.headers.common['Authorization'] = `Bearer ${this.token}`
        await this.fetchUser()
        return true
      } catch (error) {
        console.error('Login failed:', error)
        throw error
      }
    },

    async register(userData) {
      try {
        await axios.post('/api/auth/register', userData)
        return true
      } catch (error) {
        console.error('Registration failed:', error)
        throw error
      }
    },

    async fetchUser() {
      try {
        const response = await axios.get('/api/auth/me')
        this.user = response.data
      } catch (error) {
        console.error('Failed to fetch user:', error)
        this.logout()
      }
    },

    logout() {
      this.user = null
      this.token = null
      localStorage.removeItem('token')
      delete axios.defaults.headers.common['Authorization']
    },

    initAuth() {
      if (this.token) {
        axios.defaults.headers.common['Authorization'] = `Bearer ${this.token}`
        this.fetchUser()
      }
    }
  }
})
