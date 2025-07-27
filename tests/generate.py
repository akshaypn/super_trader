from openai import OpenAI
import os

client = OpenAI(
  api_key=os.getenv("OPENAI_API_KEY", "your-openai-api-key-here")
)

response = client.chat.completions.create(
  model="gpt-4o-mini",
  messages=[
    {"role": "user", "content": "write a haiku about ai"}
  ]
)

print(response.choices[0].message.content)
