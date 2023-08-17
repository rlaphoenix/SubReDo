# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2023-08-17

### Added

- The cut video export will now try to be automatically determined if not explicitly provided.
- Multiple Project files can now be specified in a single call, as well as one or more folders
  containing Project files. (Note: Specifying the cut-video path is not currently supported in
  this mode).
- Implemented `-o/--offset` so you can specify an offset for each subtitle caption. This sync
  adjustment can only be NIL or a positive integer. It cannot be negative. If you need negative
  sync adjustment, use FFmpeg or MKVToolNix.
- Windows: The Project file will be automatically exported using the default `Matroska MKV` profile
  if a path to a cut video export is not explicitly provided. Supports VideoReDo 5, 6, and 6 Pro.

### Changed

- The original cut video export is now deleted after processing is successful unless `-k/--keep-cut`
  is passed.
- The argument `CUT_VIDEO` was removed and replaced with an optional `-c/--cut-video` option.
- Padded the milliseconds value to 3 digits on the Timestamp string representation.
- The list of cut segments and kept segments are now one aligned list in order, and now using a
  rich table for readability. Cut segments are now denoted by a red `-` mark next to the segment
  number.
- One-frame Cut segments are now completely ignored, as if it wasn't listed in the Project file.
  This is because that frame isn't actually cut out of the file, nor should it be. It's seemingly
  just a poor way for VideoReDo to separate one continuous scene into two explicitly defined
  segments that the user made.

### Fixed

- Subtitles may have had UTF-8-BOM marks after being processed by SubtitleEdit, resulting in a
  possibly corrupt or dodgy Subtitle file. SubtitleEdit now explicitly works with UTF-8 (no BOM)
  and exports as UTF-8 (no BOM).
- Fixed crash when no captions ended up on one or more of the Subtitle tracks within the cut
  segments. I.e. if the cut-out video segments were the only portions of video that would
  have contained captions for that track.
- Fixed subtitle caption timestamps when the first cut was not at `00:00:00.000`.
- Kept segment start timestamps now start one frame AFTER what was cut or kept, not on the last
  frame of the previous cut or kept segment. Effectively fixing a 1 frame desync.
- Timestamps can no longer be subtracted past 0 milliseconds. This behaviour was possible but
  not supported nor intended. The result will not be way you expect, therefore I have explicitly
  removed the ability to do so.
- Now using the project file's `CutTimeStart` and `CutTimeEnd` millisecond values instead of the
  `CutStart` and `CutEnd` timecodes as I cannot figure out how to convert them accurately to a
  Timestamp. The millisecond values were way more easily convertible to frame-accurate Timestamps.
- Segment Start and End timestamps were shifted forward by 1 frame. The end timestamp would
  actually be the timestamp of the frame AFTER the cut seen on the VideoReDo GUI; and the start
  timestamp would have actually been 1 frame AFTER what it was meant to begin at.

## [1.0.0] - 2023-08-15

Initial release.

[1.1.0]: https://github.com/rlaphoenix/SubReDo/releases/tag/v1.1.0
[1.0.0]: https://github.com/rlaphoenix/SubReDo/releases/tag/v1.0.0
