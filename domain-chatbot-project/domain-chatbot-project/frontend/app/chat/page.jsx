import { ProtectedRoute } from "@/components/auth/ProtectedRoute"
import { Header } from "@/components/common/Header"
import { ChatInterface } from "@/components/chat/ChatInterface"

export default function ChatPage() {
  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-background">
        <Header />
        <ChatInterface />
      </div>
    </ProtectedRoute>
  )
}
