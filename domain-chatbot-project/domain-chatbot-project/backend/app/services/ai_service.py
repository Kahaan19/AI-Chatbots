from typing import List, Dict
from app.models.domain import Domain
from app.models.message import Message
from app.ai.domain_router import domain_router
from app.ai.chat_engine import chat_engine
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage
import os
import google.generativeai as genai
import asyncio
from app.schemas.domain import Domain as DomainSchema
import re
import requests
import uuid
from datetime import datetime

# Add these imports for image generation
# (PIL.Image and aiohttp removed as they're not used in this implementation)


class AIService:
    def __init__(self):
        # Configure Google Gemini API
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.domain_router = domain_router
        self.chat_engine = chat_engine
        # Initialize Gemini for title generation
        self.title_llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash-preview-05-20",
            temperature=0.3,
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
        
        # Pollinations API settings
        self.pollinations_base_url = "https://image.pollinations.ai/prompt"

    def _detect_image_request(self, message_content: str) -> bool:
        """Detect if the user is requesting image generation"""
        image_keywords = [
            "generate image", "create image", "make image", "draw", "picture of",
            "show me", "visualize", "generate art", "create art", "make art",
            "image of", "picture", "illustration", "artwork", "design",
            # Technical-specific keywords
            "diagram", "flowchart", "blueprint", "schematic", "chart", "graph"
        ]
        detected = any(keyword in message_content.lower() for keyword in image_keywords)
        print(f"Image detection for '{message_content}': {detected}")  # Debug log
        return detected

    def _extract_image_prompt(self, message_content: str) -> str:
        """Extract and clean the image generation prompt"""
        # Remove common prefixes
        prompt = message_content.lower()
        prefixes_to_remove = [
            "generate image of", "create image of", "make image of",
            "generate an image of", "create an image of", "make an image of",
            "draw", "show me", "picture of", "image of", "generate", "create"
        ]
        
        for prefix in prefixes_to_remove:
            if prompt.startswith(prefix):
                prompt = prompt[len(prefix):].strip()
                break
        
        return prompt.strip()

    def _generate_image(self, prompt: str, domain_name: str) -> str:
        try:
            # Enhance prompt based on domain
            enhanced_prompt = self._enhance_prompt_by_domain(prompt, domain_name)
            
            # URL encode the prompt
            import urllib.parse
            encoded_prompt = urllib.parse.quote(enhanced_prompt)
            
            # Pollinations API parameters
            params = {
                'width': 512,
                'height': 512,
                'seed': -1,  # Random seed
                'model': 'flux',  # You can use 'flux' or other available models
                'enhance': 'true'
            }
            
            # Build the URL
            param_string = '&'.join([f"{k}={v}" for k, v in params.items()])
            image_url = f"{self.pollinations_base_url}/{encoded_prompt}?{param_string}"
            
            # Download the image
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            
            # Save image locally
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"generated_{timestamp}_{uuid.uuid4().hex[:8]}.png"
            filepath = os.path.join("static", "generated_images", filename)
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Save the image
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            # Return the full URL instead of relative path
            # Assuming your FastAPI runs on port 8000, adjust if different
            return f"http://localhost:8000/static/generated_images/{filename}"
            
        except Exception as e:
            print(f"Pollinations image generation error: {e}")
            return None

    def _enhance_prompt_by_domain(self, prompt: str, domain_name: str) -> str:
        """Enhance the prompt based on the domain"""
        domain_enhancements = {
            "entertainment": f"{prompt}, cinematic, high quality, detailed, artistic, vibrant colors, professional lighting, 4k",
            "technical": f"technical diagram of {prompt}, flowchart, blueprint style, clean lines, professional diagram, schematic, engineering drawing, minimalist, clear labels, black and white"
        }
        
        enhanced = domain_enhancements.get(domain_name.lower(), f"{prompt}, high quality, detailed")
        print(f"Enhanced prompt for {domain_name}: {enhanced}")  # Debug log
        return enhanced

    def generate_response(self, domain: Domain, message_content: str, conversation_history: List[Message], conversation_id: int, length: str = "medium") -> str:
        try:
            # Convert Domain to schema if it's a SQLAlchemy model
            if isinstance(domain, Domain):
                domain_data = DomainSchema.from_orm(domain)
                domain_name = domain_data.name
            else:
                domain_name = domain.name if hasattr(domain, "name") else domain

            print(f"Domain: {domain_name}, Message: {message_content}")  # Debug log

            history_dicts = []
            for msg in conversation_history:
                history_dicts.append({
                    'role': msg.role,
                    'content': msg.content,
                    'timestamp': msg.created_at.isoformat() if hasattr(msg.created_at, 'isoformat') else str(msg.created_at)
                })

            # Check for image generation request in entertainment/technical domains
            is_image_request = self._detect_image_request(message_content)
            is_supported_domain = domain_name.lower() in ["entertainment", "technical"]
            
            print(f"Image request: {is_image_request}, Supported domain: {is_supported_domain}")  # Debug log
            
            if is_supported_domain and is_image_request:
                print("Generating image...")  # Debug log
                
                image_prompt = self._extract_image_prompt(message_content)
                image_url = self._generate_image(image_prompt, domain_name)
                
                if image_url:
                    # Generate text response about the image with length control
                    length_instruction = {
                        "short": "Give a brief description in 1-2 sentences.",
                        "medium": "Give a moderate description in 2-4 sentences.", 
                        "long": "Give a detailed description in 4-6 sentences."
                    }.get(length, "Give a moderate description in 2-4 sentences.")
                    
                    # Add length instruction directly to the query
                    enhanced_query = f"I generated an image based on: {image_prompt}. {length_instruction}"
                    
                    text_response = self.domain_router.generate_response(
                        domain=domain_name,
                        user_query=enhanced_query,
                        conversation_history=history_dicts,
                        context=self._build_context(conversation_history)
                    )
                    return f"[image]{image_url}[/image]\n\n{text_response}"
                else:
                    return "I apologize, but I'm unable to generate images right now. The image service might be temporarily unavailable. Please try again later."

            # Handle regular text responses with proper length control
            url = self._extract_url(message_content)
            url_content = ""
            if url and domain_name.lower() == "stock":
                url_content = self._fetch_url_content(url)

            context = self._build_context(conversation_history)
            if url_content:
                context = f"Here is the latest article or news content provided by the user:\n{url_content}\n\n" + context

            # Create stronger length instruction with token limits
            length_instructions = {
                "short": "CRITICAL: Maximum 30 words only. Be extremely brief.",
                "medium": "CRITICAL: Maximum 80 words. Keep it concise.",
                "long": "CRITICAL: Maximum 150 words. Be detailed but not verbose."
            }
            
            length_instruction = length_instructions.get(length, length_instructions["medium"])
            
            # Add stronger length control to the query
            enhanced_query = f"RESPONSE LENGTH LIMIT: {length_instruction}\n\nUser Question: {message_content}\n\nRemember: Strictly follow the word limit above."

            response = self.domain_router.generate_response(
                domain=domain_name,
                user_query=enhanced_query,
                conversation_history=history_dicts,
                context=context
            )

            # Enforce length limits if AI didn't follow instructions
            response = self._enforce_length_limit(response, length)

            return response

        except Exception as e:
            print(f"AI Service error: {e}")
            domain_name = getattr(domain, 'name', 'general') if hasattr(domain, 'name') else 'general'
            return self._get_fallback_response(domain_name, message_content)

    async def stream_ai_response(
        self,
        domain,
        message_content,
        conversation_history,
        conversation_id,
        length="medium"
    ):
        try:
            # Convert Domain to schema if it's a SQLAlchemy model
            if isinstance(domain, Domain):
                domain_data = DomainSchema.from_orm(domain)
                domain_name = domain_data.name
            else:
                domain_name = domain.name if hasattr(domain, "name") else domain
            
            # Check for image generation request in entertainment/technical domains
            if (domain_name.lower() in ["entertainment", "technical"] and 
                self._detect_image_request(message_content)):
                
                yield "🎨 Generating image..."
                
                image_prompt = self._extract_image_prompt(message_content)
                image_url = self._generate_image(image_prompt, domain_name)
                
                if image_url:
                    yield f"\n[image]{image_url}[/image]\n\n"
                    
                    # Generate a text response about the image with length control
                    context = self._build_context(conversation_history)
                    max_tokens = {"short": 100, "medium": 300, "long": 700}.get(length, 300)
                    
                    # Stream the description with length control
                    async for chunk in self.chat_engine.stream_response(
                        domain=domain_name,
                        user_input=f"I generated an image based on: {image_prompt}. Describe what you created in {length} length.",
                        conversation_id=conversation_id,
                        max_tokens=max_tokens,
                        context=context
                    ):
                        yield chunk
                        await asyncio.sleep(0)
                else:
                    yield "\n❌ I apologize, but I'm unable to generate images right now. The Pollinations service might be temporarily unavailable. Please try again later."
                return
            
            history_dicts = []
            for msg in conversation_history:
                history_dicts.append({
                    'role': msg.role,
                    'content': msg.content,
                    'timestamp': msg.created_at.isoformat() if hasattr(msg.created_at, 'isoformat') else str(msg.created_at)
                })

            context = self._build_context(conversation_history)
            max_tokens = {"short": 100, "medium": 300, "long": 700}.get(length, 300)

            async for chunk in self.chat_engine.stream_response(
                domain=domain_name,
                user_input=message_content,
                conversation_id=conversation_id,
                max_tokens=max_tokens,
                context=context
            ):
                yield chunk
                await asyncio.sleep(0)

        except Exception as e:
            yield f"\n[Error]: {str(e)}"

    # ... rest of the existing methods remain the same ...
    def generate_conversation_title(self, domain_name: str, first_message: str) -> str:
        """Generate a conversation title based on the first message using Gemini"""
        try:
            prompt = f"""Generate a short, descriptive title (maximum 50 characters) for a conversation based on the first message.

Domain: {domain_name}
First message: {first_message}

Create a concise title that captures the main topic. Do not use quotes around the title.

Title:"""

            messages = [HumanMessage(content=prompt)]
            response = self.title_llm.invoke(messages)
            title = response.content.strip().strip('"').strip("'")

            # Ensure title isn't too long
            if len(title) > 50:
                title = title[:47] + "..."

            return title

        except Exception as e:
            print(f"Title generation error: {e}")
            return f"New {domain_name.title()} Chat"

    def _extract_url(self, text: str) -> str:
        url_pattern = r'(https?://[^\s]+)'
        match = re.search(url_pattern, text)
        return match.group(0) if match else None

    def _fetch_url_content(self, url: str) -> str:
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            # Return only the first 2000 characters to avoid prompt overflow
            return response.text[:2000]
        except Exception as e:
            print(f"Error fetching URL content: {e}")
            return ""

    def _build_context(self, conversation_history: List[Message]) -> str:
        """Build context string from recent conversation history"""
        if not conversation_history:
            return "This is the start of a new conversation."

        recent_messages = conversation_history[-5:]  # Last 5 messages for context
        context_parts = []

        for msg in recent_messages:
            try:
                role = "User" if msg.role == "user" else "Assistant"
                content_preview = msg.content[:100] + "..." if len(msg.content) > 100 else msg.content
                context_parts.append(f"{role}: {content_preview}")
            except Exception as e:
                print(f"Error processing message in context: {e}")
                continue

        return "Recent conversation context:\n" + "\n".join(context_parts)

    def _get_fallback_response(self, domain_name: str, message_content: str) -> str:
        """Fallback response when AI services fail"""
        fallback_responses = {
            "stock": f"I understand you're asking about '{message_content}' regarding financial markets. I'm currently experiencing technical difficulties, but I'd be happy to help with your stock market questions once I'm back online.",
            "law": f"I see you have a legal question about '{message_content}'. I'm having technical issues right now, but I'd like to help with general legal information once my systems are restored.",
            "entertainment": f"You're asking about '{message_content}' in entertainment! I'm experiencing some technical difficulties, but I'd love to discuss movies, music, games, or pop culture with you once I'm back up.",
            "psychology": f"I understand you're interested in the psychological aspects of '{message_content}'. I'm currently having technical issues, but I'd be glad to share psychological insights once my systems are working properly.",
            "technical": f"I see you have a technical question about '{message_content}'. I'm experiencing some system issues right now, but I'd be happy to assist you with technical topics once I'm back online."
        }
        return fallback_responses.get(
            domain_name,
            f"I understand you're asking about '{message_content}'. I'm having some technical difficulties right now, but I'll be back to help you soon!"
        )

# Create singleton
ai_service = AIService()