import { apiService } from "./api"

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

class ChatService {
  async getDomains() {
    return apiService.get("/api/domains")
  }

  async getConversations(domainId) {
    const endpoint = domainId
      ? `/api/conversations?domain_id=${domainId}`
      : "/api/conversations"
    return apiService.get(endpoint)
  }

  async createConversation(domainId, title) {
    return apiService.post("/api/conversations", { domain_id: domainId, title })
  }

  async deleteConversation(conversationId) {
    return apiService.delete(`/api/conversations/${conversationId}`)
  }

  async getMessages(conversationId) {
  const response = await apiService.get(`/api/conversations/${conversationId}/messages`)
  return response.messages || response
}

  async sendMessage(conversationId, message) {
    return apiService.post(`/api/chat/${conversationId}`, { message })
  }

  // Streaming AI response (now uses full backend URL)
  async streamAIResponse(conversationId, message, length = "medium", onChunk) {
    const response = await fetch(
      `${API_BASE_URL}/api/chat/${conversationId}/stream?length=${length}`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
        body: JSON.stringify({ message }),
      }
    )

    if (!response.body) throw new Error("No response body")

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let done = false

    while (!done) {
      const { value, done: doneReading } = await reader.read()
      done = doneReading
      if (value) {
        const chunk = decoder.decode(value)
        if (onChunk) onChunk(chunk)
      }
    }
  }
}

export const chatService = new ChatService()