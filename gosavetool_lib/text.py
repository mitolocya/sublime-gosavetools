"""Word, character and reading-time counts, case changes and whitespace cleanup for subtitle text. No dependencies.

The Python version of @gosavetool/text: https://www.gosavetool.com/character-counter
"""
import re

__all__ = ["stats", "words", "upper", "lower", "title", "sentence", "clean"]

SMALL = {"a", "an", "and", "as", "at", "but", "by", "for", "in", "nor", "of", "on", "or", "so", "the", "to", "up", "yet", "via", "vs"}

# A letter or digit, then letters, digits, apostrophes, underscores or hyphens (counted words)
_WORD = re.compile(r"[^\W_][\w'’-]*")
# A letter or digit, then letters, digits or apostrophes (words for Title Case)
_TITLE_WORD = re.compile(r"[^\W_](?:[^\W_]|['’])*")
_SENTENCE = re.compile(r"[^.!?…]+[.!?…]+")


def stats(s):
    """Words, characters, lines, sentences and reading time (238 words a minute) of a text."""
    words_ = len(_WORD.findall(s))
    return {
        "words": words_,
        "chars": len(s),
        "charsNoSpaces": len(re.sub(r"\s", "", s)),
        "lines": 0 if s == "" else len(re.split(r"\r\n|\r|\n", s)),
        "sentences": len(_SENTENCE.findall(s)),
        # Half up, as JavaScript's Math.round
        "readSeconds": int(words_ / 238 * 60 + 0.5),
    }


def words(s):
    """'bestPostingTime 2' -> ['best', 'Posting', 'Time', '2']"""
    spaced = "".join(" " + c if i and c.isupper() and (s[i - 1].islower() or s[i - 1].isnumeric()) else c for i, c in enumerate(s))
    return [w for w in re.split(r"[\W_]+", spaced) if w]


def upper(s):
    return s.upper()


def lower(s):
    return s.lower()


def title(s):
    """'the lord of the rings: return of the king' -> 'The Lord of the Rings: Return of the King'"""
    low = s.lower()
    out, last, first = [], 0, True
    for m in _TITLE_WORD.finditer(low):
        w = m.group(0)
        after_colon = re.search(r"[:.!?]\s*$", s[:m.start()]) is not None
        if first or after_colon or w not in SMALL:
            w = w[0].upper() + w[1:]
        out.append(low[last:m.start()] + w)
        last, first = m.end(), False
    return "".join(out) + low[last:]


def sentence(s):
    """'HELLO WORLD. how ARE you?' -> 'Hello world. How are you?'"""
    return re.sub(r"(^\s*|[.!?…]\s+)([^\W\d_])", lambda m: m.group(1) + m.group(2).upper(), s.lower())


def clean(s):
    """Trailing spaces, runs of spaces and more than one blank line in a row."""
    nl = "\r\n" if "\r\n" in s else "\n"
    lines = [re.sub(r"(\S)[ \t]{2,}", r"\1 ", re.sub(r"[ \t]+$", "", line)) for line in re.split(r"\r\n|\n", s)]
    return re.sub("(" + re.escape(nl) + "){3,}", nl + nl, nl.join(lines))
