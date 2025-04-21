from openai import OpenAI

client = OpenAI(base_url="http://198.19.5.70:8000/v1", api_key="not-used")
MODEL_NAME = "meta/llama3-8b-instruct"

# Define available function
weather_tool = {
    "type": "function",
    "function": {
        "name": "get_current_weather",
        "description": "Get the current weather",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city and state, e.g. San Francisco, CA"
                },
                "format": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"],
                    "description": "The temperature unit to use. Infer this from the user's location."
                }
            },
            "required": ["location", "format"]
        }
    }
}

messages = [
    {"role": "user", "content": "Is it hot in Pittsburgh, PA right now?"}
]

chat_response = client.chat.completions.create(
    model=MODEL_NAME,
    messages=messages,
    tools=[weather_tool],
    tool_choice="auto",
    stream=False
)

assistant_message = chat_response.choices[0].message
messages.append(assistant_message)

print(assistant_message)
# Example output:
# ChatCompletionMessage(content=None, role='assistant', function_call=None, tool_calls=[ChatCompletionMessageToolCall(id='call_abc123', function=Function(arguments='{"location": "Pittsburgh, PA", "format": "fahrenheit"}', name='get_current_weather'), type='function')])

# Simulate external function call
tool_call_result = 88
tool_call_id = assistant_message.tool_calls[0].id
tool_function_name = assistant_message.tool_calls[0].function.name
messages.append({"role": "tool", "content": str(tool_call_result), "tool_call_id": tool_call_id, "name": tool_function_name})

chat_response = client.chat.completions.create(
    model=MODEL_NAME,
    messages=messages,
    tools=[weather_tool],
    tool_choice="auto",
    stream=False
)

assistant_message = chat_response.choices[0].message
print(assistant_message)
# Example output:
# ChatCompletionMessage(content='Based on the current temperature of 88°F (31°C) in Pittsburgh, PA, it is indeed quite hot right now. This temperature is generally considered warm to hot, especially if accompanied by high humidity, which is common in Pittsburgh during summer months.', role='assistant', function_call=None, tool_calls=None)