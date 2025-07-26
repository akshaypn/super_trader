from openai import OpenAI
import os

client = OpenAI(
  api_key=os.getenv("OPENAI_API_KEY", "your-openai-api-key-here")
)

response = client.responses.create(
  model="gpt-4o-mini",
  input="write a haiku about ai",
  store=True,
)

print(response.output_text);
