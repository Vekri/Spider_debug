"""Find spelling mistakes in code comments, strings, and documents."""

from __future__ import annotations

import keyword
import re
from dataclasses import dataclass
from pathlib import Path
from typing import TypedDict

from spellchecker import SpellChecker

# Classic typos the dictionary often "fixes" into the wrong real word.
COMMON: dict[str, str] = {
    "accomodate": "accommodate",
    "acheive": "achieve",
    "adress": "address",
    "adresses": "addresses",
    "arguement": "argument",
    "availble": "available",
    "becuase": "because",
    "begining": "beginning",
    "beleive": "believe",
    "calcluate": "calculate",
    "calcluates": "calculates",
    "comming": "coming",
    "concious": "conscious",
    "definately": "definitely",
    "documnet": "document",
    "enviroment": "environment",
    "excercise": "exercise",
    "existance": "existence",
    "fourty": "forty",
    "freind": "friend",
    "funciton": "function",
    "funtion": "function",
    "goverment": "government",
    "grammer": "grammar",
    "harrass": "harass",
    "improt": "import",
    "independant": "independent",
    "knowlege": "knowledge",
    "langauge": "language",
    "lenght": "length",
    "liason": "liaison",
    "maintainance": "maintenance",
    "mesage": "message",
    "millenium": "millennium",
    "mispelled": "misspelled",
    "neccessary": "necessary",
    "noticable": "noticeable",
    "occassion": "occasion",
    "occassionally": "occasionally",
    "occured": "occurred",
    "paragragh": "paragraph",
    "persistant": "persistent",
    "posession": "possession",
    "preceed": "precede",
    "priviledge": "privilege",
    "pronounciation": "pronunciation",
    "publically": "publicly",
    "reccomend": "recommend",
    "recieve": "receive",
    "recieved": "received",
    "refered": "referred",
    "retrun": "return",
    "rythm": "rhythm",
    "sentance": "sentence",
    "seperate": "separate",
    "seperated": "separated",
    "sieze": "seize",
    "speling": "spelling",
    "sucess": "success",
    "sucessful": "successful",
    "suprise": "surprise",
    "teh": "the",
    "thier": "their",
    "tommorow": "tomorrow",
    "tounge": "tongue",
    "truely": "truly",
    "untill": "until",
    "wich": "which",
    "widht": "width",
    "wierd": "weird",
    "writting": "writing",
}

# Real technical tokens that are not in an English word list.
TECHNICAL = (
    "args",
    "kwargs",
    "dataframe",
    "filename",
    "filepath",
    "streamlit",
    "numpy",
    "pandas",
    "sklearn",
    "docstring",
    "todo",
    "async",
    "elif",
    "nonlocal",
    "init",
    "bool",
    "dict",
    "tuple",
    "str",
    "int",
    "json",
    "html",
    "css",
    "url",
    "api",
    "idx",
    "tmp",
    "cfg",
    "stdout",
    "stderr",
    "stdin",
    "argv",
    "regex",
    "dataframe",
    "dtype",
    "iloc",
    "dropna",
    "fillna",
    "groupby",
    "utf",
    "ascii",
    "oauth",
    "config",
    "venv",
    "repo",
    "src",
    "dest",
    "param",
    "params",
    "attrs",
    "obj",
    "nums",
    "cols",
    "rows",
    "vals",
    "func",
    "var",
    "env",
    "pip",
    "git",
    "cli",
    "gui",
    "cpu",
    "gpu",
    "auth",
    "jwt",
    "token",
    "hash",
    "http",
    "https",
    "www",
    "png",
    "jpg",
    "pdf",
    "csv",
    "xml",
    "yaml",
    "yml",
    "txt",
    "sql",
    "nosql",
    "docker",
    "linux",
    "windows",
    "macos",
    "isinstance",
    "issubclass",
    "getattr",
    "setattr",
    "hasattr",
    "staticmethod",
    "classmethod",
    "dataclass",
    "abstractmethod",
    "self",
    "cls",
    "df",
    "pd",
    "np",
    "ui",
    "ux",
    "id",
    "uuid",
    "js",
    "ts",
    "py",
    "md",
    "db",
    "os",
    "io",
    "app",
    "apps",
    "btn",
    "msg",
    "err",
    "ok",
    "len",
    "repr",
    "eval",
    "exec",
    "vars",
    "dir",
    "abs",
    "min",
    "max",
    "sum",
    "zip",
    "map",
    "hex",
    "bin",
    "oct",
    "ord",
    "chr",
    "iter",
    "next",
    "type",
    "super",
    "open",
    "read",
    "write",
    "seek",
    "flush",
    "close",
    "append",
    "extend",
    "insert",
    "remove",
    "clear",
    "copy",
    "keys",
    "items",
    "values",
    "update",
    "split",
    "join",
    "strip",
    "lower",
    "upper",
    "title",
    "format",
    "encode",
    "decode",
    "replace",
    "startswith",
    "endswith",
    "isdigit",
    "isalpha",
    "isinstance",
    "print",
    "input",
    "range",
    "enumerate",
    "sorted",
    "reversed",
    "any",
    "all",
    "filter",
    "round",
    "float",
    "list",
    "set",
    "dict",
    "tuple",
    "bool",
    "object",
    "property",
    "lambda",
    "none",
    "true",
    "false",
)

