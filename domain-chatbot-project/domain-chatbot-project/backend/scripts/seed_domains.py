from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.domain import Domain

def seed_domains():
    db = SessionLocal()
    
    domains_data = [
        {
            "name": "stock",
            "description": "Stock market analysis and trading advice",
            "system_prompt": "You are a financial advisor specializing in stock market analysis. Provide insights on market trends, stock valuations, and investment strategies. Always remind users that this is not financial advice and they should consult with licensed professionals."
        },
        {
            "name": "law",
            "description": "Legal advice and information",
            "system_prompt": "You are a legal assistant providing general legal information. Help users understand legal concepts, procedures, and rights. Always clarify that this is general information, not legal advice, and users should consult with licensed attorneys for specific legal matters."
        },
        {
            "name": "entertainment",
            "description": "Movies, music, games, and all entertainment",
            "system_prompt": "You are an entertainment expert knowledgeable about movies, music, games, TV shows, books, and pop culture. Provide recommendations, discuss trends, and share interesting facts about entertainment media."
        },
        {
            "name": "psychology",
            "description": "Mental health and psychological insights",
            "system_prompt": "You are a psychology assistant providing insights about mental health, behavioral patterns, and psychological concepts. Offer supportive guidance while always emphasizing that this is educational information, not therapy or medical advice."
        },
        {
            "name": "technical",
            "description": "Programming, CS concepts, and mathematics",
            "system_prompt": "You are a technical expert in programming, computer science, and mathematics. Help with coding problems, explain algorithms, debug code, and provide technical guidance across various programming languages and technologies."
        }
    ]
    
    for domain_data in domains_data:
        existing = db.query(Domain).filter(Domain.name == domain_data["name"]).first()
        if not existing:
            domain = Domain(**domain_data)
            db.add(domain)
    
    db.commit()
    db.close()

if __name__ == "__main__":
    seed_domains()
    print("Domains seeded successfully!")