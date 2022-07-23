from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta


SCOPES = ['https://www.googleapis.com/auth/calendar']
SERVICE_ACCOUNT_FILE = 'cardiodep.json' 


def service_build ():
    #create credentials instance 
    credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    #Construct a Resource object for interacting with an API
    service = build('calendar', 'v3', credentials=credentials)
    return service

def create_calendar(summary, timeZone):
    calendar = {
    'summary': summary,
    'timeZone': timeZone
    }
    created_calendar = service.calendars().insert(body=calendar).execute()
    return created_calendar['id']

def give_access (cal_ID,dr_email):
    #Creates an access control rule
    rule = {
        'scope': {
            'type' : 'user',
            'value': dr_email,
        },
        'role': 'reader'
    }
    created_rule = service.acl().insert(calendarId=cal_ID, body=rule).execute()
    print (created_rule['id'])


def create_event(A_date,cal_ID):
    start = A_date.isoformat()
    end = A_date + timedelta(minutes=30)
    end = end.isoformat()
    body={"summary": 'New Appointment', 
        "description": 'An appointment is booked',
        "start": {"dateTime": start, "timeZone": 'Africa/Cairo'}, 
        "end": {"dateTime": end, "timeZone": 'Africa/Cairo'},
        }
    event = service.events().insert(calendarId=cal_ID,body=body).execute()
    return event['id']

def delete_calendar(calendar_ID):
    r=service.calendars().delete(calendarId=calendar_ID).execute()

def delete_event(calendar_ID, event_ID):
    r=service.events().delete(calendarId=calendar_ID, eventId=event_ID).execute()


#listing access control of a calendar
def list_acl (calendar_ID):
    acl = service.acl().list(calendarId=calendar_ID).execute()
    for rule in acl['items']:
        print ((rule['id'], rule['role']))


service = service_build()

# # list calendars
# page_token = None
# while True:
#   calendar_list = service.calendarList().list(pageToken=page_token).execute()
#   for calendar_list_entry in calendar_list['items']:
#     print (calendar_list_entry['id'])
#   page_token = calendar_list.get('nextPageToken')
#   if not page_token:
#     break



