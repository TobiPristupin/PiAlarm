import argparse
import datetime
from audio_player import AudioPlayer, Platform
from alarm import Alarm
import os
from overrider import overrides
import calendar_api
import sys

def parse_args() :
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--morning-time", type=int, help="Time at which screen turns to white theme", default=8)
    parser.add_argument("-n", "--night-time", type=int, help="Time at which screen turns to black theme", default=21)
    parser.add_argument("-r", "--refresh-minutes", type=int, help="Minutes between each alarm refresh", default=30)
    parser.add_argument("-a", "--audio-file", type=str, help="path to alarm audio file",
                        default=str(os.path.join("media", "pinkpanther.wav")))
    parser.add_argument("-p", "--platform", type=Platform.from_string, choices=list(Platform), default=Platform.windows,
                        help="""Platform where the program is running. If platforms is windows, it will use winsound as 
                        an audio provider. If platform is linux, it will use aplay for audio and attempt to access the 
                        voicehat drivers""")

    return parser.parse_known_args()


# Because Kivy overrides argv processing, arguments for the program have to be parsed before importing or using
# anything from Kivy. This workaround disables arguments for Kivy.
# See https://groups.google.com/forum/#!topic/kivy-users/dQze67KgASo
args, unknown = parse_args()
sys.argv[1:] = unknown


import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty
from kivy.clock import Clock
from kivy.properties import ListProperty

kivy.require("1.9.1")

if args.morning_time >= args.night_time :
    raise ValueError("Morning time can't be after night time")

black_rgba = [0, 0, 0, 1]
white_rgba = [1, 1, 1, 1]
night_time = args.night_time
morning = args.morning_time
alarm_refresh_minutes = args.refresh_minutes
alarm_audio_path = args.audio_file
audio_out = AudioPlayer(args.platform)

def get_current_time() -> datetime.datetime:
    return datetime.datetime.now()

def alarm_as_display_text(alarm: Alarm) -> str:
    return alarm.to_datetime().strftime("%A %I:%M %p")


class ClockScreen(BoxLayout):

    time_label = ObjectProperty(None)
    alarm_label = ObjectProperty(None)
    background_color = ListProperty(white_rgba)
    time_label_color = ListProperty(black_rgba)
    alarm_label_color = ListProperty(black_rgba)

    def __init__(self, **kwargs):
        super(ClockScreen, self).__init__(**kwargs)
        self.alarm = None
        self.init_button()
        self.set_time()
        self.change_theme()
        self.schedule_callbacks()
        self.refresh_alarm()

    def schedule_callbacks(self):
        Clock.schedule_interval(lambda delta_time: self.set_time(), 1)
        Clock.schedule_interval(lambda delta_time: self.change_theme(), 60)
        Clock.schedule_interval(lambda delta_time: self.check_alarm(), 3)
        Clock.schedule_interval(lambda delta_time: self.refresh_alarm(), alarm_refresh_minutes * 60)

    def init_button(self):
        try :
            import aiy.voicehat
            aiy.voicehat.get_button().on_press(audio_out.stop)
        except :
            print("Unable to access VoiceHat Drivers")

    @overrides(BoxLayout)
    def on_touch_down(self, touch):
        audio_out.stop()

    def check_alarm(self):
        if self.alarm is not None and self.alarm.should_play():
            self.alarm = None
            self.play_alarm()
            # Schedule refresh in 62 seconds, so one minute passes and the alarm just played
            # is not fetched from gcal again
            Clock.schedule_once(lambda delta_time: self.refresh_alarm, 62)

    def play_alarm(self):
        self.set_white_theme()
        audio_out.play_wave(alarm_audio_path)

    def set_time(self):
        self.time_label.text = get_current_time().strftime("%H:%M")

    def change_theme(self):
        if get_current_time().time() > datetime.time(hour=night_time):
            self.set_black_theme()
        elif get_current_time().time() > datetime.time(hour=morning):
            self.set_white_theme()

    def refresh_alarm(self):
        result = calendar_api.get_next_alarm()

        if result[0] is False:
            self.set_alarm_text("No Alarm")
            return

        self.alarm = result[1]
        self.set_alarm_text(alarm_as_display_text(self.alarm))

    def set_black_theme(self):
        self.background_color = black_rgba
        self.time_label_color = white_rgba
        self.alarm_label_color = white_rgba

    def set_white_theme(self):
        self.background_color = white_rgba
        self.time_label_color = black_rgba
        self.alarm_label_color = black_rgba

    def set_alarm_text(self, text: str):
        self.alarm_label.text = text

class AlarmApp(App):

    @overrides(App)
    def build(self):
        return ClockScreen()


def main():
    app = AlarmApp()
    app.run()


if __name__ == "__main__" :
    main()
