from openai import OpenAI

# Initialize the client to connect to the local server
# For Ollama, the default base_url is "http://localhost:11434/v1"
# A dummy API key is required by the SDK, but not used by the local server
client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama", # Can be any non-empty string
)

# Specify the model name available in your local runner
# For Ollama with the llama3 model, it would be "llama3"
# model_name = "qwen3-vl:2b"
# model_name = "qwen3-vl:2b-instruct"
# model_name = "qwen3-vl:4b-instruct"
# model_name = "qwen3-vl:8b"
model_name = "qwen3-vl:8b-instruct"
# model_name = "llama3.2" 

# Use the standard OpenAI chat completions API
response = client.chat.completions.create(
    model=model_name,
    messages=[
        # {"role": "system", "content": "You are a helpful assistant that responds in haikus."},
        # {"role": "user", "content": "Explain how to use a local model with the OpenAI python SDK."}
        {"role": "user", "content": "Hello, how are you?"}
    ],
    temperature=0,
)

# Print the model's response
print(response.choices[0].message.content)