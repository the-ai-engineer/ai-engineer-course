from openai import OpenAI
import requests
import json

client = OpenAI()


def get_weather(latitude: float, longitude: float) -> dict:
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={latitude}&longitude={longitude}"
        "&current=temperature_2m,wind_speed_10m"
    )
    data = requests.get(url, timeout=8).json()
    cur = data.get("current", {})
    return {
        "temperature_c": cur.get("temperature_2m"),
        "wind_speed": cur.get("wind_speed_10m"),
        "lat": latitude,
        "lon": longitude,
        "source": "open-meteo.com",
    }


tools = [
    {
        "type": "function",
        "name": "get_weather",
        "description": "Get current weather at given coordinates.",
        "parameters": {
            "type": "object",
            "properties": {
                "latitude": {"type": "number"},
                "longitude": {"type": "number"},
            },
            "required": ["latitude", "longitude"],
        },
    }
]

messages = [{"role": "user", "content": "What’s the weather in London right now?"}]

# 1) Let the model decide to call the tool
resp1 = client.responses.create(model="gpt-5", tools=tools, input=messages)

# 2) Run the tool if requested, attach output, then finalize
for item in resp1.output:
    if getattr(item, "type", "") == "function_call" and item.name == "get_weather":
        args = json.loads(item.arguments or "{}")
        result = get_weather(**args)
        messages += resp1.output
        messages.append(
            {
                "type": "function_call_output",
                "call_id": item.call_id,
                "output": json.dumps(result),
            }
        )

resp2 = client.responses.create(
    model="gpt-5",
    tools=tools,
    input=messages,
    instructions="You are a helpful weather assistant. Be concise",
)

print(resp2.output_text)
