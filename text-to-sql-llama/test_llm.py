from openai import OpenAI
# Set OpenAI's API key and API base to use vLLM's API server.
openai_api_key = "LLM"
openai_api_base = "http://64.101.169.102:8000/v1"

client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_api_base,
)

chat_response = client.chat.completions.create(
    model="/ai/models/Meta-Llama-3-8B-Instruct/",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Tell me why Cisco UCS X-Series is a great server to put GPU in and to run AI workloads"},
    ]
)
print(chat_response.choices[0].message.content)