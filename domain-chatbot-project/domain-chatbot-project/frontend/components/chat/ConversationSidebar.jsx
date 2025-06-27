"use client"

import { useState, useEffect } from "react"
import { useChat } from "@/context/ChatContext"
import { chatService } from "@/services/chatService"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Badge } from "@/components/ui/badge"
import { LoadingSpinner } from "@/components/common/LoadingSpinner"
import { useToast } from "@/hooks/use-toast"
import { Plus, MessageSquare, Trash2, Calendar } from "lucide-react"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog"

export const ConversationSidebar = () => {
  const [loading, setLoading] = useState(true)
  const [creating, setCreating] = useState(false)
  const [conversationTitles, setConversationTitles] = useState({}) // Cache for conversation titles
  const { selectedDomain, conversations, setConversations, currentConversation, setCurrentConversation, setMessages } =
    useChat()
  const { toast } = useToast()

  useEffect(() => {
    if (selectedDomain) {
      fetchConversations()
    }
    // eslint-disable-next-line
  }, [selectedDomain])

  const fetchConversations = async () => {
    if (!selectedDomain) return

    try {
      setLoading(true)
      const conversationsData = await chatService.getConversations(selectedDomain.id)
      
      // Fetch first message for each conversation to generate titles and update lastMessage
      await fetchConversationTitles(conversationsData)
      
      // Remember last conversation per domain
      const lastId = localStorage.getItem(`lastConversation_${selectedDomain.id}`)
      const found = conversations.find(c => c.id === Number(lastId))
      if (found) {
        setCurrentConversation(found)
        const messages = await chatService.getMessages(found.id)
        setMessages(messages)
      } else if (conversations.length > 0) {
        setCurrentConversation(conversations[0])
        const messages = await chatService.getMessages(conversations[0].id)
        setMessages(messages)
      } else {
        setCurrentConversation(null)
        setMessages([])
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load conversations",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  // Fetch first message for each conversation to generate titles
  const fetchConversationTitles = async (conversationsData) => {
    const titles = {}
    const updatedConversations = [...conversationsData]
    
    // Process conversations in batches to avoid too many concurrent requests
    const batchSize = 5
    for (let i = 0; i < conversationsData.length; i += batchSize) {
      const batch = conversationsData.slice(i, i + batchSize)
      
      await Promise.all(
        batch.map(async (conversation, batchIndex) => {
          const actualIndex = i + batchIndex
          try {
            const messages = await chatService.getMessages(conversation.id)
            if (messages && messages.length > 0) {
              // Find first user message for title
              const firstUserMessage = messages.find(msg => msg.role === 'user' || msg.sender === 'user')
              if (firstUserMessage) {
                titles[conversation.id] = generateConversationTitle(firstUserMessage.content || firstUserMessage.message)
              } else {
                titles[conversation.id] = "New Conversation"
              }
              
              // Get last message for preview
              const lastMessage = messages[messages.length - 1]
              const lastMessageText = lastMessage.content || lastMessage.message || ""
              updatedConversations[actualIndex] = {
                ...conversation,
                lastMessage: lastMessageText.length > 100 ? lastMessageText.substring(0, 100) + "..." : lastMessageText
              }
            } else {
              titles[conversation.id] = "New Conversation"
              updatedConversations[actualIndex] = {
                ...conversation,
                lastMessage: "No messages yet"
              }
            }
          } catch (error) {
            console.error(`Failed to fetch messages for conversation ${conversation.id}:`, error)
            titles[conversation.id] = "New Conversation"
            updatedConversations[actualIndex] = {
              ...conversation,
              lastMessage: "Failed to load messages"
            }
          }
        })
      )
    }
    
    setConversationTitles(titles)
    setConversations(updatedConversations)
  }

  const createNewConversation = async () => {
    if (!selectedDomain) return

    try {
      setCreating(true)
      const newConversation = await chatService.createConversation(selectedDomain.id, "New Conversation")
      setConversations([newConversation, ...conversations])
      setCurrentConversation(newConversation)
      setMessages([])
      // Set title for new conversation
      setConversationTitles(prev => ({
        ...prev,
        [newConversation.id]: "New Conversation"
      }))
      // Remember this as last conversation for this domain
      localStorage.setItem(`lastConversation_${selectedDomain.id}`, newConversation.id)
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to create conversation",
        variant: "destructive",
      })
    } finally {
      setCreating(false)
    }
  }

  const selectConversation = async (conversation) => {
    try {
      setCurrentConversation(conversation)
      localStorage.setItem(`lastConversation_${selectedDomain.id}`, conversation.id)
      const messages = await chatService.getMessages(conversation.id)
      setMessages(messages)
      
      // Update conversation cache with last message for preview
      if (messages && messages.length > 0) {
        const lastMessage = messages[messages.length - 1]
        const lastMessageText = lastMessage.content || lastMessage.message || ""
        
        // Update conversations array with the last message
        setConversations(prev => prev.map(conv => 
          conv.id === conversation.id 
            ? { ...conv, lastMessage: lastMessageText.length > 100 ? lastMessageText.substring(0, 100) + "..." : lastMessageText }
            : conv
        ))
        
        // Update title if we don't have one yet
        if (!conversationTitles[conversation.id]) {
          const firstUserMessage = messages.find(msg => msg.role === 'user' || msg.sender === 'user')
          if (firstUserMessage) {
            const title = generateConversationTitle(firstUserMessage.content || firstUserMessage.message)
            setConversationTitles(prev => ({
              ...prev,
              [conversation.id]: title
            }))
          }
        }
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load messages",
        variant: "destructive",
      })
    }
  }

  const deleteConversation = async (conversationId) => {
    try {
      await chatService.deleteConversation(conversationId)
      const updatedConversations = conversations.filter((c) => c.id !== conversationId)
      setConversations(updatedConversations)

      // Remove from titles cache
      setConversationTitles(prev => {
        const updated = { ...prev }
        delete updated[conversationId]
        return updated
      })

      if (currentConversation?.id === conversationId) {
        setCurrentConversation(null)
        setMessages([])
        localStorage.removeItem(`lastConversation_${selectedDomain.id}`)
      }

      toast({
        title: "Success",
        description: "Conversation deleted",
      })
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to delete conversation",
        variant: "destructive",
      })
    }
  }

  // Fixed date formatting function with IST timezone
  const formatDate = (dateString) => {
    if (!dateString) return "Today"
    
    try {
      const date = new Date(dateString)
      
      // Check if date is valid
      if (isNaN(date.getTime())) {
        return "Today"
      }
      
      const now = new Date()
      
      // Get dates without time for comparison
      const dateOnly = new Date(date.getFullYear(), date.getMonth(), date.getDate())
      const todayOnly = new Date(now.getFullYear(), now.getMonth(), now.getDate())
      
      // Calculate difference in days
      const diffInDays = Math.floor((todayOnly - dateOnly) / (1000 * 60 * 60 * 24))
      
      if (diffInDays === 0) {
        return "Today"
      } else if (diffInDays === 1) {
        return "Yesterday"
      } else if (diffInDays < 7) {
        // Show day of week for this week
        return date.toLocaleDateString('en-IN', { 
          weekday: "long",
          timeZone: 'Asia/Kolkata'
        })
      } else if (diffInDays < 365) {
        // Show month and day for this year
        return date.toLocaleDateString('en-IN', { 
          month: "short", 
          day: "numeric",
          timeZone: 'Asia/Kolkata'
        })
      } else {
        // Show full date for older entries
        return date.toLocaleDateString('en-IN', { 
          year: "numeric",
          month: "short", 
          day: "numeric",
          timeZone: 'Asia/Kolkata'
        })
      }
    } catch (error) {
      console.error("Date formatting error:", error)
      return "Today"
    }
  }

  // Function to generate conversation title from first message
  const generateConversationTitle = (firstMessage) => {
    if (!firstMessage) return "New Conversation"
    
    // Clean the message and truncate
    const cleanMessage = firstMessage.trim()
    if (cleanMessage.length <= 50) {
      return cleanMessage
    }
    
    // Find a good break point (end of sentence or word)
    const truncated = cleanMessage.substring(0, 47)
    const lastSpace = truncated.lastIndexOf(' ')
    const lastPeriod = truncated.lastIndexOf('.')
    const lastQuestion = truncated.lastIndexOf('?')
    const lastExclamation = truncated.lastIndexOf('!')
    
    const breakPoint = Math.max(lastPeriod, lastQuestion, lastExclamation)
    
    if (breakPoint > 20) {
      return cleanMessage.substring(0, breakPoint + 1)
    } else if (lastSpace > 20) {
      return cleanMessage.substring(0, lastSpace) + "..."
    } else {
      return cleanMessage.substring(0, 47) + "..."
    }
  }

  // Function to get conversation display title
  const getConversationTitle = (conversation) => {
    // First check our cache
    const cachedTitle = conversationTitles[conversation.id]
    if (cachedTitle && cachedTitle !== "New Conversation") {
      return cachedTitle
    }
    
    // If conversation has a custom title that's not the default, use it
    if (conversation.title && conversation.title !== "New Conversation") {
      return conversation.title
    }
    
    // If there's a first message, generate title from it
    if (conversation.firstMessage) {
      return generateConversationTitle(conversation.firstMessage)
    }
    
    // If there's a last message, use that
    if (conversation.lastMessage) {
      return generateConversationTitle(conversation.lastMessage)
    }
    
    return cachedTitle || "New Conversation"
  }

  return (
    <div className="w-80 border-r bg-muted/10 flex flex-col h-full">
      <div className="p-4 border-b">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-semibold">Conversations</h3>
          <Button size="sm" onClick={createNewConversation} disabled={creating || !selectedDomain}>
            {creating ? <LoadingSpinner className="mr-2" size="sm" /> : <Plus className="mr-2 h-4 w-4" />}
            New
          </Button>
        </div>

        {selectedDomain && (
          <Badge variant="outline" className="w-full justify-center">
            {selectedDomain.name}
          </Badge>
        )}
      </div>

      <ScrollArea className="flex-1">
        {loading ? (
          <div className="flex items-center justify-center p-8">
            <LoadingSpinner />
          </div>
        ) : conversations.length === 0 ? (
          <div className="p-4 text-center text-muted-foreground">
            <MessageSquare className="h-8 w-8 mx-auto mb-2 opacity-50" />
            <p className="text-sm">No conversations yet</p>
            <p className="text-xs">Start a new conversation to begin</p>
          </div>
        ) : (
          <div className="p-2 space-y-2">
            {conversations.map((conversation) => (
              <div
                key={conversation.id}
                className={`group relative p-3 rounded-lg cursor-pointer transition-colors ${
                  currentConversation?.id === conversation.id
                    ? "bg-primary/10 border border-primary/20"
                    : "hover:bg-muted/50"
                }`}
                onClick={() => selectConversation(conversation)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <h4 className="font-medium text-sm truncate">{getConversationTitle(conversation)}</h4>
                    <p className="text-xs text-muted-foreground truncate mt-1">
                      {conversation.lastMessage || "No messages yet"}
                    </p>
                    <div className="flex items-center mt-2 text-xs text-muted-foreground">
                      <Calendar className="h-3 w-3 mr-1" />
                      {formatDate(conversation.updatedAt || conversation.createdAt || conversation.created_at)}
                    </div>
                  </div>

                  <AlertDialog>
                    <AlertDialogTrigger asChild>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-6 w-6 opacity-0 group-hover:opacity-100 transition-opacity"
                        onClick={(e) => e.stopPropagation()}
                      >
                        <Trash2 className="h-3 w-3" />
                      </Button>
                    </AlertDialogTrigger>
                    <AlertDialogContent>
                      <AlertDialogHeader>
                        <AlertDialogTitle>Delete Conversation</AlertDialogTitle>
                        <AlertDialogDescription>
                          Are you sure you want to delete this conversation? This action cannot be undone.
                        </AlertDialogDescription>
                      </AlertDialogHeader>
                      <AlertDialogFooter>
                        <AlertDialogCancel>Cancel</AlertDialogCancel>
                        <AlertDialogAction
                          onClick={() => deleteConversation(conversation.id)}
                          className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                        >
                          Delete
                        </AlertDialogAction>
                      </AlertDialogFooter>
                    </AlertDialogContent>
                  </AlertDialog>
                </div>
              </div>
            ))}
          </div>
        )}
      </ScrollArea>
    </div>
  )
} 