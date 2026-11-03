"""python -m unittest discover -s tests  (from the package folder; Sublime Text is not needed)"""
import importlib
import json
import re
import sys
import types
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Load the package as "GoSaveTool" so its relative imports work, with small stand-ins for the sublime modules
sublime = types.ModuleType("sublime")
sublime.messages = []
sublime.status_message = sublime.messages.append
sublime.load_settings = lambda name: {"status_bar_count": True}


class Region:
    def __init__(self, a, b=None):
        self.a, self.b = a, a if b is None else b

    def begin(self):
        return min(self.a, self.b)

    def end(self):
        return max(self.a, self.b)

    def empty(self):
        return self.a == self.b


sublime.Region = Region
plugin_mod = types.ModuleType("sublime_plugin")
plugin_mod.TextCommand = type("TextCommand", (), {"__init__": lambda self, view: setattr(self, "view", view)})
plugin_mod.EventListener = type("EventListener", (), {})
sys.modules.update(sublime=sublime, sublime_plugin=plugin_mod)
pkg = types.ModuleType("GoSaveTool")
pkg.__path__ = [str(ROOT)]
sys.modules["GoSaveTool"] = pkg
plugin = importlib.import_module("GoSaveTool.gosavetool")
txt = importlib.import_module("GoSaveTool.gosavetool_lib.text")
sub = importlib.import_module("GoSaveTool.gosavetool_lib.subtitles")


class View:
    """A buffer with selections, enough for the commands"""

    def __init__(self, text, sel=()):
        self.text, self.selections, self.status = text, [Region(a, b) for a, b in sel], {}
        self.win = Window()

    def size(self):
        return len(self.text)

    def substr(self, r):
        return self.text[r.begin():r.end()]

    def sel(self):
        return self.selections

    def replace(self, edit, r, s):
        self.text = self.text[:r.begin()] + s + self.text[r.end():]

    def window(self):
        return self.win

    def file_name(self):
        return "C:\\videos\\talk.srt"

    def set_status(self, key, value):
        self.status[key] = value

    def erase_status(self, key):
        self.status.pop(key, None)

    def run_command(self, name, args=None):
        if name == "append":
            self.text += args["characters"]
        elif name == "gosavetool_subtitles_shift":
            plugin.GosavetoolSubtitlesShiftCommand(self).run(None, **args)

    def set_name(self, name):
        self.name = name


class Window:
    def __init__(self):
        self.files, self.commands = [], []

    def new_file(self):
        v = View("")
        self.files.append(v)
        return v

    def create_output_panel(self, name):
        self.panel = View("")
        return self.panel

    def run_command(self, name, args=None):
        self.commands.append((name, args))

    def show_input_panel(self, caption, initial, done, change, cancel):
        self.input = done


SRT = "1\n00:00:02,000 --> 00:00:01,000\nB\n\n2\n00:00:00,500 --> 00:00:01,500\nA\n"


class Text(unittest.TestCase):
    """The checks of @gosavetool/text, against the Python port"""

    def test_stats(self):
        self.assertEqual(txt.stats("Hello world. It’s 2026!"), {"words": 4, "chars": 23, "charsNoSpaces": 20, "lines": 1, "sentences": 2, "readSeconds": 1})
        st = txt.stats("Hello world. It’s 2026!\nSecond line.")
        self.assertEqual([st["words"], st["lines"], st["sentences"]], [6, 2, 3])
        self.assertEqual(txt.stats("")["lines"], 0)
        self.assertEqual(txt.stats("well-known co_op don't")["words"], 3)
        self.assertEqual(txt.stats(" ".join(["w"] * 119))["readSeconds"], 30)  # 29.99… rounds up

    def test_cases(self):
        self.assertEqual(txt.title("the lord of the rings: return of the king"), "The Lord of the Rings: Return of the King")
        self.assertEqual(txt.title("it's a dog's life"), "It's a Dog's Life")
        self.assertEqual(txt.sentence("HELLO WORLD. how ARE you?"), "Hello world. How are you?")
        self.assertEqual(txt.words("HTMLParser v2Beta"), ["HTMLParser", "v2", "Beta"])
        self.assertEqual(txt.clean("a   b  \n\n\n\nc\t"), "a b\n\nc")
        self.assertEqual(txt.clean("a  \r\n\r\n\r\n\r\nb"), "a\r\n\r\nb")

    def test_no_developer_or_seo_helpers(self):
        """The package is subtitle and caption text only: no SEO limits, no identifier cases"""
        for name in ("limits", "LIMITS", "slug", "camel", "snake", "kebab"):
            self.assertFalse(hasattr(txt, name), name)


