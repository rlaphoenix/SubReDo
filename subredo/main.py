from __future__ import annotations

import math
import platform
import shutil
import sys
import tempfile
import time
from pathlib import Path
from typing import Optional

import click
from rich.status import Status
from rich import print
from pymediainfo import MediaInfo
from rich.table import Table

from subredo.helpers import mux_subtitles, Subtitle, offset_subtitle, cut_subtitle
from subredo.timestamp import Timestamp
from subredo.videoredoproject import VideoReDoProject


@click.command()
@click.argument("projects", type=Path, nargs=-1)
@click.option("-o", "--original-language", type=str, default="en",
              help="Declare the Original Language for this Video's Subtitle flags.")
@click.option("-c", "--cut-video", type=Path, default=None,
              help="Specify manually exported cut video from the VideoReDo project file to mux the Subtitles to."
                   "Otherwise, On Windows a new MKV will be automatically exported next to the project file.")
@click.option("-k", "--keep-cut", is_flag=True, default=False,
              help="Keep the original Cut Video after multiplexing a Cut Video with the Subtitles.")
@click.option("-o", "--offset", type=int, default=0,
              help="Initial Subtitle Sync adjustment offset in milliseconds. Must be 0 or greater.")
def main(projects: list[Path], original_language: str, cut_video: Optional[Path], keep_cut: bool, offset: int):
    """
    Apply Cuts from a VideoReDo Project File on Subtitles.

    \b
    PROJECTS    One or more VideoReDo project files (.Vprj) to read and apply cuts from.
                You can alternatively specify a folder to search for .Vprj files from.
                Subtitles are read from the source file of each project.
    """
    project_files = [
        project_file
        for x in projects
        for project_file in (x.glob("*.Vprj") if x.is_dir() else [x])
    ]

    cut_video_ = cut_video

    if cut_video and len(project_files) > 1:
        print("[Error]: Batch mode does not support -c/--cut-video.")
        sys.exit(1)

    for project in project_files:
        print(f"Processing {project.name}")

        video_redo_project = VideoReDoProject.loads(project.read_text(encoding="utf8"))
        subs_folder = Path("subs")
        cut_video = cut_video_

        mediainfo = MediaInfo.parse(video_redo_project.filename)
        video_track = mediainfo.video_tracks[0]
        subtitles = mediainfo.text_tracks

        duration = Timestamp.from_milliseconds(video_redo_project.duration / 10000)
        fps = int(video_track.framerate_num) / int(video_track.framerate_den)
        frame_time = (1 / fps) * 1000
        frame_time_int = math.ceil(frame_time)

        keep_timestamps = []
        elapsed = Timestamp.from_milliseconds(0)

        if not cut_video:
            if platform.system() == "Windows":
                from subredo.videoredocom import VideoReDo
                with Status("Exporting the VideoReDo Project to MKV...") as status:
                    cut_video = project.with_stem(f"{project.stem} (SubReDo)").with_suffix(".mkv")
                    vrd = VideoReDo()
                    if not vrd.file_open(project):
                        raise ValueError(f"Failed to open Project File \"{project}\"")
                    if not vrd.file_save_as(cut_video, "Matroska MKV"):
                        raise ValueError(f"Failed to save Video to \"{cut_video}\"")
                    while vrd.vrd.OutputGetState != 0:
                        status.update(f"Exporting the VideoReDo Project to MKV ({vrd.output_get_percent_complete:.2f}%)...")
                        time.sleep(0.2)
            else:
                cut_video = project.with_suffix(".mkv")
                if not cut_video.exists():
                    print("[ERROR]: Unable to automatically determine the path to the Cut Video export.")
                    sys.exit(1)

        cuts_table = Table(title="Project Segments")
        cuts_table.add_column("#", justify="right", style="cyan", no_wrap=True)
        cuts_table.add_column("Start", style="magenta")
        cuts_table.add_column("End", style="magenta")
        cuts_table.add_column("Difference", justify="right", style="green")
        cuts_table.add_column("Note", justify="right")

        segment_i = 0
        if video_redo_project.cut_mode:
            # TODO: Seems to be used even in Scene editing mode?
            for cut in video_redo_project.cut_list:
                cut_start = Timestamp.from_timecode(cut.cut_start, fps)
                cut_end = Timestamp.from_timecode(cut.cut_end, fps)
                if cut_start == cut_end:
                    # it didn't cut away anything duration-wise, likely header data, skip
                    print(f"Ignoring Cut #{cut.sequence} as it's a duration-less cut and will not affect Subtitles")
                    continue

                cut_duration = cut_end - cut_start

                note = ""
                if cut_duration.total_milliseconds() <= frame_time_int:
                    note = "1 frame long"
                elif cut_duration.total_milliseconds() < 1000:
                    note = "less than 1 second long"

                if elapsed < cut_start:
                    a, b = elapsed, cut_start - frame_time
                    keep_timestamps.append((a, b))
                    segment_i += 1
                    cuts_table.add_row(f"{segment_i}", str(a), str(b), f"{b - a}")

                segment_i += 1
                cuts_table.add_row(
                    f"[bold red]-[/] {segment_i}", str(cut_start), str(cut_end), f"-{cut_duration}",
                    note
                )

                elapsed = cut_end
        else:
            raise NotImplementedError("Scene Edit Mode is not yet supported...")

        if elapsed < duration:
            segment_i += 1
            a, b = elapsed, duration
            keep_timestamps.append((a, b))
            cuts_table.add_row(f"{segment_i}", str(a), str(b), f"{b - a}")

        print(cuts_table)

        final_duration = Timestamp.from_milliseconds(0)
        for a, b in keep_timestamps:
            final_duration += b - a
        print("Final Duration:", final_duration)

        if subs_folder.exists():
            shutil.rmtree(subs_folder)
        subs_folder.mkdir(parents=True)

        for sub in subtitles:
            with Status(f"Processing Subtitle #{sub.stream_identifier + 1} ({sub.language} {sub.title or ''})..."):
                # Use FFMPEG to make the cuts, use SubEdit to rebase it's offset
                final_srt_file = subs_folder / f"sub_{sub.track_id}_{sub.language}_{sub.title}_cuts.srt"
                with tempfile.TemporaryDirectory(prefix="rlaphoenix-subredo") as tmp_dir:
                    tmp_dir = Path(tmp_dir)
                    segment_offset = Timestamp.from_milliseconds(offset)
                    for i, (a, b) in enumerate(keep_timestamps):
                        sub_file = tmp_dir / f"sub_{sub.track_id}_{sub.language}_{sub.title}_{i}.srt"
                        cut_subtitle(
                            video_path=video_redo_project.filename,
                            out_path=sub_file,
                            sub_id=sub.stream_identifier,
                            start=a,
                            end=b
                        )
                        offset_subtitle(sub_file, segment_offset)
                        segment_offset += (b - a)
                    merged_srt_data = "\n".join([
                        srt.read_text(encoding="utf8")
                        for srt in tmp_dir.glob("*.srt")
                        if srt.stat().st_size > 0
                    ])
                    if len(merged_srt_data) > 0:
                        final_srt_file.write_text(merged_srt_data, encoding="utf8")

        with Status("Muxing Subtitles to MKV..."):
            cut_with_subs = cut_video.with_stem(cut_video.stem + " (with Subs)")
            cut_with_subs.unlink(missing_ok=True)
            subs = [
                Subtitle(
                    path=subs_folder / f"sub_{sub.track_id}_{sub.language}_{sub.title}_cuts.srt",
                    name=sub.title,
                    language=sub.language,
                    forced=sub.forced == "Yes",
                    default=sub.default == "Yes",
                    sdh="SDH" in (sub.title or ""),
                    original_lang=sub.language == original_language
                )
                for sub in subtitles
            ]
            mux_subtitles(cut_video, cut_with_subs, subs)

        if not keep_cut:
            cut_video.unlink()
        shutil.rmtree(subs_folder)

    print(":tada: Done!")


if __name__ == "__main__":
    main()
