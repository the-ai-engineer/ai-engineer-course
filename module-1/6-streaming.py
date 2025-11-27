from openai import OpenAI

client = OpenAI()

stream = client.responses.create(
    model="gpt-5-mini",
    input=[
        {
            "role": "user",
            "content": "Say 'double bubble bath' ten times fast.",
        },
    ],
    stream=True,
)

for event in stream:
    print(event)