class Commands(unittest.TestCase):
    def test_case_on_selections(self):
        v = View("the lord of the rings and HELLO", [(0, 21), (26, 31), (3, 3)])
        plugin.GosavetoolCaseCommand(v).run(None, op="title")
        self.assertEqual(v.text, "The Lord of the Rings and Hello")
        v = View("abc")
        plugin.GosavetoolCaseCommand(v).run(None, op="upper")
        self.assertEqual(sublime.messages[-1], "GoSaveTool: select some text first")
        plugin.GosavetoolCaseCommand(v).run(None, op="__class__")
        self.assertEqual(v.text, "abc")

    def test_removed_operations_do_nothing(self):
        v = View("Best Posting Time", [(0, 17)])
        for op in ("slug", "camel", "snake", "kebab"):
            plugin.GosavetoolCaseCommand(v).run(None, op=op)
            self.assertEqual(v.text, "Best Posting Time", op)
            self.assertIn("unknown operation", sublime.messages[-1])

    def test_count_panel(self):
        v = View("Hello world. Again!")
        plugin.GosavetoolCountCommand(v).run(None)
        self.assertIn("Words: 3", v.win.panel.text)
        self.assertIn("Reading time", v.win.panel.text)
        self.assertNotIn("Character limits", v.win.panel.text)
        self.assertEqual(v.win.commands[-1], ("show_panel", {"panel": "output.gosavetool"}))

    def test_subtitles(self):
        v = View(SRT)
        plugin.GosavetoolSubtitlesConvertCommand(v).run(None, to="vtt")
        out = v.win.files[0]
        self.assertTrue(out.text.startswith("WEBVTT"))
        self.assertEqual(out.name, "talk.vtt")
        plugin.GosavetoolSubtitlesRepairCommand(v).run(None)
        self.assertTrue(v.text.startswith("1\n00:00:00,500 --> 00:00:01,500\nA"))
        self.assertEqual(sublime.messages[-1], "GoSaveTool: 2 problems fixed")
        plugin.GosavetoolSubtitlesShiftCommand(v).run(None)
        v.win.input("1,5")
        self.assertIn("00:00:02,000 --> 00:00:03,000\nA", v.text)
        v.win.input("soon")
        self.assertIn("enter a number", sublime.messages[-1])
        empty = View("no cues")
        plugin.GosavetoolSubtitlesRepairCommand(empty).run(None)
        self.assertEqual(empty.text, "no cues")

    def test_status_bar(self):
        v = View("one two three", [(0, 3)])
        plugin.GosavetoolStatusListener().on_selection_modified_async(v)
        self.assertEqual(v.status["gosavetool"], "1 words, 3 chars selected")
        v.selections = [Region(0)]
        plugin.GosavetoolStatusListener().on_selection_modified_async(v)
        self.assertEqual(v.status["gosavetool"], "3 words, 13 chars")


class Files(unittest.TestCase):
    def test_menus_name_real_commands(self):
        names = {re.sub(r"(?<!^)(?=[A-Z])", "_", c.__name__[:-7]).lower() for c in vars(plugin).values()
                 if isinstance(c, type) and c.__name__.endswith("Command")}
        for f in ("Default.sublime-commands", "Context.sublime-menu", "Main.sublime-menu"):
            data = json.loads((ROOT / f).read_text("utf-8"))
            found = re.findall(r'"command": "(gosavetool_\w+)"', json.dumps(data))
            self.assertTrue(found, f)
            for cmd in found:
                self.assertIn(cmd, names, f)
            for op in re.findall(r'"op": "(\w+)"', json.dumps(data)):
                self.assertIn(op, plugin.CASE_OPS)

    def test_menus_have_no_removed_labels(self):
        for f in ("Default.sublime-commands", "Context.sublime-menu", "Main.sublime-menu"):
            data = (ROOT / f).read_text("utf-8")
            for word in ("slug", "camelCase", "snake_case", "kebab-case", "SEO", "Instagram"):
                self.assertNotIn(word, data, f)


if __name__ == "__main__":
    unittest.main()
