import { ProtectedRoute } from "@/components/auth/ProtectedRoute"
import { Header } from "@/components/common/Header"
import { ChatInterface } from "@/components/chat/ChatInterface"

export default function ChatConversationPage({ params }) {
  // You can pass params.conversationId to ChatInterface if needed
  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-background">
        <Header />
        <ChatInterface conversationId={params.conversationId} />
      </div>
    </ProtectedRoute>
  )
}