import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from azure.ai.projects import AIProjectClient
from azure.identity import DeviceCodeCredential

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

@app.get("/health")
def health():
    return {"status": "ok"}

TENANT_ID = os.getenv("FOUNDRY_TENANT_ID")
PROJECT_ENDPOINT = os.getenv("FOUNDRY_PROJECT_ENDPOINT")
AGENT_NAME = os.getenv("FOUNDRY_AGENT_NAME")

if not TENANT_ID:
    raise RuntimeError("Missing FOUNDRY_TENANT_ID in .env")
if not PROJECT_ENDPOINT:
    raise RuntimeError("Missing FOUNDRY_PROJECT_ENDPOINT in .env")
if not AGENT_NAME:
    raise RuntimeError("Missing FOUNDRY_AGENT_NAME in .env")

# Force tenant so it does NOT try "Microsoft Services"
credential = DeviceCodeCredential(tenant_id=TENANT_ID)

project = AIProjectClient(endpoint=PROJECT_ENDPOINT, credential=credential)
openai = project.get_openai_client()

@app.post("/chat")
def chat(req: ChatRequest):
    conversation = openai.conversations.create()

    response = openai.responses.create(
        conversation=conversation.id,
        input=req.message,
        extra_body={
            "agent_reference": {
                "type": "agent_reference",
                "name": AGENT_NAME
            }
        },
    )

    return {"response": response.output_text}
