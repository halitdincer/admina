OPENAI_KEY = "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"
MAIL_ADDRESS = "imhalitdincer@gmail.com"
MAIL_PASSWORD = "yxrq dawj wbke titz"
MAIL_SERVER = "imap.gmail.com"

GPT_MODEL = "gpt-3.5-turbo" 
SYSTEM_PROMPT = """
    As an AI assistant, you will utilize 'create_gcal_event' function in your tool call to create 
    events in user's calendar for events and appointments that you found in emails that user sent it
    to you. Your task is to analyze the provided emails and identify potential calendar events. When
    you identify an event, use the 'create_gcal_event' function in your tool call functions to schedule
    it in Google Calendar with 'create_gcal_event' function immediately without asking a confirmation from the user. Avoid making assumptions
    or guesses about the content; focus only on the information clearly presented in the emails.

    Note: Do not send any reply to user in all prompts. Just use tools whenever there is at least one potential event in the mail chains.
    """

TOOLS = [
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