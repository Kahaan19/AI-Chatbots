"use client"
import { createContext, useContext, useEffect, useState } from "react"
import { authService } from "@/services/authService"

const AuthContext = createContext(undefined)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const initAuth = async () => {
      const storedToken = localStorage.getItem("token")
      if (storedToken) {
        try {
          const userData = await authService.getMe(storedToken)
          setUser(userData)
          setToken(storedToken)
        } catch (error) {
          localStorage.removeItem("token")
          setUser(null)
          setToken(null)
        }
      }
      setLoading(false)
    }

    initAuth()
  }, [])

  const login = async (username, password) => {
    const response = await authService.login(username, password)
    setToken(response.access_token)
    localStorage.setItem("token", response.access_token)
    // Fetch user info after login
    const userData = await authService.getMe(response.access_token)
    setUser(userData)
  }

  const signup = async (formdata) => {
    const response = await authService.signup(formdata)
    // Optionally, redirect to login or auto-login
  }

  const logout = () => {
    setUser(null)
    setToken(null)
    localStorage.removeItem("token")
  }

  return (
    <AuthContext.Provider value={{ user, token, loading, login, signup, logout }}>
      {children}
    </AuthContext.Provider>
  )
}