from openai import OpenAI
import json
from pathlib import Path

client = OpenAI()


# --- Tool: return the full policy document ----------------------------------
def get_policy_doc() -> dict:
    return Path("policy.md").read_text(encoding="utf-8")


# --- Tool spec exposed to the model -----------------------------------------
tools = [
    {
        "type": "function",
        "name": "get_policy_doc",
        "description": "Return the complete store policy document in Markdown.",
        "parameters": {"type": "object", "properties": {}},
    }
]

# --- User asks a question ----------------------------------------------------
messages = [
    {
        "role": "user",
        "content": "My order was damaged on arrival. Can I get a refund?",
    }
]

# 1) Let the model decide to call the tool
resp1 = client.responses.create(model="gpt-5", tools=tools, input=messages)

# 2) If the model called the tool, run it and attach the result
for item in resp1.output:
    if getattr(item, "type", "") == "function_call" and item.name == "get_policy_doc":
        print("Calling the policy document tool")
        result = get_policy_doc()
        messages += resp1.output  # include the function_call in conversation history
        messages.append(
            {
                "type": "function_call_output",
                "call_id": item.call_id,
                "output": json.dumps(result),
            }
        )

# 3) Final grounded answer (use ONLY the policy doc)
resp2 = client.responses.create(
    model="gpt-5",
    tools=tools,
    input=messages,
    instructions=(
        "You are a helpful customer support assistant."
        "Answer customer questions ONLY based on information in the policy document."
        "Never make up information not in the policy document"
        "If you do not know the answer, say you only answer questions about store policies."
    ),
)

print(resp2.output_text)
