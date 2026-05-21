# rfp-proposal-agent
RFP Proposal Copilot is a consulting-style AI assistant that analyzes RFP content, extracts structured requirements, drafts proposal sections, and generates a risk/assumption register , implemented as a saved Azure AI Foundry Agent invoked by a FastAPI backend and a lightweight HTML frontend with session_id-based memory

## Problem
Consulting teams spend significant time manually parsing long RFP documents to extract mandatory
requirements, identify risks/assumptions/dependencies, and draft proposal sections under tight
deadlines. The process is repetitive, time-consuming, and can be inconsistent across team members.

## Solution
This MVP implements an agent-first design where a persisted Azure AI Foundry Agent encapsulates
the model configuration, instructions, and grounded knowledge (uploaded RFP documents). A FastAPI
backend handles authentication and invokes the agent through Foundry’s OpenAI-compatible
Responses API. A simple HTML+JavaScript UI enables quick testing and interactive chat. Multi-turn
context is preserved using session_id memory

## Why this design matters
Instead of hardcoding prompts and retrieval logic in application code, the project centralizes agent
behavior and knowledge in Foundry. This reduces prompt sprawl, makes iteration easier, and keeps
the backend thin and maintainable. The frontend stays minimal and focuses on user interaction and
display

## Architecture
High-level architecture:
Frontend (HTML + JavaScript) → FastAPI Backend → Azure AI Foundry Project → Saved Agent
(Instructions + Knowledge + Model)
Key principle: the backend invokes a saved agent (not a raw model). The agent encapsulates
instructions + knowledge + model selection, while the backend focuses on authentication, session
management, and safe API exposure.

## Component responsibilities (what each piece does)
Frontend (HTML + JavaScript)
• Collects user input (RFP text / questions).
• Sends POST /chat requests to the backend with message and session_id.
• Displays structured agent output.
• Keeps session_id stable to preserve multi-turn memory.

## Backend (FastAPI)
• Exposes /health for sanity checks and /chat for agent interaction.
• Authenticates via Device Code flow (development-friendly).
• Maintains session_id → conversation_id mapping (memory).
• Invokes the Foundry agent using OpenAI-compatible Responses API with agent_reference.
• Returns response text as JSON to the frontend

## Azure AI Foundry Agent
• Stores instructions (system prompt / role).
• Uses uploaded RFP documents for grounding.
• Runs a chat-capable model and returns structured outputs.
• Handles reasoning and retrieval within the agent runtime

## Runtime flow (what happens when the user clicks “Ask Agent”)
1. User pastes RFP text or types a question in the HTML UI.
2. Frontend sends POST /chat with JSON {message, session_id}.
3. Backend checks session_id. If new, it creates a new conversation; if existing, it reuses the stored
conversation_id.
4. Backend calls Foundry via responses.create(...,
extra_body={agent_reference:{name:AGENT_NAME}}).
5. Foundry agent applies instructions + retrieves from uploaded knowledge + generates response.
6. Backend returns {session_id, response} to the frontend.
7. Frontend renders the response.
Memory note: conversation_id is stored per session_id (in-memory in MVP). This preserves
conversational context across turns during a single server run.

## Code sequence (backend invocation pattern)
Conceptual sequence:
PROJECT_ENDPOINT = env['FOUNDRY_PROJECT_ENDPOINT']
AGENT_NAME      = env['FOUNDRY_AGENT_NAME']
TENANT_ID       = env['FOUNDRY_TENANT_ID']
credential = DeviceCodeCredential(tenant_id=TENANT_ID)
project    = AIProjectClient(endpoint=PROJECT_ENDPOINT, credential=credential)
openai     = project.get_openai_client()
conversation_id = conversations.get(session_id) or openai.conversations.create().id
response = openai.responses.create(conversation=conversation_id, input=user_message, extra_body={'agent_reference': {'type':'agent_reference','name':AGENT_NAME}})
return response.output_text

## session_id memory (README/interview explanation)
The UI sends a session_id with each message. The backend maps session_id to a conversation_id
(from Foundry conversations API). Reusing the same conversation_id across requests preserves
context, enabling multi-turn memory. In MVP, the store is in-memory; it can later be persisted to
SQLite/Redis for durability.

## Summary
This MVP demonstrates an agent-first architecture: a persisted Azure AI Foundry agent contains the
domain behavior and grounded knowledge, while FastAPI provides a secure, testable API surface and
the HTML frontend provides a simple user interface. The session_id memory enhancement shows state
management awareness and makes the demo feel like a real copilot
