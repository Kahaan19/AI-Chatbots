"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { useChat } from "@/context/ChatContext"
import { chatService } from "@/services/chatService"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { LoadingSpinner } from "@/components/common/LoadingSpinner"
import { useToast } from "@/hooks/use-toast"
import { Brain, DollarSign, Scale, Music, Code, Heart, BookOpen, Briefcase } from "lucide-react"

const iconMap = {
  brain: Brain,
  finance: DollarSign,
  law: Scale,
  entertainment: Music,
  technical: Code,
  psychology: Heart,
  education: BookOpen,
  business: Briefcase,
}

export const DomainSelector = () => {
  const [domains, setDomains] = useState([])
  const [loading, setLoading] = useState(true)
  const { setSelectedDomain } = useChat()
  const { toast } = useToast()
  const router = useRouter()

  useEffect(() => {
    const fetchDomains = async () => {
      try {
        const domainsData = await chatService.getDomains()
        setDomains(domainsData)
      } catch (error) {
        toast({
          title: "Error",
          description: "Failed to load domains",
          variant: "destructive",
        })
      } finally {
        setLoading(false)
      }
    }

    fetchDomains()
  }, [toast])

  const handleDomainSelect = (domain) => {
    setSelectedDomain(domain)
    router.push("/chat")
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="text-center space-y-2">
        <h2 className="text-3xl font-bold tracking-tight">Choose Your Domain</h2>
        <p className="text-muted-foreground">Select a specialized AI assistant to help with your specific needs</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {domains.map((domain) => {
          const IconComponent = iconMap[domain.icon] || Brain

          return (
            <Card
              key={domain.id}
              className="cursor-pointer transition-all hover:shadow-lg hover:scale-105 border-2 hover:border-primary/50"
              onClick={() => handleDomainSelect(domain)}
            >
              <CardHeader className="text-center">
                <div className="mx-auto mb-4 p-3 rounded-full bg-primary/10 w-fit">
                  <IconComponent className="h-8 w-8 text-primary" />
                </div>
                <CardTitle className="text-xl">{domain.name}</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription className="text-center text-sm leading-relaxed">{domain.description}</CardDescription>
                {domain.systemPrompt && (
                  <Badge variant="secondary" className="mt-3 w-full justify-center">
                    Specialized Assistant
                  </Badge>
                )}
              </CardContent>
            </Card>
          )
        })}
      </div>
    </div>
  )
}
