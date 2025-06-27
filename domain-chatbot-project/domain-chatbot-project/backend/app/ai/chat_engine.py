from typing import List, Dict, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import BaseMessage, HumanMessage, SystemMessage, AIMessage
from langchain.memory import ConversationBufferWindowMemory
from langchain.chains import ConversationChain
from langchain.prompts import PromptTemplate
import os
import google.generativeai as genai
import asyncio

class DomainChatEngine:
    def __init__(self):
        # Configure Google Gemini API
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash-preview-05-20",
            temperature=0.7,
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            convert_system_message_to_human=True
        )
        
        # Domain-specific conversation chains
        self.domain_chains = {}
        self._initialize_domain_chains()
    
    def _initialize_domain_chains(self):
        """Initialize conversation chains for each domain"""
        
        # Modified templates for Gemini (no separate system role)
        domain_templates = {
            "stock": """You are a professional financial advisor. 
            
            Previous conversation:
            {history}
            
            Human: {input}
            
            Provide financial insights while reminding users this isn't personalized financial advice. Be professional and informative.
            
            Financial Advisor:""",
            
            "law": """You are a legal information assistant.
            
            Previous conversation:
            {history}
            
            Human: {input}
            
            Provide legal information while clarifying this isn't legal advice. Be helpful and informative.
            
            Legal Assistant:""",
            
            "entertainment": """You are an entertainment expert.
            
            Previous conversation:
            {history}
            
            Human: {input}
            
            Share engaging insights about movies, music, games, and pop culture. Be enthusiastic and knowledgeable.
            
            Entertainment Expert:""",
            
            "psychology": """You are a psychology educator.
            
            Previous conversation:
            {history}
            
            Human: {input}
            
            Provide psychological insights while noting this isn't therapy or medical advice. Be supportive and educational.
            
            Psychology Expert:""",
            
            "technical": """You are a senior software engineer.
            
            Previous conversation:
            {history}
            
            Human: {input}
            
            Provide technical solutions with clear explanations and working code examples. Be precise and helpful.
            
            Technical Expert:"""
        }
        
        for domain, template in domain_templates.items():
            prompt = PromptTemplate(
                input_variables=["history", "input"],
                template=template
            )
            
            memory = ConversationBufferWindowMemory(
                k=10,  # Remember last 10 exchanges
                return_messages=False  # Return as string for Gemini compatibility
            )
            
            self.domain_chains[domain] = ConversationChain(
                llm=self.llm,
                prompt=prompt,
                memory=memory,
                verbose=False
            )
    
    def get_response(self, domain: str, user_input: str, conversation_id: str) -> str:
        """Get domain-specific response using LangChain conversation chain with Gemini"""
        
        if domain not in self.domain_chains:
            return f"Sorry, I don't have expertise in the {domain} domain yet."
        
        try:
            # Get the domain-specific chain
            chain = self.domain_chains[domain]
            
            # Generate response
            response = chain.predict(input=user_input)
            
            return response
            
        except Exception as e:
            print(f"Chat engine error: {e}")
            return "I'm having trouble processing your request. Please try again."
    
    async def stream_response(
        self,
        domain: str,
        user_input: str,
        conversation_id: str,
        max_tokens: int = 300,
        context: str = None
    ):
        """
        Stream response from Gemini (if supported), otherwise fake streaming by chunking.
        """
        if domain not in self.domain_chains:
            yield f"Sorry, I don't have expertise in the {domain} domain yet."
            return

        try:
            chain = self.domain_chains[domain]
            # If your LLM supports streaming, use it here.
            # For now, we'll fake streaming by splitting the response.
            response = chain.predict(input=user_input)
            # Split response into chunks (e.g., by sentence or every N chars)
            chunk_size = 30
            for i in range(0, len(response), chunk_size):
                yield response[i:i+chunk_size]
                await asyncio.sleep(0.05)  # Simulate streaming delay
        except Exception as e:
            yield f"\n[Error]: {str(e)}"
    
    def clear_conversation_memory(self, domain: str):
        """Clear conversation memory for a specific domain"""
        if domain in self.domain_chains:
            self.domain_chains[domain].memory.clear()

# Create singleton instance
chat_engine = DomainChatEngine()