# Import necessary libraries
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import pickle
import os.path

# Constants for Google Calendar API
SCOPES = ['https://www.googleapis.com/auth/calendar']  # Scopes required to access Google Calendar
TOKEN_FILE = 'connectors/gcal_token.pickle'  # File to store the user's access and refresh tokens
CREDENTIALS_FILE = 'connectors/gcal_credentials.json'  # File with Google Calendar API credentials
TIMEZONE = "America/New_York"  # Timezone for the calendar events
CALENDAR_ID = "primary"  # ID of the calendar to be used

def authenticate_gcal():
    """
    Authenticate and create a service for accessing Google Calendar.

    Checks if a valid token is stored in TOKEN_FILE, if not, initiates a flow to
    get credentials and store them for future use.
    
    Returns:
        service: Authorized Google Calendar service object.
    """
    creds = None

    # Load credentials from the token file if it exists
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)

    # Refresh or fetch new credentials if necessary
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)
    return service

def create_gcal_event(args):
    """
    Create an event in Google Calendar.

    Args:
        args (dict): containing event details such as summary, location,
                     description, start and end times.

    Returns:
        str: Confirmation message with the link to the created event.
    """
    service = authenticate_gcal()

    # Define the event structure
    event = {
        'summary': args.get("summary"),
        'location': args.get("location"),
        'description': args.get("description"),
        'start': {
            'dateTime': args.get("start_time"),
            'timeZone': TIMEZONE,
        },
        'end': {
            'dateTime': args.get("end_time"),
            'timeZone': TIMEZONE,
        },
    }

    # Insert the event into the calendar
    event = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
    return "{'success':'true'}"

# TODO: Function to update an event
#def update_gcal_event(event_id, updated_event):
#    service = authenticate_gcal()
#    service.events().update(calendarId='primary', eventId=event_id, body=updated_event).execute()

# TODO: Function to delete an event
#def delete_gcal_event(event_id):
#    service = authenticate_gcal()
#    service.events().delete(calendarId='primary', eventId=event_id).execute()
