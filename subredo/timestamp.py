from __future__ import annotations

import math
from typing import Union

from subredo.timecode import Timecode


class Timestamp:
    def __init__(self, hours: int, minutes: int, seconds: int, ms: Union[int, float]):
        self.hours = hours
        self.minutes = minutes
        self.seconds = seconds
        self.ms = ms

        if self.ms < 1:
            self.ms *= 1000

    def __str__(self) -> str:
        return f"{self.hours:02}:{self.minutes:02}:{self.seconds:02}.{int(self.ms)}"

    def __lt__(self, other: Timestamp) -> bool:
        return self.total_milliseconds() < other.total_milliseconds()

    def __le__(self, other: Timestamp) -> bool:
        return self.total_milliseconds() <= other.total_milliseconds()

    def __gt__(self, other: Timestamp) -> bool:
        return self.total_milliseconds() > other.total_milliseconds()

    def __ge__(self, other: Timestamp) -> bool:
        return self.total_milliseconds() >= other.total_milliseconds()

    def __eq__(self, other: Timestamp) -> bool:
        return self.total_milliseconds() == other.total_milliseconds()

    def __ne__(self, other: Timestamp) -> bool:
        return self.total_milliseconds() != other.total_milliseconds()

    def __add__(self, other: Union[Timestamp, int]) -> Timestamp:
        total_ms = self.total_milliseconds()
        if isinstance(other, Timestamp):
            total_ms += other.total_milliseconds()
        else:
            total_ms += other
        return self.from_milliseconds(total_ms)

    def __sub__(self, other: Union[Timestamp, int]) -> Timestamp:
        total_ms = self.total_milliseconds()
        if isinstance(other, Timestamp):
            total_ms -= other.total_milliseconds()
        else:
            total_ms -= other
        return self.from_milliseconds(total_ms)

    @classmethod
    def load(cls, value: str) -> Timestamp:
        time, ms = value.split(".")
        hours, minutes, seconds = map(int, time.split(":"))
        ms = float(f"0.{ms}")
        return cls(hours, minutes, seconds, ms)

    @classmethod
    def from_timecode(cls, timecode: Timecode, fps: Union[int, float]):
        frame_time = 1 / fps  # time each frame is displayed on screen
        frame_stamp = frame_time * timecode.frame
        ms = frame_stamp
        return cls(timecode.hours, timecode.minutes, timecode.seconds, ms)

    @classmethod
    def from_milliseconds(cls, total_ms: Union[int, float]) -> Timestamp:
        hours, remainder = divmod(total_ms, 3600000)
        minutes, remainder = divmod(remainder, 60000)
        seconds, ms = divmod(remainder, 1000)
        hours, minutes, seconds = int(hours), int(minutes), int(seconds)
        return cls(hours, minutes, seconds, ms)

    def total_milliseconds(self) -> int:
        return math.floor(
            self.hours * 3600000 +
            self.minutes * 60000 +
            self.seconds * 1000 +
            self.ms
        )
