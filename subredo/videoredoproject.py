from __future__ import annotations

import xml.etree.ElementTree as ET
from abc import abstractmethod
from pathlib import Path

from subredo.timecode import Timecode


class Xml:
    @classmethod
    @abstractmethod
    def load(cls, element: ET.Element):
        ...

    @classmethod
    def loads(cls, xml: str) -> Xml:
        element = ET.fromstring(xml)
        return cls.load(element)

    @abstractmethod
    def dump(self) -> ET.Element:
        ...

    def dumps(self) -> str:
        element = self.dump()
        return ET.tostring(element, encoding="utf-8").decode("utf-8")


class VideoReDoProject(Xml):
    """Root Element of a VideoReDoProject file."""
    def __init__(
        self, version: int, video_redo_version: VideoReDoVersion, filename: Path, description: str,
        stream_type: int, duration: int, sync_adjustment: float, audio_volume_adjust: float,
        cut_mode: bool, video_stream_pid: int, audio_stream_pid: int, project_time: int,
        cut_list: list[Cut], chapter_list: list[ChapterMarker]
    ):
        self.version = version
        self.video_redo_version = video_redo_version
        self.filename = filename
        self.description = description
        self.stream_type = stream_type
        self.duration = duration
        self.sync_adjustment = sync_adjustment
        self.audio_volume_adjust = audio_volume_adjust
        self.cut_mode = cut_mode
        self.video_stream_pid = video_stream_pid
        self.audio_stream_pid = audio_stream_pid
        self.project_time = project_time
        self.cut_list = cut_list
        self.chapter_list = chapter_list

    @classmethod
    def load(cls, element: ET.Element) -> VideoReDoProject:
        version = int(element.get("Version"))
        video_redo_version = VideoReDoVersion.load(element.find("VideoReDoVersion"))
        filename = Path(element.find("Filename").text)
        description = element.find("Description").text
        stream_type = int(element.find("StreamType").text)
        duration = int(element.find("Duration").text)
        sync_adjustment = float(element.find("SyncAdjustment").text)
        audio_volume_adjust = float(element.find("AudioVolumeAdjust").text)
        cut_mode = bool(int(element.find("CutMode").text))
        video_stream_pid = int(element.find("VideoStreamPID").text)
        audio_stream_pid = int(element.find("AudioStreamPID").text)
        project_time = int(element.find("ProjectTime").text)
        cut_list = [
            Cut.load(cut_element)
            for cut_element in element.find("CutList").findall("cut")
        ]
        chapter_list = [
            ChapterMarker.load(chapter_element)
            for chapter_element in element.find("ChapterList").findall("ChapterMarker")
        ]
        return cls(
            version, video_redo_version, filename, description, stream_type,
            duration, sync_adjustment, audio_volume_adjust, cut_mode,
            video_stream_pid, audio_stream_pid, project_time, cut_list, chapter_list
        )

    def dump(self) -> ET.Element:
        element = ET.Element(
            "VideoReDoProject",
            Version=str(self.version)
        )
        element.append(self.video_redo_version.dump())
        ET.SubElement(element, "Filename").text = str(self.filename)
        ET.SubElement(element, "Description").text = self.description
        ET.SubElement(element, "StreamType").text = str(self.stream_type)
        ET.SubElement(element, "Duration").text = str(self.duration)
        ET.SubElement(element, "SyncAdjustment").text = str(self.sync_adjustment)
        ET.SubElement(element, "AudioVolumeAdjust").text = "{:.6f}".format(self.audio_volume_adjust)
        ET.SubElement(element, "CutMode").text = str(int(self.cut_mode))
        ET.SubElement(element, "VideoStreamPID").text = str(self.video_stream_pid)
        ET.SubElement(element, "AudioStreamPID").text = str(self.audio_stream_pid)
        ET.SubElement(element, "ProjectTime").text = str(self.project_time)

        cut_list_element = ET.SubElement(element, "CutList")
        for cut in self.cut_list:
            cut_list_element.append(cut.dump())

        chapter_list_element = ET.SubElement(element, "ChapterList")
        for chapter_marker in self.chapter_list:
            chapter_list_element.append(chapter_marker.dump())

        return element


class VideoReDoVersion(Xml):
    def __init__(self, build_number: int, version: str):
        self.build_number = build_number
        self.version = version

    @classmethod
    def load(cls, element: ET.Element) -> VideoReDoVersion:
        build_number = int(element.get("BuildNumber"))
        version = element.text
        return cls(build_number, version)

    def dump(self) -> ET.Element:
        element = ET.Element(
            "VideoReDoVersion",
            BuildNumber=str(self.build_number)
        )
        element.text = self.version
        return element


class Cut(Xml):
    def __init__(
        self, sequence: int, cut_start: Timecode, cut_end: Timecode, elapsed: Timecode,
        cut_time_start: int, cut_time_end: int, cut_byte_start: int, cut_byte_end: int
    ):
        self.sequence = sequence
        self.cut_start = cut_start
        self.cut_end = cut_end
        self.elapsed = elapsed
        self.cut_time_start = cut_time_start
        self.cut_time_end = cut_time_end
        self.cut_byte_start = cut_byte_start
        self.cut_byte_end = cut_byte_end

    @classmethod
    def load(cls, element: ET.Element) -> Cut:
        sequence = int(element.get("Sequence"))
        cut_start = Timecode.load(element.get("CutStart"))
        cut_end = Timecode.load(element.get("CutEnd"))
        elapsed = Timecode.load(element.get("Elapsed"))
        cut_time_start = int(element.find("CutTimeStart").text)
        cut_time_end = int(element.find("CutTimeEnd").text)
        cut_byte_start = int(element.find("CutByteStart").text)
        cut_byte_end = int(element.find("CutByteEnd").text)
        return cls(
            sequence, cut_start, cut_end, elapsed, cut_time_start,
            cut_time_end, cut_byte_start, cut_byte_end
        )

    def dump(self) -> ET.Element:
        element = ET.Element(
            "cut",
            Sequence=str(self.sequence),
            CutStart=str(self.cut_start),
            CutEnd=str(self.cut_end),
            Elapsed=str(self.elapsed)
        )
        ET.SubElement(element, "CutTimeStart").text = str(self.cut_time_start)
        ET.SubElement(element, "CutTimeEnd").text = str(self.cut_time_end)
        ET.SubElement(element, "CutByteStart").text = str(self.cut_byte_start)
        ET.SubElement(element, "CutByteEnd").text = str(self.cut_byte_end)
        return element


class ChapterMarker(Xml):
    def __init__(self, sequence: int, timecode: str, value: int):
        self.sequence = sequence
        self.timecode = timecode
        self.value = value

    @classmethod
    def load(cls, element: ET.Element) -> ChapterMarker:
        sequence = int(element.get("Sequence"))
        timecode = element.get("Timecode")
        value = int(element.text)
        return cls(sequence, timecode, value)

    def dump(self) -> ET.Element:
        element = ET.Element(
            "ChapterMarker",
            Sequence=str(self.sequence),
            Timecode=self.timecode
        )
        element.text = str(self.value)
        return element
