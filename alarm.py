import datetime

class Alarm():

    def __init__(self, year: int, month: int, day_of_month: int, hour: int, minute: int):
        self.time = datetime.datetime(year, month, day_of_month, hour, minute)

    def should_play(self) -> bool:
        now = datetime.datetime.now()
        if self.time.year == now.year \
                and self.time.month == now.month \
                and self.time.day == now.day \
                and self.time.hour == now.hour \
                and self.time.minute == now.minute :
            return True
        return False

    def to_datetime(self) -> datetime.datetime:
        return datetime.datetime(self.time.year, self.time.month, self.time.day, self.time.hour, self.time.minute)

    def __str__(self) -> str:
        return "Alarm: [time: {}]".format(self.time)





