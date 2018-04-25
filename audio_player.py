import subprocess
from enum import Enum

class Platform(Enum):
    windows = 1
    linux = 2

    def __str__(self):
        return self.name

    @staticmethod
    def from_string(string: str):
        try :
            return Platform[string]
        except KeyError :
            raise ValueError()


# Class that handles audio output for linux, voicehat drivers and windows. Because winsound is only available in
#  windows, it can only be used before having checked that the platform is windows and it has to be imported each time.
class AudioPlayer():

    def __init__(self, platform=Platform.linux):
        self.platform = platform
        self.process = None

    def play_wave(self, path_to_wave: str):
        self.stop() # Avoid overlapping audio files
        if self.platform is Platform.linux :
            self.process = subprocess.Popen(["aplay", str(path_to_wave)])
        elif self.platform is Platform.windows :
            import winsound
            winsound.PlaySound(path_to_wave, winsound.SND_FILENAME | winsound.SND_ASYNC)

    def stop(self):
        if self.platform is Platform.linux and self.process is not None :
            self.process.terminate()
            self.process = None
        elif self.platform is Platform.windows :
            import winsound
            winsound.PlaySound(None, winsound.SND_PURGE)




