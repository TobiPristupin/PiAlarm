import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty
from kivy.clock import Clock
from kivy.core.audio import SoundLoader

kivy.require("1.9.1")

import datetime
import httplib2
import os
import argparse
import dateutil.parser
import pygame
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

	

class GoogleCalendarManager():
	
	flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
	scopes = 'https://www.googleapis.com/auth/calendar.readonly'
	client_secret_file = 'client_secret.json'
	application_name = 'PiAlarm'

	def get_credentials(self):
	    """Gets valid user credentials from storage.
	    If nothing has been stored, or if the stored credentials are invalid,
	    the OAuth2 flow is completed to obtain the new credentials.
	    Returns:
	        Credentials, the obtained credential.
	    """
	    home_dir = os.path.expanduser('~')
	    credential_dir = os.path.join(home_dir, '.credentials')
	    if not os.path.exists(credential_dir):
	        os.makedirs(credential_dir)
	    credential_path = os.path.join(credential_dir,
	                                   'calendar-python-quickstart.json')

	    store = Storage(credential_path)
	    credentials = store.get()
	    if not credentials or credentials.invalid:
	        flow = client.flow_from_clientsecrets(self.client_secret_file, self.scopes)
	        flow.user_agent = self.application_name
	        if self.flags:
	            credentials = tools.run_flow(flow, store, self.flags)
	    return credentials

	def get_next_alarm(self):
		credentials = self.get_credentials()
		http = credentials.authorize(httplib2.Http())
		service = discovery.build('calendar', 'v3', http=http)
		
		now = datetime.datetime.utcnow().isoformat() + 'Z' 
		week_from_now = str(datetime.datetime.today().date() + datetime.timedelta(weeks=1) ) + "T00:00:00Z"
		#ID of PiAlarm dedicated calendar
		calendar_id = "u38uqb2rt2fr3drka35jopmsho@group.calendar.google.com"
		#Send query to Google Cal API. Filter events one week from current time.
		eventsResult = service.events().list(
        	calendarId=calendar_id, timeMin=now, timeMax=week_from_now, maxResults=1, singleEvents=True,
        	orderBy='startTime', q="PiAlarm Wake").execute()
		
		events = eventsResult.get('items', [])

		if not events :
			return None
		
		for event in events :
			#Get start time of event
			start_time = event['start'].get('dateTime', event['start'].get('date'))

		return self.utc_to_alarm(start_time)		

	#Extracts hour and minute from string utc time into Alarm object.
	def utc_to_alarm(self, utc_datetime):
		datetime = dateutil.parser.parse(utc_datetime)
		return Alarm(datetime.month, datetime.day, datetime.hour, datetime.minute)		
		

class ClockScreen(BoxLayout):
	
	time_label = ObjectProperty(None)
	alarm_label = ObjectProperty(None)
	calendar_manager = GoogleCalendarManager()

	def __init__(self, **kwargs):
		super(ClockScreen, self).__init__(**kwargs)
		self.alarm = None
		self.set_time()
		self.refresh_alarm()
		#Schedules callback to change time label time every 60 seconds
		Clock.schedule_interval(self.set_time, 1)
		#Schecules callback to check if should play alarm
		Clock.schedule_interval(self.check_alarm, 2)
		#Schedules callback to refresh alarm from Google Calendar every 30 minutes
		Clock.schedule_interval(self.refresh_alarm, 1800)


	def set_time(self, *args): 
		self.time_label.text = datetime.datetime.now().strftime("%H:%M")

	def set_next_alarm_text(self, has_alarm):
		if has_alarm :
			date = datetime.datetime(datetime.datetime.now().year, self.alarm.month,
				self.alarm.day_of_month, self.alarm.hour)
			if date.hour < 12 :
				time_period = "AM"
			else :
				time_period = "PM"	 
			
			self.alarm_label.text = "{} {}:{:02d} {}".format(date.strftime("%A"), date.hour, self.alarm.minute, time_period)
		else :
			self.alarm_label.text = "No Alarm"	

	def on_touch_down(self, touch):
		if pygame.mixer.get_init() != None and pygame.mixer.music.get_busy() :
			pygame.mixer.music.stop()
			pygame.mixer.quit()

	def check_alarm(self, *args):
		if self.alarm != None and self.alarm.should_play():
			self.play_alarm()
			self.alarm = None
			#Schedule refresh in 62 seconds, to pass through current min and prevent setting alarm to same one.
			Clock.schedule_once(self.refresh_alarm, 62)

	def play_alarm(self):
		pygame.mixer.init()
		pygame.mixer.music.load("plegaria.mp3")
		pygame.mixer.music.play(1)

	def refresh_alarm(self, *args):
		self.alarm = self.calendar_manager.get_next_alarm()
		if self.alarm == None :
			self.set_next_alarm_text(False)
		else :
			self.set_next_alarm_text(True)	



class Alarm():
	
	def __init__(self, month, day_of_month, hour, minute):
		self.hour = hour
		self.minute = minute
		self.day_of_month = day_of_month
		self.month = month

	#Checks if alarm should be played
	def should_play(self):
		time = datetime.datetime.now().today()
		if (self.hour == time.hour and self.minute == time.minute 
			and self.day_of_month == time.day and self.month == time.month) :
			return True
		
		return False



class AlarmApp(App):
	pass


if __name__ == "__main__" :
	AlarmApp().run()



