"use client"

import { createContext, useContext, useState } from "react"

const ChatContext = createContext(undefined)

export const useChat = () => {
  const context = useContext(ChatContext)
  if (context === undefined) {
    throw new Error("useChat must be used within a ChatProvider")
  }
  return context
}

export const ChatProvider = ({ children }) => {
  const [selectedDomain, setSelectedDomain] = useState(null)
  const [conversations, setConversations] = useState([])
  const [currentConversation, setCurrentConversation] = useState(null)
  const [messages, setMessages] = useState([])
  const [isLoading, setIsLoading] = useState(false)

  return (
    <ChatContext.Provider
      value={{
        selectedDomain,
        setSelectedDomain,
        conversations,
        setConversations,
        currentConversation,
        setCurrentConversation,
        messages,
        setMessages,
        isLoading,
        setIsLoading,
      }}
    >
      {children}
    </ChatContext.Provider>
  )
}
