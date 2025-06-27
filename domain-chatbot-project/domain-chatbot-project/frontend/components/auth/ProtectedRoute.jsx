"use client"

import { useAuth } from "@/context/AuthContext"
import { useRouter } from "next/navigation"
import { useEffect } from "react"
import { LoadingSpinner } from "@/components/common/LoadingSpinner"

export const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!loading && !user) {
      router.push("/auth/login")
    }
  }, [user, loading, router])

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner />
      </div>
    )
  }

  if (!user) {
    return null
  }

  return <>{children}</>
}
