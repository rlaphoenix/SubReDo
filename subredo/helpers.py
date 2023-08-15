import subprocess
from pathlib import Path

from subredo.timestamp import Timestamp


class Subtitle:
    """Generic data container for Subtitles."""
    def __init__(
        self, path: Path, name: str, language: str, forced: bool,
        default: bool, sdh: bool, original_lang: bool
    ):
        self.path = path
        self.name = name
        self.language = language
        self.forced = forced
        self.default = default
        self.sdh = sdh
        self.original_lang = original_lang


def cut_subtitle(video_path: Path, out_path: Path, sub_id: int, start: Timestamp, end: Timestamp) -> int:
    """
    Trim/Cut the Subtitle track to only the Start to End timestamps.

    Note: FFMPEG will offset all output caption timestamps at `00:00:00.000`.
          You may want to also use offset_subtitle().
    """
    return subprocess.check_call([
        "ffmpeg",
        "-y",
        "-hide_banner",
        "-loglevel", "error",
        "-i", video_path,
        "-map", f"0:s:{sub_id}",
        "-ss", str(start),
        "-to", str(end),
        out_path
    ])


def offset_subtitle(subtitle_path: Path, offset: Timestamp) -> int:
    """Offset Timestamps of Subtitle Captions in-place."""
    if subtitle_path.stat().st_size == 0:
        # nothing to offset and SubtitleEdit complains
        return 0
    return subprocess.check_call([
        "SubtitleEdit",
        "/convert", subtitle_path,
        "srt",
        f"/offset:{str(offset).replace('.', ':')}",
        "/overwrite"
    ], stdout=subprocess.DEVNULL)


def mux_subtitles(video_path: Path, out_path: Path, subtitles: list[Subtitle]) -> int:
    """Mux one or more Subtitles into an MKV container."""
    cli = [
        "mkvmerge",
        video_path,
        "-o", out_path
    ]

    for subtitle in subtitles:
        cli.extend([
            "--track-name", f"0:{subtitle.name or ''}",
            "--language", f"0:{subtitle.language}",
            "--sub-charset", "0:UTF-8",
            "--forced-track", f"0:{subtitle.forced}",
            "--default-track", f"0:{subtitle.default}",
            "--hearing-impaired-flag", f"0:{subtitle.sdh}",
            "--original-flag", f"0:{subtitle.original_lang}",
            "--compression", "0:none",  # disable extra compression (probably zlib)
            "(", str(subtitle.path), ")"
        ])

    return subprocess.check_call(cli)
