"use client"

import { useEffect, useRef } from "react"
import { useChat } from "@/context/ChatContext"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Card } from "@/components/ui/card"
import { LoadingSpinner } from "@/components/common/LoadingSpinner"
import { Bot, User, Camera, Cpu } from "lucide-react"

export const MessageList = () => {
  const { messages, isLoading, currentConversation } = useChat()
  const messagesEndRef = useRef(null)
  const safeMessages = Array.isArray(messages) ? messages : []

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages, isLoading])

  // Safe date formatting
  const formatTime = (timestamp) => {
    if (!timestamp) return ""
    const date = new Date(timestamp)
    return isNaN(date) ? "" : date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
  }

  // Helper to extract image URL and text
  const renderMessageContent = (content) => {
    if (content && content.includes("[image]")) {
      const match = content.match(/\[image\](.*?)\[\/image\]/)
      const imageUrl = match?.[1]
      const text = content.replace(/\[image\].*?\[\/image\]/, "").trim()
      return (
        <>
          {imageUrl && (
            <div className="mb-3">
              <img
                src={imageUrl}
                alt="Generated"
                className="rounded-lg border shadow-sm max-w-full hover:shadow-md transition-shadow duration-200"
                style={{ maxHeight: 400, width: 'auto' }}
                onError={(e) => {
                  e.target.style.display = 'none'
                  console.error('Failed to load image:', imageUrl)
                }}
              />
            </div>
          )}
          {text && <div className="whitespace-pre-wrap">{text}</div>}
        </>
      )
    }
    return <div className="whitespace-pre-wrap">{content}</div>
  }

  // Get domain-specific hint
  const getDomainHint = (domainName) => {
    const hints = {
      entertainment: {
        icon: <Camera className="h-4 w-4" />,
        text: "🎨 Image generation available! Try: 'Generate an image of a fantasy landscape' or 'Create art of a futuristic city'",
        color: "bg-purple-100 text-purple-800 border-purple-200"
      },
      technical: {
        icon: <Cpu className="h-4 w-4" />,
        text: "🛠️ Technical diagrams available! Try: 'Generate a network diagram' or 'Create a technical illustration of...'",
        color: "bg-blue-100 text-blue-800 border-blue-200"
      }
    }
    return hints[domainName?.toLowerCase()]
  }

  const currentDomainHint = getDomainHint(currentConversation?.domain?.name)

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4">
      {/* Show image generation hint for entertainment and technical domains */}
      {currentDomainHint && (
        <div className={`mb-4 p-3 rounded-lg border flex items-center gap-2 ${currentDomainHint.color}`}>
          {currentDomainHint.icon}
          <span className="text-sm font-medium">{currentDomainHint.text}</span>
        </div>
      )}
      
      {safeMessages.length === 0 && !isLoading ? (
        <div className="flex items-center justify-center h-full text-center">
          <div className="space-y-2">
            <Bot className="h-12 w-12 mx-auto text-muted-foreground" />
            <h3 className="text-lg font-medium">Start a conversation</h3>
            <p className="text-muted-foreground">Send a message to begin chatting with your AI assistant</p>
            {currentDomainHint && (
              <p className="text-sm text-muted-foreground mt-2">
                💡 This domain supports image generation!
              </p>
            )}
          </div>
        </div>
      ) : (
        <>
          {safeMessages.map((message) => (
            <div key={message.id} className={`flex gap-3 ${message.role === "user" ? "justify-end" : "justify-start"}`}>
              {message.role === "assistant" && (
                <Avatar className="h-8 w-8 mt-1 flex-shrink-0">
                  <AvatarFallback>
                    <Bot className="h-4 w-4" />
                  </AvatarFallback>
                </Avatar>
              )}

              <div className={`max-w-[75%] ${message.role === "user" ? "order-1" : ""}`}>
                <Card className={`p-3 ${message.role === "user" ? "bg-primary text-primary-foreground" : "bg-muted"}`}>
                  <div className="text-sm leading-relaxed">
                    {renderMessageContent(message.content)}
                  </div>
                </Card>
                <div
                  className={`text-xs text-muted-foreground mt-1 ${
                    message.role === "user" ? "text-right" : "text-left"
                  }`}
                >
                  {formatTime(message.timestamp || message.created_at)}
                </div>
              </div>

              {message.role === "user" && (
                <Avatar className="h-8 w-8 mt-1 flex-shrink-0">
                  <AvatarFallback>
                    <User className="h-4 w-4" />
                  </AvatarFallback>
                </Avatar>
              )}
            </div>
          ))}

          {isLoading && (
            <div className="flex gap-3 justify-start">
              <Avatar className="h-8 w-8 mt-1">
                <AvatarFallback>
                  <Bot className="h-4 w-4" />
                </AvatarFallback>
              </Avatar>
              <Card className="p-3 bg-muted">
                <div className="flex items-center gap-2">
                  <LoadingSpinner size="sm" />
                  <span className="text-sm text-muted-foreground">
                    {currentDomainHint ? "Generating response..." : "Thinking..."}
                  </span>
                </div>
              </Card>
            </div>
          )}
        </>
      )}
      <div ref={messagesEndRef} />
    </div>
  )
}