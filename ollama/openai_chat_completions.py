from openai import OpenAI

# model = 'gpt-oss:20b'
# model = 'gemma3'
# model = 'qwen3-vl'
model = 'qwen3-vl:2b-instruct'
# model = 'qwen3-vl:2b-thinking'

client = OpenAI(base_url="http://localhost:11434/v1/")

chat_completion = client.chat.completions.create(
    messages=[
        {
            'role': 'user',
            'content': 'Say this is a test',
        }
    ],
    model=model,
    temperature=0
)
print(chat_completion.choices[0].message.content)