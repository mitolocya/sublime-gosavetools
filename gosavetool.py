"""GoSaveTool for Sublime Text: SRT and WebVTT subtitle tools, word counter with social media limits, case changes.

https://www.gosavetool.com/
"""
import os

import sublime
import sublime_plugin

from .gosavetool_lib import subtitles as sub
from .gosavetool_lib import text as txt

CASE_OPS = ("title", "sentence", "upper", "lower", "slug", "camel", "snake", "kebab", "clean")
NAMES = {
    "x-post": "X post", "instagram-caption": "Instagram caption", "tiktok-caption": "TikTok caption",
    "youtube-title": "YouTube title", "youtube-description": "YouTube description", "linkedin-post": "LinkedIn post",
    "pinterest-description": "Pinterest description", "seo-title": "SEO title", "meta-description": "Meta description",
}
# Live counts in the status bar stop above this size, to keep typing fast in big files
LIVE_LIMIT = 2000000


def whole(view):
    return sublime.Region(0, view.size())


def selected_or_whole(view):
    """The selected regions, or the whole file when nothing is selected"""
    regions = [r for r in view.sel() if not r.empty()]
    return regions or [whole(view)]


def report(view, text):
    st = txt.stats(text)
    lines = [
        "Words: {words:,}".format(**st),
        "Characters: {chars:,}  (without spaces: {charsNoSpaces:,})".format(**st),
        "Sentences: {sentences:,}   Lines: {lines:,}".format(**st),
        "Reading time: {} min {} s".format(st["readSeconds"] // 60, st["readSeconds"] % 60),
        "",
        "Character limits:",
    ]
    for key, lim in txt.limits(text).items():
        lines.append("  {:<22} {:>5}  {}".format(NAMES[key], lim["limit"], "%d left" % lim["left"] if lim["fits"] else "%d over" % -lim["left"]))
    lines += ["", "Online counter: https://www.gosavetool.com/character-counter"]
    return "\n".join(lines)


class GosavetoolCaseCommand(sublime_plugin.TextCommand):
    """Changes the case of each selection: title, sentence, upper, lower, slug, camel, snake, kebab or clean"""

    def run(self, edit, op="title"):
        if op not in CASE_OPS:
            return sublime.status_message("GoSaveTool: unknown operation " + op)
        regions = [r for r in self.view.sel() if not r.empty()]
        if not regions:
            return sublime.status_message("GoSaveTool: select some text first")
        # From the end, so earlier regions keep their positions
        for r in sorted(regions, key=lambda r: r.begin(), reverse=True):
            before = self.view.substr(r)
            after = getattr(txt, op)(before)
            if after != before:
                self.view.replace(edit, r, after)


class GosavetoolCountCommand(sublime_plugin.TextCommand):
    """Words, characters, reading time and social media limits of the selection or the file"""

    def run(self, edit):
        text = "\n".join(self.view.substr(r) for r in selected_or_whole(self.view))
        panel = self.view.window().create_output_panel("gosavetool")
        panel.run_command("append", {"characters": report(self.view, text)})
        self.view.window().run_command("show_panel", {"panel": "output.gosavetool"})


class GosavetoolSubtitlesConvertCommand(sublime_plugin.TextCommand):
    """Opens the file converted to SRT or WebVTT in a new tab"""

    def run(self, edit, to="vtt"):
        src = self.view.substr(whole(self.view))
        cues = sub.parse(src)
        if not cues:
            return sublime.status_message("GoSaveTool: no SRT or WebVTT cues in this file")
        out = self.view.window().new_file()
        out.run_command("append", {"characters": sub.convert(src, to)})
        name = os.path.splitext(os.path.basename(self.view.file_name() or "subtitles"))[0]
        out.set_name(name + "." + to)
        sublime.status_message("GoSaveTool: {} cues converted to {}".format(len(cues), "WebVTT" if to == "vtt" else "SRT"))

    def is_enabled(self, to="vtt"):
        return self.view.size() > 0


class GosavetoolSubtitlesShiftCommand(sublime_plugin.TextCommand):
    """Moves every cue by a number of seconds (asked for when not given)"""

    def run(self, edit, seconds=None):
        if seconds is None:
            self.view.window().show_input_panel("Shift subtitles by seconds (1.5 = later, -2 = earlier):", "", self.on_done, None, None)
            return
        src = self.view.substr(whole(self.view))
        cues = sub.parse(src)
        if not cues:
            return sublime.status_message("GoSaveTool: no SRT or WebVTT cues in this file")
        moved = sub.shift(cues, int(round(float(seconds) * 1000)))
        self.view.replace(edit, whole(self.view), sub.to_vtt(moved) if sub.is_vtt(src) else sub.to_srt(moved))
        sublime.status_message("GoSaveTool: moved {} s".format(seconds))

    def on_done(self, value):
        try:
            seconds = float(value.replace(",", "."))
        except ValueError:
            return sublime.status_message("GoSaveTool: enter a number of seconds, like 1.5 or -2")
        self.view.run_command("gosavetool_subtitles_shift", {"seconds": seconds})


class GosavetoolSubtitlesRepairCommand(sublime_plugin.TextCommand):
    """Sorts cues, fixes overlaps and bad times, drops empty cues, renumbers"""

    def run(self, edit):
        src = self.view.substr(whole(self.view))
        cues = sub.parse(src)
        if not cues:
            return sublime.status_message("GoSaveTool: no SRT or WebVTT cues in this file")
        fixed, n = sub.repair(cues)
        self.view.replace(edit, whole(self.view), sub.to_vtt(fixed) if sub.is_vtt(src) else sub.to_srt(fixed))
        sublime.status_message("GoSaveTool: " + ("%d problems fixed" % n if n else "no problems found"))


class GosavetoolStatusListener(sublime_plugin.EventListener):
    """Word and character count of the selection, or of the file, in the status bar"""

    def on_selection_modified_async(self, view):
        if not sublime.load_settings("GoSaveTool.sublime-settings").get("status_bar_count", True):
            return view.erase_status("gosavetool")
        regions = [r for r in view.sel() if not r.empty()]
        if not regions and view.size() > LIVE_LIMIT:
            return view.erase_status("gosavetool")
        text = "\n".join(view.substr(r) for r in regions) if regions else view.substr(whole(view))
        st = txt.stats(text)
        view.set_status("gosavetool", "{:,} words, {:,} chars{}".format(st["words"], st["chars"], " selected" if regions else ""))

    on_activated_async = on_selection_modified_async