_LETTERS = re.compile(r"[A-Za-z]+")
_CAMEL = re.compile(r"[A-Z]+(?=[A-Z][a-z])|[A-Z]?[a-z]+|[A-Z]+")
_PY = {".py", ".pyw"}
_C_LIKE = {
    ".js",
    ".mjs",
    ".cjs",
    ".ts",
    ".tsx",
    ".jsx",
    ".java",
    ".c",
    ".h",
    ".cpp",
    ".hpp",
    ".cs",
    ".go",
    ".rs",
    ".css",
    ".scss",
    ".php",
    ".rb",
    ".swift",
    ".kt",
}
MAX_FIXES = 80


class Fix(TypedDict):
    start: int
    end: int
    original: str
    corrected: str
    line: int


@dataclass(frozen=True)
class SpellReport:
    fixes: list[Fix]
    limited: bool


def build_checker() -> SpellChecker:
    spell = SpellChecker(language="en", distance=2)
    spell.word_frequency.load_words(TECHNICAL)
    return spell


def language_for(filename: str) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix in _PY:
        return "python"
    if suffix in _C_LIKE:
        return "c"
    return "document"


def apply_fixes(text: str, fixes: list[Fix]) -> str:
    parts: list[str] = []
    cursor = 0
    for fix in fixes:
        parts.append(text[cursor : fix["start"]])
        parts.append(fix["corrected"])
        cursor = fix["end"]
    parts.append(text[cursor:])
    return "".join(parts)


def find_fixes(text: str, filename: str, spell: SpellChecker) -> SpellReport:
    language = language_for(filename)
    prose = _prose_mask(text, language)
    skip = _skip_words()
    fixes: list[Fix] = []
    limited = False

    for match in _LETTERS.finditer(text):
        for start, piece in _pieces(match.start(), match.group()):
            if len(fixes) >= MAX_FIXES:
                limited = True
                break
            in_prose = any(prose[index] for index in range(start, start + len(piece)))
            corrected = _suggest(spell, piece, in_prose=in_prose, skip=skip)
            if not corrected or corrected == piece:
                continue
            fixes.append(
                {
                    "start": start,
                    "end": start + len(piece),
                    "original": piece,
                    "corrected": corrected,
                    "line": text.count("\n", 0, start) + 1,
                }
            )
        if limited:
            break

    return SpellReport(fixes=fixes, limited=limited)


def _pieces(start: int, token: str) -> list[tuple[int, str]]:
    if token.isupper() or token.islower() or len(token) < 5:
        return [(start, token)]
    return [
        (start + piece.start(), piece.group()) for piece in _CAMEL.finditer(token)
    ]


