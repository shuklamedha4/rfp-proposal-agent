import os
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.identity import DeviceCodeCredential

load_dotenv()

endpoint = os.getenv("FOUNDRY_PROJECT_ENDPOINT")
tenant_id = os.getenv("FOUNDRY_TENANT_ID")	

credential = DeviceCodeCredential(tenant_id=tenant_id)

client = AIProjectClient(endpoint=endpoint, credential=credential)

print("\nAgents found in project:")
for agent in client.agents.list():  # correct method in your SDK
    print("Name:", agent.name, "| ID:", agent.id)
