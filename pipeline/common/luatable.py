"""Minimal parser for Lua table constructors as used in QuestieDB data files.

Supports: nested tables, [n]=value keys, strings (double/single quoted),
numbers, nil, true/false. Positional entries keep nil holes (None).
Returns dicts with int keys for explicit [n]= entries and for positional ones (1-based).
"""
import re

_WS = re.compile(r"(?:\s+|--[^\n]*)*")
_NUM = re.compile(r"-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?")
_ESC = {"n": "\n", "t": "\t", "r": "\r", "\\": "\\", '"': '"', "'": "'", "0": "\0"}


class LuaParser:
    def __init__(self, text):
        self.s = text
        self.i = 0

    def ws(self):
        self.i = _WS.match(self.s, self.i).end()

    def parse_value(self):
        self.ws()
        c = self.s[self.i]
        if c == "{":
            return self.parse_table()
        if c in "\"'":
            return self.parse_string(c)
        m = _NUM.match(self.s, self.i)
        if m:
            self.i = m.end()
            t = m.group()
            return float(t) if any(x in t for x in ".eE") else int(t)
        for word, val in (("nil", None), ("true", True), ("false", False)):
            if self.s.startswith(word, self.i):
                self.i += len(word)
                return val
        raise ValueError(f"unexpected {self.s[self.i:self.i+30]!r} at {self.i}")

    def parse_string(self, q):
        self.i += 1
        out = []
        while True:
            c = self.s[self.i]
            if c == "\\":
                n = self.s[self.i + 1]
                out.append(_ESC.get(n, n))
                self.i += 2
            elif c == q:
                self.i += 1
                return "".join(out)
            else:
                out.append(c)
                self.i += 1

    def parse_table(self):
        self.i += 1  # {
        result = {}
        pos = 1
        while True:
            self.ws()
            if self.s[self.i] == "}":
                self.i += 1
                return result
            if self.s[self.i] == "[":
                self.i += 1
                key = self.parse_value()
                self.ws()
                assert self.s[self.i] == "]"
                self.i += 1
                self.ws()
                assert self.s[self.i] == "="
                self.i += 1
                result[key] = self.parse_value()
            else:
                val = self.parse_value()
                if val is not None:
                    result[pos] = val
                pos += 1
            self.ws()
            if self.s[self.i] in ",;":
                self.i += 1


def load_data_block(path, var):
    """Load `QuestieDB.<var> = [[return {...}]]` and return the parsed table."""
    text = open(path, encoding="utf-8").read()
    m = re.search(r"QuestieDB\." + re.escape(var) + r"\s*=\s*\[\[return ", text)
    if not m:
        raise ValueError(f"{var} not found in {path}")
    p = LuaParser(text)
    p.i = m.end()
    return p.parse_table()


def load_keys(path, var):
    """Load `QuestieDB.<var> = { ['name'] = 1, ... }` key-name -> index map."""
    text = open(path, encoding="utf-8").read()
    m = re.search(r"QuestieDB\." + re.escape(var) + r"\s*=\s*\{", text)
    end = text.index("\n}", m.end())
    lines = [ln for ln in text[m.end():end].splitlines() if not ln.lstrip().startswith("--")]
    return {k: int(v) for k, v in re.findall(r"\['(\w+)'\]\s*=\s*(\d+)", "\n".join(lines))}
