"use client"

import { useChat } from "@/context/ChatContext"
import { ConversationSidebar } from "./ConversationSidebar"
import { MessageList } from "./MessageList"
import { MessageInput } from "./MessageInput"
import { Badge } from "@/components/ui/badge"
import { Brain } from "lucide-react"

export const ChatInterface = () => {
  const { selectedDomain, currentConversation } = useChat()

  return (
    <div className="flex h-[calc(100vh-3.5rem)]">
      <ConversationSidebar />

      <div className="flex-1 flex flex-col">
        {selectedDomain && (
          <div className="border-b p-4 bg-muted/30">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-primary/10">
                <Brain className="h-5 w-5 text-primary" />
              </div>
              <div>
                <h2 className="font-semibold">{selectedDomain.name}</h2>
                <p className="text-sm text-muted-foreground">{selectedDomain.description}</p>
              </div>
              <Badge variant="secondary" className="ml-auto">
                {currentConversation ? "Active" : "Select Conversation"}
              </Badge>
            </div>
            {selectedDomain.systemPrompt && (
              <div className="mt-3 p-3 bg-blue-50 dark:bg-blue-950/20 rounded-lg border border-blue-200 dark:border-blue-800">
                <p className="text-sm text-blue-800 dark:text-blue-200">
                  <strong>System:</strong> {selectedDomain.systemPrompt}
                </p>
              </div>
            )}
          </div>
        )}

        <MessageList />
        <MessageInput />
      </div>
    </div>
  )
}
