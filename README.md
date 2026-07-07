# AI-Chatbots — Domain Chatbot Platform

A full-stack, multi-domain AI chatbot application. Users sign up, pick a domain of expertise (Stock Market, Law, Entertainment, Psychology, or Technical), and chat with a domain-specialized AI assistant powered by Google Gemini, LangChain, and LangGraph — with persisted conversation history, streaming responses, and on-demand AI image generation.

<p align="left">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white">
  <img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white">
  <img alt="Next.js" src="https://img.shields.io/badge/Next.js-14-000000?logo=nextdotjs&logoColor=white">
  <img alt="PostgreSQL" src="https://img.shields.io/badge/PostgreSQL-336791?logo=postgresql&logoColor=white">
  <img alt="LangChain" src="https://img.shields.io/badge/LangChain%20%2B%20LangGraph-1C3C3C?logo=langchain&logoColor=white">
  <img alt="Google Gemini" src="https://img.shields.io/badge/Google%20Gemini-8E75B2?logo=googlegemini&logoColor=white">
</p>

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Request Flow: Sending a Chat Message](#request-flow-sending-a-chat-message)
- [Domain Routing / LangGraph Workflow](#domain-routing--langgraph-workflow)
- [Data Model (ERD)](#data-model-erd)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
- [Environment Variables](#environment-variables)
- [API Reference](#api-reference)
- [Database Migrations](#database-migrations)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

**AI-Chatbots** is a domain-specialized conversational AI platform. Instead of one generic chatbot, users choose a domain — **Stock**, **Law**, **Entertainment**, **Psychology**, or **Technical** — and every response is generated with a domain-specific system prompt, persona, and post-processing pipeline (analysis → generation → formatting) built with **LangGraph**.

The backend is a **FastAPI** REST + streaming API backed by **PostgreSQL** (via SQLAlchemy + Alembic). The frontend is a **Next.js 14** App Router application styled with **Tailwind CSS** and **shadcn/ui** (Radix primitives).

## Key Features

- 🔐 **JWT authentication** — signup/login with bcrypt-hashed passwords and bearer-token protected routes
- 🧭 **Multi-domain chat** — Stock, Law, Entertainment, Psychology, Technical, each with its own persona/system prompt
- 🔁 **LangGraph pipeline** — every AI reply passes through `analyze → generate → enhance` nodes for higher-quality, well-structured answers
- ⚡ **Streaming responses** — Server-Sent Events (SSE) endpoint for token-by-token chat UX
- 💬 **Persistent conversations** — conversations and messages stored in Postgres, with auto-generated conversation titles
- 🎨 **AI image generation** — detects image requests (e.g. "draw a diagram of...") and generates images via the Pollinations API, enhanced per-domain (e.g. schematic-style for Technical, cinematic for Entertainment)
- 📏 **Response length control** — short / medium / long response modes enforced via prompt instructions + post-hoc truncation
- 🌗 **Dark/light theme** support in the frontend
- 🗃️ **Alembic migrations** for schema versioning

## Tech Stack

| Layer          | Technology |
|----------------|------------|
| Frontend       | Next.js 14 (App Router), React 18, TypeScript/JSX, Tailwind CSS, shadcn/ui (Radix UI), Recharts |
| Backend        | FastAPI, Pydantic v2, Uvicorn |
| AI / Orchestration | LangChain, LangGraph, Google Gemini (`gemini-2.5-flash-preview-05-20`) |
| Database       | PostgreSQL, SQLAlchemy 2.0, Alembic |
| Auth           | JWT (python-jose), bcrypt (passlib) |
| Image Gen      | Pollinations.ai image API |

## Architecture

```mermaid
flowchart TB
    subgraph Client["Frontend — Next.js"]
        UI["Chat UI / Auth Pages<br/>(app/, components/)"]
        Ctx["AuthContext / ChatContext"]
        Svc["services/api.js, authService.js, chatService.js"]
    end

    subgraph API["Backend — FastAPI (main.py)"]
        MW["CORS Middleware"]
        AuthR["/api/auth<br/>routers/auth.py"]
        DomR["/api/domains<br/>routers/domains.py"]
        ConvR["/api/conversations<br/>routers/conversations.py"]
        ChatR["/api/chat<br/>routers/chat.py"]
    end

    subgraph Services["Service Layer"]
        AuthSvc["auth_service.py"]
        ConvSvc["conversation_service.py"]
        MsgSvc["message_service.py"]
        DomSvc["domain_service.py"]
        AISvc["ai_service.py"]
    end

    subgraph AI["AI Layer"]
        Router["domain_router.py<br/>(LangGraph workflow)"]
        Engine["chat_engine.py<br/>(LangChain memory chains)"]
        Gemini["Google Gemini API"]
        Pollinations["Pollinations.ai<br/>(image generation)"]
    end

    subgraph Data["Persistence"]
        PG[("PostgreSQL")]
        Static["/static/generated_images"]
    end

    UI --> Ctx --> Svc
    Svc -- "HTTPS + JWT" --> MW
    MW --> AuthR & DomR & ConvR & ChatR

    AuthR --> AuthSvc --> PG
    DomR --> DomSvc --> PG
    ConvR --> ConvSvc & MsgSvc --> PG
    ChatR --> MsgSvc & DomSvc
    ChatR --> AISvc

    AISvc --> Router
    AISvc --> Engine
    AISvc -- "image request detected" --> Pollinations --> Static
    Router --> Gemini
    Engine --> Gemini

    AISvc --> MsgSvc
```

## Request Flow: Sending a Chat Message

```mermaid
sequenceDiagram
    participant U as User (Browser)
    participant FE as Next.js Frontend
    participant API as FastAPI /api/chat
    participant MS as MessageService
    participant AIS as AIService
    participant DR as DomainRouter (LangGraph)
    participant LLM as Gemini

    U->>FE: Types message, hits send
    FE->>API: POST /api/chat/{conversation_id}/stream (JWT, message)
    API->>API: Verify conversation belongs to user
    API->>MS: create_message(role="user")
    MS-->>API: user message persisted
    API->>AIS: stream_ai_response(domain, message, history)
    alt Image request detected
        AIS->>AIS: generate image via Pollinations
        AIS-->>FE: stream "[image]url[/image]" + description
    else Standard text response
        AIS->>DR: generate_response(domain, query, history, context)
        DR->>LLM: analyze_query node
        DR->>LLM: generate_response node
        DR->>LLM: enhance_response node
        LLM-->>DR: final formatted response
        DR-->>AIS: response text
        AIS-->>FE: stream response chunks (SSE)
    end
    FE-->>U: Renders streamed tokens live
    API->>MS: create_message(role="assistant", full response)
```

## Domain Routing / LangGraph Workflow

Every non-image chat response is processed by a 3-node LangGraph graph defined in [`domain_router.py`](domain-chatbot-project/domain-chatbot-project/backend/app/ai/domain_router.py):

```mermaid
flowchart LR
    Start([User Query + Domain + History]) --> A[analyze_query]
    A -->|"analysis of intent/topics"| B[generate_domain_response]
    B -->|"raw domain-specific answer"| C[enhance_response]
    C -->|"reformatted, structured answer"| End([Final Response])

    style A fill:#4C6EF5,color:#fff
    style B fill:#3B5BDB,color:#fff
    style C fill:#2F42A6,color:#fff
```

Each domain (`stock`, `law`, `entertainment`, `psychology`, `technical`) has its own **system prompt** and **enhancement formatter**, so the same 3-step pipeline produces a financial-analyst-styled answer for Stock and a code-example-rich answer for Technical.

## Data Model (ERD)

```mermaid
erDiagram
    USER ||--o{ CONVERSATION : owns
    DOMAIN ||--o{ CONVERSATION : categorizes
    CONVERSATION ||--o{ MESSAGE : contains

    USER {
        int id PK
        string email
        string username
        string password_hash
        string full_name
        datetime created_at
        datetime updated_at
    }
    DOMAIN {
        int id PK
        string name
        text description
        text system_prompt
    }
    CONVERSATION {
        int id PK
        int user_id FK
        int domain_id FK
        string title
        datetime created_at
        datetime updated_at
    }
    MESSAGE {
        int id PK
        int conversation_id FK
        string role "user | assistant"
        text content
        datetime created_at
    }
```

## Project Structure

```
AI-Chatbots/
└── domain-chatbot-project/
    └── domain-chatbot-project/
        ├── backend/                      # FastAPI service
        │   ├── main.py                   # App entrypoint, CORS, router registration
        │   ├── alembic/                  # DB migrations
        │   ├── scripts/seed_domains.py   # Seeds the 5 default domains
        │   └── app/
        │       ├── ai/                   # chat_engine.py, domain_router.py (LangChain/LangGraph)
        │       ├── models/               # SQLAlchemy models (User, Domain, Conversation, Message)
        │       ├── routers/              # auth, domains, conversations, chat
        │       ├── schemas/              # Pydantic request/response schemas
        │       ├── services/             # business logic layer
        │       ├── utils/                # security (JWT/bcrypt), auth dependency
        │       ├── config.py             # Settings (pydantic-settings, .env driven)
        │       └── database.py           # Engine/session/Base setup
        └── frontend/                     # Next.js 14 App Router client
            ├── app/                      # routes: /, /auth/login, /auth/signup, /chat, /dashboard
            ├── components/               # auth/, chat/, domain/, common/, ui/ (shadcn)
            ├── context/                  # AuthContext, ChatContext
            └── services/                 # api.js, authService.js, chatService.js
```

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+ and a package manager (npm / pnpm)
- PostgreSQL 14+ running locally or accessible remotely
- A Google Gemini API key ([Google AI Studio](https://ai.google.dev/))

### Backend Setup

```bash
cd domain-chatbot-project/domain-chatbot-project/backend

# 1. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment variables (see below)
#    create a .env file in backend/ with the variables listed in
#    the "Environment Variables" section

# 4. Run database migrations
alembic upgrade head

# 5. Seed the default domains (stock, law, entertainment, psychology, technical)
python -m scripts.seed_domains

# 6. Start the API server
uvicorn main:app --reload --port 8000
```

The API will be live at `http://localhost:8000`, with interactive docs at `http://localhost:8000/docs`.

### Frontend Setup

```bash
cd domain-chatbot-project/domain-chatbot-project/frontend

# 1. Install dependencies
npm install        # or: pnpm install

# 2. Configure environment variables
#    Note: the frontend prepends "/api" to every request itself,
#    so this value must NOT include the /api suffix.
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# 3. Run the dev server
npm run dev
```

The app will be live at `http://localhost:3000`.

## Environment Variables

Backend (`backend/.env`):

| Variable | Required | Description |
|---|---|---|
| `DATABASE_URL` | ✅ | PostgreSQL connection string, e.g. `postgresql://user:pass@localhost:5432/chatbot_db` |
| `SECRET_KEY` | ✅ | Secret used to sign JWTs |
| `ALGORITHM` | – | JWT signing algorithm (default `HS256`) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | – | Token TTL in minutes (default `30`) |
| `GOOGLE_API_KEY` | ✅ | Google Gemini API key used by LangChain/LangGraph |
| `GOOGLE_APPLICATION_CREDENTIALS` | – | Path to a GCP service-account credentials file (optional) |
| `HUGGINGFACE_API_KEY` | – | Reserved for future Hugging Face integrations |
| `RUNWAYML_API_KEY` | – | Reserved for future RunwayML integrations |
| `APP_NAME` | – | Display name (default `Domain Chatbot`) |
| `DEBUG` | – | FastAPI debug mode (default `true`) |
| `NEXT_PUBLIC_API_URL` | ✅ | Read by backend config for reference/consistency with frontend |

Frontend (`frontend/.env.local`):

| Variable | Required | Description |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | ✅ | Base URL of the backend **without** a trailing `/api` (the frontend adds `/api` to each path itself), e.g. `http://localhost:8000` |

> ⚠️ Never commit `.env` files — they contain secrets and should be gitignored.

## API Reference

All endpoints below are mounted under `/api`. Protected endpoints require an `Authorization: Bearer <token>` header.

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/auth/signup` | – | Create a new user account |
| POST | `/auth/login` | – | Exchange **username** + password for a JWT access token |
| GET  | `/auth/me` | ✅ | Get the current authenticated user |
| GET  | `/domains/` | ✅ | List all available chat domains |
| GET  | `/domains/{domain_id}` | ✅ | Get a specific domain |
| POST | `/conversations/` | ✅ | Start a new conversation in a domain |
| GET  | `/conversations/` | ✅ | List the current user's conversations (optionally filter by domain) |
| GET  | `/conversations/{id}` | ✅ | Get a single conversation |
| GET  | `/conversations/{id}/messages` | ✅ | Get a conversation with its full message history |
| PUT  | `/conversations/{id}` | ✅ | Update a conversation (e.g. rename) |
| DELETE | `/conversations/{id}` | ✅ | Delete a conversation |
| POST | `/chat/{conversation_id}` | ✅ | Send a message, get a full (non-streamed) AI response |
| POST | `/chat/{conversation_id}/stream` | ✅ | Send a message, receive the AI response as an SSE stream |
| GET  | `/chat/{conversation_id}/history` | ✅ | Get recent chat history for a conversation |
| GET  | `/health` | – | Health check (verifies DB connectivity) |
| GET  | `/test-db` | – | Returns row counts for each table (debug utility) |

Full interactive documentation (Swagger UI) is auto-generated by FastAPI at **`/docs`**, and ReDoc at **`/redoc`**.

## Database Migrations

Schema changes are managed with **Alembic**:

```bash
cd backend

# Generate a new migration after changing SQLAlchemy models
alembic revision --autogenerate -m "describe your change"

# Apply pending migrations
alembic upgrade head

# Roll back the last migration
alembic downgrade -1
```

## Roadmap

- [ ] Automated test suite (`test_api.py`, `test_backend.py`, `test_hf_api.py` exist as manual/ad-hoc scripts — migrate to `pytest`)
- [ ] Real token-level streaming from Gemini (currently simulated via chunked splitting)
- [ ] Rate limiting / usage quotas per user
- [ ] Dockerfile + docker-compose for one-command local setup
- [ ] CI pipeline (lint, type-check, test) on pull requests

## Contributing

1. Fork the repo and create a feature branch: `git checkout -b feature/my-feature`
2. Make your changes with clear, focused commits
3. Ensure the backend runs (`uvicorn main:app --reload`) and the frontend builds (`npm run build`) cleanly
4. Open a pull request describing the change and motivation

## License

No license file is currently included in this repository. Until a `LICENSE` is added, the code is **All Rights Reserved** by default and may not be reused without the author's permission. To make the project open source, add a `LICENSE` file (e.g. [MIT](https://choosealicense.com/licenses/mit/)) and update this section.
