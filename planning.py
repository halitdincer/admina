import os
import json
from openai import OpenAI
from connectors.gcal import *  # Import Google Calendar connector functions
from connectors.mail import fetch_emails_from_today
from constants import *

emails_from_today = fetch_emails_from_today(MAIL_ADDRESS, MAIL_PASSWORD, MAIL_SERVER)

PLANNING_PROMPT = """
    Mail chain:
    {}
    Note: Do not send any reply to the user after this prompt. Just use tools whenever there is at least one potential event in the mail chain.
""".format(emails_from_today)

# Message chain for the OpenAI chat completion
messages = [
    {"role": "system", "content": SYSTEM_PROMPT},
    {"role": "user", "content": PLANNING_PROMPT}
]

print(f'USER > {PLANNING_PROMPT}')

# Initialize OpenAI client with the API key
client = OpenAI(api_key=OPENAI_KEY)

# Create a chat completion with OpenAI
response = client.chat.completions.create(
    model=GPT_MODEL,
    messages=messages,
    tools=TOOLS,
    tool_choice="auto"  # auto is default, but we'll be explicit
)

# Extract and print the response message content
response_message = response.choices[0].message

# Process tool calls in the response message
if response_message and response_message.tool_calls:

    print(f'Admina > {response_message.tool_calls}')
    tool_calls = response_message.tool_calls
    # Mapping of available functions
    available_functions = {
        "create_gcal_event": create_gcal_event
    } 

    # Append the response message to the message chain
    messages.append(response_message)  

    # Execute function calls and append their responses
    for tool_call in tool_calls:
        function_name = tool_call.function.name
        function_to_call = available_functions[function_name]
        function_args = json.loads(tool_call.function.arguments)
        function_response = function_to_call(function_args)
        messages.append(
            {
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": function_response,
            }
        )

    # Create a second chat completion with the updated messages
    second_response = client.chat.completions.create(
        model=GPT_MODEL,
        messages=messages
    ) 
    print(second_response.choices[0].message.content)
else:
    print("LOG > There wasn't any tool calls.")