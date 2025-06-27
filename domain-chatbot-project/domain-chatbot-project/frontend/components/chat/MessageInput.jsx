"use client"

import { useState, useRef } from "react"
import { useChat } from "@/context/ChatContext"
import { chatService } from "@/services/chatService"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { useToast } from "@/hooks/use-toast"
import { Send } from "lucide-react"

const LENGTH_OPTIONS = [
  { value: "short", label: "Short" },
  { value: "medium", label: "Medium" },
  { value: "long", label: "Long" },
]

export const MessageInput = () => {
  const [input, setInput] = useState("")
  const [length, setLength] = useState("medium")
  const textareaRef = useRef(null)
  const { currentConversation, messages, setMessages, isLoading, setIsLoading } = useChat()
  const { toast } = useToast()

  const safeMessages = Array.isArray(messages) ? messages : []

  const handleSubmit = async () => {
    if (!input.trim() || !currentConversation || isLoading) return

    setInput("")
    setIsLoading(true)

    // Add user message immediately
    const userMessage = {
      id: Date.now(),
      role: "user",
      content: input.trim(),
      timestamp: new Date().toISOString(),
    }
    setMessages((prev) => [...(Array.isArray(prev) ? prev : []), userMessage])

    // Add placeholder for streaming AI message
    const aiMessageId = Date.now() + 1
    setMessages((prev) => [
      ...(Array.isArray(prev) ? prev : []),
      { id: aiMessageId, role: "assistant", content: "", timestamp: new Date().toISOString() },
    ])

    try {
      await chatService.streamAIResponse(
        currentConversation.id,
        input.trim(),
        length,
        (chunk) => {
          setMessages((prev) => {
            const updated = [...prev]
            const aiIndex = updated.findIndex((m) => m.id === aiMessageId)
            if (aiIndex !== -1) {
              updated[aiIndex] = {
                ...updated[aiIndex],
                content: (updated[aiIndex].content || "") + chunk,
              }
            }
            return updated
          })
        }
      )
      const latestMessages = await chatService.getMessages(currentConversation.id)
      setMessages(latestMessages)
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to send message",
        variant: "destructive",
      })
      // Remove the placeholder AI message on error
      setMessages((prev) => prev.filter((m) => m.id !== aiMessageId))
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  const adjustTextareaHeight = () => {
    const textarea = textareaRef.current
    if (textarea) {
      textarea.style.height = "auto"
      textarea.style.height = `${Math.min(textarea.scrollHeight, 120)}px`
    }
  }

  return (
    <div className="border-t bg-background p-4">
      <div className="flex gap-2 items-end">
        <div className="flex-1">
          <Textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => {
              setInput(e.target.value)
              adjustTextareaHeight()
            }}
            onKeyDown={handleKeyDown}
            placeholder={
              currentConversation
                ? "Type your message... (Enter to send, Shift+Enter for new line)"
                : "Select a conversation to start chatting"
            }
            disabled={!currentConversation || isLoading}
            className="min-h-[40px] max-h-[120px] resize-none"
            rows={1}
          />
        </div>
        <select
          value={length}
          onChange={(e) => setLength(e.target.value)}
          disabled={isLoading}
          className="border rounded px-2 py-1 text-sm bg-background"
        >
          {LENGTH_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
        <Button
          onClick={handleSubmit}
          disabled={!input.trim() || !currentConversation || isLoading}
          size="icon"
          className="h-10 w-10"
        >
          <Send className="h-4 w-4" />
        </Button>
      </div>
    </div>
  )
}