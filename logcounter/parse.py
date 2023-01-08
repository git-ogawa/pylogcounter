import re
from typing import List, Optional, Tuple


class Parser:

    timestamp = "timestamp"
    byte = "bytes"
    line = "line"

    def __init__(self, file: str, timestamp_format: Optional[str] = None) -> None:
        self.file = file
        self.timestamp_format = timestamp_format
        self.timestamp_pattern: Optional[str] = ""
        self.timestamp_type: Optional[str] = None
        self.columns = [Parser.timestamp, Parser.byte, Parser.line]

    def precheck(self) -> None:
        self.set_timestamp_type()

    def set_timestamp_type(self) -> None:
        if self.timestamp_format is not None:
            self.timestamp_type = "custom"
            self.timestamp_pattern = TimeString().convert(self.timestamp_format)
        else:
            with open(self.file, "r") as f:
                _type, _format, _pat = TimeString().extract(f.readline())
            if _type is not None:
                self.timestamp_type = _type
                self.timestamp_pattern = _pat
                self.timestamp_format = _format
            else:
                raise ParserError(f"Timestamp cannot be parsed in {self.file}.")

    def parse(self) -> List[List]:
        pattern = re.compile(f"({self.timestamp_pattern})")
        d = []
        line_num = 0
        with open(self.file, "r") as f:
            line = f.readline()
            line_num += 1
            while line:
                m = pattern.search(line)
                if m is not None:
                    d.append([m.group(1), len(line.encode()), 1])
                else:
                    raise ParserError(f"Timestamp cannot be parsed in line {line_num}.")
                line = f.readline()
                line_num += 1
        return d


class TimeString:
    patterns = [
        {
            "name": "ISO8601",
            "format": "%Y-%m-%dT%H:%M:%S.%fZ",
            "pattern": "[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]{3,6}Z",
        },
        {
            "name": "RFC 3164",
            "format": "%b %m %H:%M:%S",
            "pattern": "[a-zA-Z]{,3}\\s+[0-9]{,2}\\s+[0-9]{2}:[0-9]{2}:[0-9]{2}",
        },
        {
            "name": "general",
            "format": "%Y-%m-%d %H:%M:%S",
            "pattern": "[0-9]{4}-[0-9]{2}-[0-9]{2}\\s+[0-9]{2}:[0-9]{2}:[0-9]{2}",
        },
    ]

    directives = {
        "%a": "[a-zA-Z]{3}",
        "%b": "[a-zA-Z]{3}",
        "%d": "[0-9]{2}",
        "%f": "[0-9]{6}",
        "%G": "[0-9]{4}",
        "%H": "[0-9]{2}",
        "%m": "[0-9]{2}",
        "%M": "[0-9]{2}",
        "%p": "[a-zA-Z]{2}",
        "%S": "[0-9]{2}",
        "%U": "[0-7]{1}",
        "%V": "[0-9]{2}",
        "%w": "[0-6]{1}",
        "%W": "[0-9]{2}",
        "%y": "[0-9]{2}",
        "%Y": "[0-9]{4}",
        "%z": "[+-]{1}[0-9]{4}",
        "%Z": "[a-zA-Z]{3}",
    }

    def __init__(self) -> None:
        pass

    def extract(
        self, string: str
    ) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        for t in TimeString.patterns:
            m = re.search(f"({t['pattern']})", string)
            if m is not None:
                return t["name"], t["format"], t["pattern"]
        return None, None, None

    def convert(self, fmt: str) -> str:
        it = iter(fmt)
        res = ""
        try:
            while True:
                c = next(it)
                if c == "%":
                    c2 = next(it)
                    res += self._directive(c + c2)
                else:
                    res += c
        except KeyError as e:
            raise DirectiveError(f"{e} in {fmt}.") from e
        except StopIteration:
            return res

    def _directive(self, c: str):
        try:
            return TimeString.directives[c]
        except KeyError:
            raise KeyError(f"{c} not found")


class ParserError(Exception):
    pass


class DirectiveError(Exception):
    pass