def _suggest(
    spell: SpellChecker,
    word: str,
    *,
    in_prose: bool,
    skip: set[str],
) -> str | None:
    lower = word.lower()
    if lower in COMMON:
        return _match_case(word, COMMON[lower])
    if lower in skip or word.isupper() or len(lower) < 4:
        return None
    if lower in spell:
        return None
    if not in_prose and len(lower) < 6:
        return None

    candidates = spell.candidates(lower) or set()
    best: str | None = None
    best_rank: tuple[int, int, int, str] | None = None
    for candidate in candidates:
        if candidate == lower or candidate in skip:
            continue
        distance = _levenshtein(lower, candidate)
        if distance == 0 or distance > (2 if in_prose else 1):
            continue
        prefix = _common_prefix(lower, candidate)
        if distance == 1 and prefix < 2:
            continue
        if distance == 2 and prefix < 4:
            continue
        if not in_prose and prefix < 3:
            continue
        rank = (distance, -prefix, -int(spell[candidate]), candidate)
        if best_rank is None or rank < best_rank:
            best_rank = rank
            best = candidate
    if best is None:
        return None
    return _match_case(word, best)


def _match_case(source: str, replacement: str) -> str:
    if source.isupper():
        return replacement.upper()
    if source[0].isupper():
        return replacement[:1].upper() + replacement[1:]
    return replacement


def _common_prefix(left: str, right: str) -> int:
    count = 0
    for a, b in zip(left, right):
        if a != b:
            break
        count += 1
    return count


def _levenshtein(left: str, right: str) -> int:
    if left == right:
        return 0
    if not left:
        return len(right)
    if not right:
        return len(left)
    previous = list(range(len(right) + 1))
    for i, left_char in enumerate(left, start=1):
        current = [i]
        for j, right_char in enumerate(right, start=1):
            insert = current[j - 1] + 1
            delete = previous[j] + 1
            replace = previous[j - 1] + (left_char != right_char)
            current.append(min(insert, delete, replace))
        previous = current
    return previous[-1]


def _skip_words() -> set[str]:
    skip = {word.lower() for word in keyword.kwlist}
    skip.update(word.lower() for word in TECHNICAL)
    return skip


def _prose_mask(text: str, language: str) -> bytearray:
    if language == "document":
        return bytearray(b"\x01") * len(text)

    mask = bytearray(len(text))
    index = 0
    size = len(text)
    while index < size:
        if language == "python" and text.startswith(("'''", '"""'), index):
            quote = text[index : index + 3]
            _mark(mask, index, index + 3)
            index += 3
            while index < size and not text.startswith(quote, index):
                mask[index] = 1
                if text[index] == "\\" and index + 1 < size:
                    mask[index + 1] = 1
                    index += 2
                    continue
                index += 1
            if index < size:
                _mark(mask, index, index + 3)
                index += 3
            continue

        if text[index] in {"'", '"'}:
            quote = text[index]
            mask[index] = 1
            index += 1
            while index < size and text[index] not in {quote, "\n"}:
                mask[index] = 1
                if text[index] == "\\" and index + 1 < size and text[index + 1] != "\n":
                    mask[index + 1] = 1
                    index += 2
                    continue
                index += 1
            if index < size and text[index] == quote:
                mask[index] = 1
                index += 1
            continue

        if language == "python" and text[index] == "#":
            while index < size and text[index] != "\n":
                mask[index] = 1
                index += 1
            continue

        if language == "c" and text.startswith("//", index):
            while index < size and text[index] != "\n":
                mask[index] = 1
                index += 1
            continue

        if language == "c" and text.startswith("/*", index):
            while index < size and not text.startswith("*/", index):
                mask[index] = 1
                index += 1
            if index < size:
                mask[index] = 1
                if index + 1 < size:
                    mask[index + 1] = 1
                index += 2
            continue

        index += 1
    return mask


def _mark(mask: bytearray, start: int, end: int) -> None:
    end = min(end, len(mask))
    for index in range(start, end):
        mask[index] = 1
