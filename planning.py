import os
import json
from openai import OpenAI
from connectors.gcal import *  # Import Google Calendar connector functions
from config import OPENAI_KEY  # Import OpenAI API key

# Constants
GPT_MODEL = "gpt-3.5-turbo-1106"  # GPT model version
SYSTEM_PROMPT = """
    You are Admina and you are trying to help your owner, Halit. 
    You will manage his calendar with your tools based on the information
    that you receive such as message chains.
"""
PLANNING_PROMPT = """
    Here is the message chain:

    2023 Dec 18:
    Bob: Hi, do you remember our lunch tomorrow at 1pm?
    Halit: Yes, I do remember.
    Bob: Can we move to 2pm?
    Halit: Yeah, sure.
    Bob: Great.
"""

# Message chain for the OpenAI chat completion
messages = [
    {"role": "system", "content": SYSTEM_PROMPT},
    {"role": "system", "content": PLANNING_PROMPT}
]

# Tool definition for calendar event creation
tools = [
    {
        "type": "function",
        "function": {
            "name": "create_gcal_event",
            "description": "Create a new event in Google Calendar",
            "parameters": {
                "type": "object",
                "properties": {
                    "summary": {
                        "type": "string",
                        "description": "The title of the event"
                    },
                    "location": {
                        "type": "string",
                        "description": "The location of the event"
                    },
                    "description": {
                        "type": "string",
                        "description": "A description of the event"
                    },
                    "start_time": {
                        "type": "string",
                        "description": "Start time of the event in ISO format"
                    },
                    "end_time": {
                        "type": "string",
                        "description": "End time of the event in ISO format"
                    }
                },
                "required": ["summary", "start_time", "end_time"]
            },
        },
    }
]

# Initialize OpenAI client with the API key
client = OpenAI(api_key=OPENAI_KEY)

# Create a chat completion with OpenAI
response = client.chat.completions.create(
    model=GPT_MODEL,
    messages=messages,
    tools=tools,
    tool_choice="auto"  # auto is default, but we'll be explicit
)

# Extract and print the response message content
response_message = response.choices[0].message

# Process tool calls in the response message
tool_calls = response_message.tool_calls
if tool_calls:
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