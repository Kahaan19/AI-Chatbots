import { ProtectedRoute } from "@/components/auth/ProtectedRoute"
import { Header } from "@/components/common/Header"
import { DomainSelector } from "@/components/domain/DomainSelector"

export default function DashboardPage() {
  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-background">
        <Header />
        <main className="container mx-auto py-8">
          <DomainSelector />
        </main>
      </div>
    </ProtectedRoute>
  )
}
