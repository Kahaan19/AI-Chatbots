"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/context/AuthContext"
import { LoadingSpinner } from "@/components/common/LoadingSpinner"

export default function HomePage() {
  const { user, loading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!loading) {
      if (user) {
        router.push("/dashboard")
      } else {
        router.push("/auth/login")
      }
    }
  }, [user, loading, router])

  return (
    <div className="flex items-center justify-center min-h-screen">
      <LoadingSpinner size="lg" />
    </div>
  )
}
