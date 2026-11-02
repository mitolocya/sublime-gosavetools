# GoSaveTool for Sublime Text

Subtitle and text tools for Sublime Text 4: convert **SRT ↔ WebVTT**, **shift** and **repair** subtitle timings, see a live **word count** in the status bar, check **social media and SEO character limits**, and change **text case** of any selection.

Made by [GoSaveTool](https://www.gosavetool.com/), free online tools for creators.

## Commands

Open the Command Palette (`Ctrl+Shift+P` / `Cmd+Shift+P`) and type **GoSaveTool**, or use **Tools → GoSaveTool** and the right-click menu.

| Command | What it does |
| --- | --- |
| Word Count and Limits | Words, characters, sentences, lines, reading time and the characters left for X, Instagram, TikTok, YouTube, LinkedIn, Pinterest, SEO title and meta description, for the selection or the file |
| Title Case, Sentence case, UPPERCASE, lowercase | Changes every selection |
| slug, camelCase, snake_case, kebab-case | `Ölçü Birimi` → `olcu-birimi`, `best posting time` → `bestPostingTime` |
| Clean Spaces | Removes trailing spaces, runs of spaces and extra blank lines |
| Subtitles to WebVTT / Subtitles to SRT | Opens the converted file in a new tab |
| Shift Subtitles… | Moves every cue by the seconds you enter (`1.5` later, `-2` earlier) |
| Repair Subtitles | Sorts cues, fixes overlaps and end times before the start, drops empty cues, renumbers |

The status bar shows the word and character count of the selection, or of the file. Turn it off with `"status_bar_count": false` in **Preferences → Package Settings → GoSaveTool**.

Everything runs inside Sublime Text, offline.

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

The tests run without Sublime Text, against small stand-ins for its API. `gosavetool_lib/text.py` gives the same results as [`@gosavetool/text`](https://www.npmjs.com/package/@gosavetool/text) and `gosavetool_lib/subtitles.py` is [`gosavetool-subtitles`](https://pypi.org/project/gosavetool-subtitles/).

## Online tools

[VTT Subtitle Generator](https://www.gosavetool.com/vtt-subtitle-generator), [Auto Captions Generator](https://www.gosavetool.com/auto-captions-generator), [Character Counter](https://www.gosavetool.com/character-counter)

## License

MIT
