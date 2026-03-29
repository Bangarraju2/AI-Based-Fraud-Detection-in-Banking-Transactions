import React, { createContext, useContext, useState, useEffect } from 'react'
import { authAPI } from '../services/api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('access_token')
    const savedUser = localStorage.getItem('user')
    if (token && savedUser) {
      try {
        setUser(JSON.parse(savedUser))
      } catch { /* ignore */ }
    }
    setLoading(false)
  }, [])

  const login = async (email, password) => {
    try {
      const { data } = await authAPI.login({ email, password })
      localStorage.setItem('access_token', data.access_token)
      localStorage.setItem('refresh_token', data.refresh_token)
      localStorage.setItem('user', JSON.stringify(data.user))
      setUser(data.user)
      return data
    } catch (err) {
      // Automatic fallback for demo purposes if backend is unreachable
      if (!err.response || err.code === 'ECONNREFUSED' || err.message.includes('Network Error')) {
        console.warn('Backend unreachable. Falling back to Mock Mode for demo.')
        const mockUser = {
          email: email || 'admin@fraudshield.ai',
          full_name: 'Demo Analyst (Mock)',
          role: 'admin',
          is_mock: true
        }
        localStorage.setItem('access_token', 'mock_token')
        localStorage.setItem('user', JSON.stringify(mockUser))
        setUser(mockUser)
        return { user: mockUser, is_mock: true }
      }
      throw err
    }
  }

  const loginWithGoogle = async () => {
    setLoading(true)
    // 1. Simulate Google OAuth "Popup/Redirect" delay
    await new Promise(resolve => setTimeout(resolve, 1200))

    // 2. Check if backend is alive (optional, for demo to know if it's "Live" or "Mock")
    let isLive = false
    try {
      const response = await authAPI.health().catch(() => null)
      isLive = !!response
    } catch { /* stay mock */ }

    const mockUser = {
      email: 'google.user@example.com',
      full_name: 'Google User',
      role: 'analyst',
      is_mock: !isLive,
      avatar: 'https://lh3.googleusercontent.com/a/ACg8ocL...' // Mock avatar link
    }

    localStorage.setItem('access_token', isLive ? 'live_google_token' : 'mock_google_token')
    localStorage.setItem('user', JSON.stringify(mockUser))
    setUser(mockUser)
    setLoading(false)
    return { user: mockUser, is_mock: !isLive }
  }

  const register = async (email, fullName, password) => {
    try {
      const { data } = await authAPI.register({
        email,
        full_name: fullName,
        password,
        role: 'analyst',
      })
      localStorage.setItem('access_token', data.access_token)
      localStorage.setItem('refresh_token', data.refresh_token)
      localStorage.setItem('user', JSON.stringify(data.user))
      setUser(data.user)
      return data
    } catch (err) {
      if (!err.response || err.code === 'ECONNREFUSED' || err.message.includes('Network Error')) {
        const mockUser = { email, full_name: fullName, role: 'analyst', is_mock: true }
        setUser(mockUser)
        localStorage.setItem('user', JSON.stringify(mockUser))
        return { user: mockUser }
      }
      throw err
    }
  }

  const logout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, loginWithGoogle, register, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) throw new Error('useAuth must be used within AuthProvider')
  return context
}
