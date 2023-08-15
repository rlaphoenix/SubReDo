# SubReDo

Apply Cuts from a VideoReDo Project File to Subtitles.

[VideoReDo] allows you to make frame-accurate cuts without re-encoding the entire video or audio file. However, it does
not keep or cut Subtitles. That's where SubReDo comes in! Save your VideoReDo Project File (.Vprj) and pass it to
SubReDo, and it will apply the same cuts but on the Subtitle files.

> **Note**
> - Currently only SubRip (SRT) subtitles and Matroska Cut Exports are supported.<br/>

  [VideoReDo]: <https://www.videoredo.com>

## Features

- Automatically Muxes Subtitle Cuts to Video Cut Export
- Subtitle Flags and Metadata from Original Source are Retained

## Dependencies

- [FFmpeg](https://ffmpeg.org) for cutting the Subtitles at specific calculated timestamps.
- [SubtitleEdit](https://nikse.dk/subtitleedit) for offsetting the Subtitle captions to sync up with the Cut video.

Please make sure `ffmpeg` and `SubtitleEdit` can be found on your `PATH` Environment Variable, in your Current
Working Directory, or in SubReDo's Installation directory.

## Usage

```
Usage: subredo [OPTIONS] PROJECT CUT_VIDEO

  Apply Cuts from a VideoReDo Project File to Subtitles.

  PROJECT     The VideoReDo project file (.Vprj) to read and apply cuts from.
              Subtitles are read from the source file of the project.
  CUT_VIDEO   The exported video from the VideoReDo project file to mux the
              Subtitles to. Must be MKV.

Options:
  -o, --original-language TEXT  Declare the Original Language for this Video's
                                Subtitle flags.
  --help                        Show this message and exit.
```

## Contributors

<a href="https://github.com/rlaphoenix"><img src="https://images.weserv.nl/?url=avatars.githubusercontent.com/u/17136956?v=4&h=25&w=25&fit=cover&mask=circle&maxage=7d" alt=""/></a>

## License

© 2023 rlaphoenix — [GNU General Public License, Version 3.0](LICENSE)
