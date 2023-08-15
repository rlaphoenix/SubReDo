from __future__ import annotations


class Timecode:
    def __init__(self, hours: int, minutes: int, seconds: int, frame: int):
        self.hours = hours
        self.minutes = minutes
        self.seconds = seconds
        self.frame = frame

    def __str__(self) -> str:
        return f"{self.hours:02}:{self.minutes:02}:{self.seconds:02};{self.frame:02}"

    @classmethod
    def load(cls, value: str) -> Timecode:
        time, frame = value.split(";")
        hours, minutes, seconds = map(int, time.split(":"))
        frame = int(frame)
        return cls(hours, minutes, seconds, frame)
