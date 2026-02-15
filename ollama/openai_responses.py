from openai import OpenAI

client = OpenAI(base_url="http://localhost:11434/v1/")

responses_result = client.responses.create(
  model='qwen3:8b',
  input='Write a short poem about the color blue',
)
print(responses_result.output_text)