"""Word, character and reading-time counts, case changes, URL slugs and whitespace cleanup. No dependencies.

The Python version of @gosavetool/text: https://www.gosavetool.com/character-counter
"""
import re
import unicodedata

__all__ = ["LIMITS", "stats", "limits", "words", "upper", "lower", "title", "sentence", "slug", "camel", "snake", "kebab", "clean"]

SMALL = {"a", "an", "and", "as", "at", "but", "by", "for", "in", "nor", "of", "on", "or", "so", "the", "to", "up", "yet", "via", "vs"}

# Character limits of common fields; SEO values are the length search results show before cutting
LIMITS = {
    "x-post": 280,
    "instagram-caption": 2200,
    "tiktok-caption": 4000,
    "youtube-title": 100,
    "youtube-description": 5000,
    "linkedin-post": 3000,
    "pinterest-description": 500,
    "seo-title": 60,
    "meta-description": 160,
}

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


def limits(s, only=None):
    """How each limit is met: {'x-post': {'limit': 280, 'used': 120, 'left': 160, 'fits': True}, ...}"""
    used = len(s)
    return {k: {"limit": n, "used": used, "left": n - used, "fits": used <= n} for k, n in LIMITS.items() if not only or k in only}


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


_SLUG_MAP = {"ı": "i", "İ": "i", "ş": "s", "Ş": "s", "ğ": "g", "Ğ": "g", "ç": "c", "Ç": "c", "ö": "o", "Ö": "o",
             "ü": "u", "Ü": "u", "ß": "ss", "æ": "ae", "ø": "o", "đ": "d", "ł": "l"}


def slug(s):
    """'Ölçü Birimi & Çeviri!' -> 'olcu-birimi-ceviri'"""
    s = "".join(_SLUG_MAP.get(c, c) for c in s)
    s = re.sub(r"[̀-ͯ]", "", unicodedata.normalize("NFKD", s)).lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def camel(s):
    return "".join(w.lower() if i == 0 else w[0].upper() + w[1:].lower() for i, w in enumerate(words(s)))


def snake(s):
    return "_".join(w.lower() for w in words(s))


def kebab(s):
    return "-".join(w.lower() for w in words(s))


def clean(s):
    """Trailing spaces, runs of spaces and more than one blank line in a row."""
    nl = "\r\n" if "\r\n" in s else "\n"
    lines = [re.sub(r"(\S)[ \t]{2,}", r"\1 ", re.sub(r"[ \t]+$", "", line)) for line in re.split(r"\r\n|\n", s)]
    return re.sub("(" + re.escape(nl) + "){3,}", nl + nl, nl.join(lines))
