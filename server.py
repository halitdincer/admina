import os
import json
from openai import OpenAI

GPT_MODEL = "gpt-3.5-turbo"
SYSTEM_PROMPT = """
             You are Atlas and you are trying to help your owner, Halit. 
             You have access to his personal information with chat history.
             """
HISTORY_FILE = "history.txt"

def Message(role, content):
    return {"role": role, "content": content}

def load_message_history():
    """
    Load previous conversation messages
    """

    history = [Message("system", SYSTEM_PROMPT)]

    try:
        with open(HISTORY_FILE, 'r') as file:
            history.extend(json.load(file))
    except FileNotFoundError:
        print(f'Server: Message history file not found')
    except Exception as e:
        print(f'Server: Error while loading the message history. Error text is \'{e}\' ')

    return history

def save_message_history(history):
    """
    Save conversation history
    """
    try:
        with open(HISTORY_FILE, 'w') as file:
            json.dump(history[1:101], file, indent=4)
    except Exception as e:
        print(f'Server: The message history has not been saved\n Error: {e}')

def send_message(message):
    """
    Function to communicate with GPT-3
    """

    client = OpenAI(api_key=open('key.txt', 'r').read().strip())

    history = load_message_history()

    history.append(message)

    response = client.chat.completions.create(
        model=GPT_MODEL,
        messages=history
    ).choices[0].message.content

    history.append(Message("assistant", response))

    save_message_history(history)

    return response