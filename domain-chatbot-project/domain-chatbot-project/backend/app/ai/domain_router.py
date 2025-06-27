from typing import Dict, List, Any, TypedDict
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from langgraph.graph import Graph, END
import os
from enum import Enum

import google.generativeai as genai

class DomainType(str, Enum):
    STOCK = "stock"
    LAW = "law"
    ENTERTAINMENT = "entertainment"
    PSYCHOLOGY = "psychology"
    TECHNICAL = "technical"

class ConversationState(TypedDict):
    messages: List[BaseMessage]
    domain: str
    system_prompt: str
    user_query: str
    context: str
    response: str
    analysis: str


class DomainRouter:
    def __init__(self):
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash-preview-05-20",
            temperature=0.7,
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            convert_system_message_to_human=True
        )
        self.domain_prompts = {
            DomainType.STOCK: (
                "You are a professional financial advisor and stock market analyst. "
                "You provide insights on:\n"
                "- Stock analysis and market trends\n"
                "- Investment strategies and portfolio management\n"
                "- Risk assessment and market predictions\n"
                "- Company financial health and valuation\n\n"
                "Always remind users that this is educational information, not personalized financial advice, "
                "and they should consult with licensed financial professionals for investment decisions."
            ),
            DomainType.LAW: (
                "You are a knowledgeable legal assistant providing general legal information.\n"
                "You help with:\n"
                "- Legal concepts and terminology\n"
                "- General legal procedures and rights\n"
                "- Document understanding and legal research\n"
                "- Court processes and legal system navigation\n\n"
                "Always clarify that this is general legal information, not legal advice, "
                "and users should consult with licensed attorneys for specific legal matters."
            ),
            DomainType.ENTERTAINMENT: (
                "You are an entertainment expert and pop culture enthusiast.\n"
                "You provide insights on:\n"
                "- Movies, TV shows, and streaming content\n"
                "- Music trends and artist information\n"
                "- Video games and gaming industry\n"
                "- Books, comics, and pop culture trends\n"
                "- Celebrity news and entertainment industry insights\n\n"
                "Keep responses engaging and up-to-date with current entertainment trends."
            ),
            DomainType.PSYCHOLOGY: (
                "You are a psychology expert providing educational insights about mental health.\n"
                "You help with:\n"
                "- Psychological concepts and theories\n"
                "- Mental health awareness and understanding\n"
                "- Behavioral patterns and cognitive processes\n"
                "- Stress management and coping strategies\n"
                "- Personal development and well-being tips\n\n"
                "Always emphasize that this is educational information, not therapy or medical advice. "
                "Encourage users to seek professional help for serious mental health concerns."
            ),
            DomainType.TECHNICAL: (
                "You are a senior software engineer and computer science expert.\n"
                "You provide help with:\n"
                "- Programming in multiple languages (Python, JavaScript, Java, etc.)\n"
                "- Software architecture and design patterns\n"
                "- Algorithms and data structures\n"
                "- Debugging and code optimization\n"
                "- System design and best practices\n"
                "- Mathematics and computational problems\n\n"
                "Provide practical, working solutions with clear explanations."
            )
        }
        self.workflow = self._build_workflow()

    def _build_workflow(self) -> Graph:
        def analyze_query(state: ConversationState) -> ConversationState:
            analysis_prompt = (
                f"You are an expert query analyzer. Analyze this user query in the context of {state['domain']} domain:\n\n"
                f"Query: {state['user_query']}\n\n"
                f"Consider the conversation context: {state['context']}\n\n"
                "Provide a brief analysis of what the user is asking for and any key topics to address."
            )
            messages = [HumanMessage(content=analysis_prompt)]
            response = self.llm.invoke(messages)
            state['analysis'] = response.content
            return state

        def generate_domain_response(state: ConversationState) -> ConversationState:
            conversation_context = f"{state['system_prompt']}\n\n"
            if state['messages']:
                conversation_context += "Previous conversation:\n"
                for msg in state['messages'][-6:]:
                    role = "Human" if isinstance(msg, HumanMessage) else "Assistant"
                    conversation_context += f"{role}: {msg.content}\n"
                conversation_context += "\n"
            conversation_context += f"Human: {state['user_query']}\n\nAssistant:"
            messages = [HumanMessage(content=conversation_context)]
            response = self.llm.invoke(messages)
            state['response'] = response.content
            return state

        def enhance_response(state: ConversationState) -> ConversationState:
            enhancement_prompts = {
                DomainType.STOCK: "You are a financial response formatter. Format this financial response with clear sections for analysis, recommendations, and risk warnings.",
                DomainType.LAW: "You are a legal response formatter. Structure this legal response with clear sections and include relevant disclaimers.",
                DomainType.ENTERTAINMENT: "You are an entertainment response formatter. Make this entertainment response engaging with interesting facts and current trends.",
                DomainType.PSYCHOLOGY: "You are a psychology response formatter. Structure this psychology response with clear explanations and practical insights.",
                DomainType.TECHNICAL: "You are a technical response formatter. Format this technical response with code examples, best practices, and clear explanations."
            }
            if state['domain'] in enhancement_prompts:
                enhance_prompt = (
                    f"{enhancement_prompts[state['domain']]}\n\n"
                    f"Original response:\n{state['response']}\n\n"
                    "Provide an enhanced, well-structured version that maintains all the original information but improves formatting and readability."
                )
                messages = [HumanMessage(content=enhance_prompt)]
                enhanced_response = self.llm.invoke(messages)
                state['response'] = enhanced_response.content
            return state

        workflow = Graph()
        workflow.add_node("analyze_query", analyze_query)
        workflow.add_node("generate_response", generate_domain_response)
        workflow.add_node("enhance_response", enhance_response)
        workflow.add_edge("analyze_query", "generate_response")
        workflow.add_edge("generate_response", "enhance_response")
        workflow.add_edge("enhance_response", END)
        workflow.set_entry_point("analyze_query")
        return workflow.compile()

    def generate_response(self, domain: str, user_query: str, conversation_history: List[Dict], context: str = "") -> str:
        try:
            messages = []
            for msg in conversation_history:
                if msg['role'] == 'user':
                    messages.append(HumanMessage(content=msg['content']))
                elif msg['role'] == 'assistant':
                    messages.append(AIMessage(content=msg['content']))
            initial_state: ConversationState = {
                'messages': messages,
                'domain': domain,
                'system_prompt': self.domain_prompts.get(domain, "You are a helpful assistant."),
                'user_query': user_query,
                'context': context,
                'response': ''
            }
            result = self.workflow.invoke(initial_state)
            return result['response']
        except Exception as e:
            fallback_response = (
                f"I understand you're asking about '{user_query}' in the {domain} domain. "
                "I'm having trouble processing your request right now, but I'd be happy to help. "
                "Could you please rephrase your question?"
            )
            print(f"LangGraph error: {e}")
            return fallback_response

domain_router = DomainRouter()