# SubReDo

Apply Cuts from a VideoReDo Project File to Subtitles.

[VideoReDo] allows you to make frame-accurate cuts without re-encoding the entire video or audio file. However, it does
not keep or cut Subtitles. That's where SubReDo comes in! Save your VideoReDo Project File (.Vprj) and pass it to
SubReDo, and it will apply the same cuts but on the Subtitle files.

> **Note**
> - Currently only SubRip (SRT) subtitles and Matroska Cut Exports are supported.<br/>

  [VideoReDo]: <https://www.videoredo.com>

## Features

- Export VideoReDo Project to MKV automatically **(Windows Only)**
- Automatically Mux Subtitle Cuts to MKV Video Cut Exports
- Subtitle Flags and Metadata from Original Source are Retained

## Dependencies

- [FFmpeg](https://ffmpeg.org) for cutting the Subtitles at specific calculated timestamps.
- [SubtitleEdit](https://nikse.dk/subtitleedit) for offsetting the Subtitle captions to sync up with the Cut video.

Please make sure `ffmpeg` and `SubtitleEdit` can be found on your `PATH` Environment Variable, in your Current
Working Directory, or in SubReDo's Installation directory.

## Usage

```
Usage: subredo [OPTIONS] [PROJECTS]...

  Apply Cuts from a VideoReDo Project File on Subtitles.

  PROJECTS    One or more VideoReDo project files (.Vprj) to read and apply cuts from.
              You can alternatively specify a folder to search for .Vprj files from.
              Subtitles are read from the source file of each project.

Options:
  -o, --original-language TEXT  Declare the Original Language for this Video's
                                Subtitle flags.
  -c, --cut-video PATH          Specify manually exported cut video from the
                                VideoReDo project file to mux the Subtitles
                                to.Otherwise, On Windows a new MKV will be
                                automatically exported next to the project
                                file.
  -k, --keep-cut                Keep the original Cut Video after multiplexing
                                a Cut Video with the Subtitles.
  --help                        Show this message and exit.
```

## Contributors

<a href="https://github.com/rlaphoenix"><img src="https://images.weserv.nl/?url=avatars.githubusercontent.com/u/17136956?v=4&h=25&w=25&fit=cover&mask=circle&maxage=7d" alt=""/></a>

## License

© 2023 rlaphoenix — [GNU General Public License, Version 3.0](LICENSE)
