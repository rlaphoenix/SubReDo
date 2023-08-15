from __future__ import annotations

import math
import shutil
import tempfile
from pathlib import Path

import click
from rich.status import Status
from rich import print
from pymediainfo import MediaInfo

from subredo.helpers import mux_subtitles, Subtitle, offset_subtitle, cut_subtitle
from subredo.timestamp import Timestamp
from subredo.videoredoproject import VideoReDoProject


@click.command()
@click.argument("project", type=Path)
@click.argument("cut_video", type=Path)
@click.option("-o", "--original-language", type=str, default="en",
              help="Declare the Original Language for this Video's Subtitle flags.")
def main(project: Path, cut_video: Path, original_language: str):
    """
    Apply Cuts from a VideoReDo Project File on Subtitles.

    \b
    PROJECT     The VideoReDo project file (.Vprj) to read and apply cuts from.
                Subtitles are read from the source file of the project.
    CUT_VIDEO   The exported video from the VideoReDo project file to mux the
                Subtitles to. Must be MKV.
    """
    video_redo_project = VideoReDoProject.loads(project.read_text(encoding="utf8"))
    subs_folder = Path("subs")

    mediainfo = MediaInfo.parse(video_redo_project.filename)
    video_track = mediainfo.video_tracks[0]
    subtitles = mediainfo.text_tracks

    duration = Timestamp.from_milliseconds(video_redo_project.duration / 10000)
    fps = int(video_track.framerate_num) / int(video_track.framerate_den)
    frame_time = (1 / fps) * 1000
    frame_time_int = math.ceil(frame_time)

    keep_timestamps = []
    elapsed = Timestamp.from_milliseconds(0)

    if video_redo_project.cut_mode:
        # TODO: Seems to be used even in Scene editing mode?
        for cut in video_redo_project.cut_list:
            cut_start = Timestamp.from_timecode(cut.cut_start, fps)
            cut_end = Timestamp.from_timecode(cut.cut_end, fps)
            if cut_start == cut_end:
                # it didn't cut away anything duration-wise, likely header data, skip
                print(f"Cut {cut.sequence}: SKIPPED (duration-less cut)")
                continue

            cut_duration = cut_end - cut_start

            warning = None
            if cut_duration.total_milliseconds() <= frame_time_int:
                warning = "1 frame long"
            elif cut_duration.total_milliseconds() < 1000:
                warning = "less than 1 second long"

            print(
                f"Cut {cut.sequence}", cut_start, "-->", cut_end, f"(-{cut_duration})",
                f"[WARNING: {warning}]" if warning else ""
            )

            if elapsed < cut_start:
                keep_timestamps.append((elapsed, cut_start - frame_time))

            elapsed = cut_end
    else:
        raise NotImplementedError("Scene Edit Mode is not yet supported...")

    if elapsed < duration:
        keep_timestamps.append((elapsed, duration))

    print("Keeping Captions in the following Segments:")
    for a, b in keep_timestamps:
        print(" ", a, "-->", b, f"({b - a})")

    if subs_folder.exists():
        shutil.rmtree(subs_folder)
    subs_folder.mkdir(parents=True)

    for sub in subtitles:
        with Status(f"Processing Subtitle #{sub.stream_identifier + 1} ({sub.language} {sub.title or ''})..."):
            # Use FFMPEG to make the cuts, use SubEdit to rebase it's offset
            final_srt_file = subs_folder / f"sub_{sub.track_id}_{sub.language}_{sub.title}_cuts.srt"
            with tempfile.TemporaryDirectory(prefix="rlaphoenix-subredo") as tmp_dir:
                tmp_dir = Path(tmp_dir)
                offset = keep_timestamps[0][0]
                for i, (a, b) in enumerate(keep_timestamps):
                    sub_file = tmp_dir / f"sub_{sub.track_id}_{sub.language}_{sub.title}_{i}.srt"
                    cut_subtitle(
                        video_path=video_redo_project.filename,
                        out_path=sub_file,
                        sub_id=sub.stream_identifier,
                        start=a,
                        end=b
                    )
                    offset_subtitle(sub_file, offset)
                    offset += (b - a)
                final_srt_file.write_text(
                    "\n".join([
                        srt.read_text(encoding="utf8")
                        for srt in tmp_dir.glob("*.srt")
                    ]),
                    encoding="utf8"
                )

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
        for sub in subs:
            sub.path.unlink()

    print(":tada: Done!")


if __name__ == "__main__":
    main()
