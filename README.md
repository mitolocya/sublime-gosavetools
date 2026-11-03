# GoSaveTool for Sublime Text

Subtitle tools for Sublime Text 4: convert **SRT ↔ WebVTT**, **shift** and **repair** subtitle timings, change the **case** of cue text, clean up stray **spaces**, and see a live **word and character count** in the status bar while you translate or caption.

Made by [GoSaveTool](https://www.gosavetool.com/), free online tools for creators.

## Commands

Open the Command Palette (`Ctrl+Shift+P` / `Cmd+Shift+P`) and type **GoSaveTool**, or use **Tools → GoSaveTool** and the right-click menu.

| Command | What it does |
| --- | --- |
| Subtitles to WebVTT / Subtitles to SRT | Opens the converted file in a new tab, cues and numbering included |
| Shift Subtitles… | Moves every cue by the seconds you enter (`1.5` later, `-2` earlier) |
| Repair Subtitles | Sorts cues, fixes overlaps and end times before the start, drops empty cues, renumbers |
| Word Count | Words, characters, sentences, lines and reading time for the selection or the file |
| Title Case, Sentence case, UPPERCASE, lowercase | Changes every selection — handy for cue text that arrived in the wrong case |
| Clean Spaces | Removes trailing spaces, runs of spaces and extra blank lines |

The status bar shows the word and character count of the selection, or of the file. Turn it off with `"status_bar_count": false` in **Preferences → Package Settings → GoSaveTool**.

Everything runs inside Sublime Text, offline, with no dependencies.

## What this package is not

It is deliberately limited to subtitles and caption text. It does not count characters against social media or SEO limits, and it does not convert text to `slug`, `camelCase`, `snake_case` or `kebab-case` — those live in the web tools at [gosavetool.com](https://www.gosavetool.com/) instead, so this package stays out of the way of the packages that do those jobs properly.

## Key bindings

The package adds none, so it never clashes with yours. Example for **Preferences → Key Bindings**:

```json
{ "keys": ["ctrl+alt+t"], "command": "gosavetool_case", "args": { "op": "title" } },
{ "keys": ["ctrl+alt+w"], "command": "gosavetool_count" }
```

## Install

Package Control: **Install Package → GoSaveTool**. Manually: copy this folder to your `Packages` folder (**Preferences → Browse Packages…**) and name it `GoSaveTool`.

## Tests

```bash
python -m unittest discover -s tests
```

The tests run without Sublime Text, against small stand-ins for its API. `gosavetool_lib/subtitles.py` is [`gosavetool-subtitles`](https://pypi.org/project/gosavetool-subtitles/) from PyPI.

## Online tools

[VTT Subtitle Generator](https://www.gosavetool.com/vtt-subtitle-generator), [Auto Captions Generator](https://www.gosavetool.com/auto-captions-generator), [Character Counter](https://www.gosavetool.com/character-counter)

## License

MIT
