import os
import argparse
from typing import Dict
from alarm import Alarm
import httplib2
import dateutil.parser
import datetime
from googleapiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
import tzlocal

scopes = 'https://www.googleapis.com/auth/calendar.readonly'
client_secret_file = 'client_secret.json'
application_name = 'PiAlarm'
calendar_id = "u38uqb2rt2fr3drka35jopmsho@group.calendar.google.com"
event_id = "PiAlarm Wake"
iso_8601_suffix = "T00:00:00Z"

def get_next_alarm() -> (bool, Alarm):
    try :
        event = __get_gcal_events()
    except :
        return False, None

    if not event :
        return False, None

    start_time = __parse_start_time(event[0])

    # Event will only hold one value because the query will only get the
    # first event. It is maintained as a list just in case the query is modified
    # to return more than one event
    return True, __utc_to_alarm(start_time)

def __get_gcal_events() -> Dict:
    service = __get_service()
    now = datetime.datetime.now(tzlocal.get_localzone()).isoformat("T")
    week_from_now = str(datetime.datetime.today().date() + datetime.timedelta(weeks=1)) + iso_8601_suffix

    query = __query_calendar(service, now, week_from_now)
    events = query["items"]
    return events

def __query_calendar(service, time_start: str, time_end: str):
    result = service.events().list(
        calendarId=calendar_id, timeMin=time_start, timeMax=time_end, maxResults=1,
        singleEvents=True, orderBy='startTime', q=event_id).execute()

    return result

def __parse_start_time(event: Dict) -> str:
    return event["start"].get("dateTime", event["start"].get("date"))

def __utc_to_alarm(utc_datetime: str) -> Alarm:
    time = dateutil.parser.parse(utc_datetime)
    return Alarm(time.year, time.month, time.day, time.hour, time.minute)


def __get_credentials():
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')

    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)

    credential_path = os.path.join(credential_dir, 'calendar-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()

    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(client_secret_file, scopes)
        flow.user_agent = application_name
        flags = tools.argparser.parse_args(args=[])
        if flags:
            credentials = tools.run_flow(flow, store, flags)

    return credentials


def __get_service():
    credentials = __get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)
    return service




