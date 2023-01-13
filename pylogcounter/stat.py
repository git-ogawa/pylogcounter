from typing import Dict, Union

import pandas as pd

from pylogcounter.parse import LogLevelParser


class Statistic:

    byte_table = {"b": "Byte", "k": "KB", "m": "MB", "g": "GB", "t": "TB"}

    def __init__(
        self,
        df: pd.DataFrame,
        decimal: int = 10,
        time_unit: str = "",
        byte_unit: str = "b",
    ):
        self.df = df
        self.decimal = decimal
        self.byte_unit = byte_unit
        self.time_unit = time_unit
        self.properties = ["mean", "std", "max", "min", "50%"]

    def extract(self):
        self.df = self.df.round(self.decimal)
        self.total_bytes = self.df["bytes"].sum()
        self.total_lines = len(self.df.index)
        self.start_time = self.df.index[0]
        self.end_time = self.df.index[len(self.df.index) - 1]
        self.timedelta = self._timedelta()

        stat = self.df.describe()
        stat = stat.round(self.decimal)
        self.lines = {p: stat["line"][p] for p in self.properties}
        self.bytes = {p: stat["bytes"][p] for p in self.properties}

        if LogLevelParser.total in self.df.columns:
            self.log_levels = {}
            for level in LogLevelParser.levels:
                data: Dict[str, Dict[str, float]] = {level: {}}
                for prop in self.properties:
                    data[level][prop] = stat[level][prop]
                self.log_levels.update(data)

        self.convert_byte()

    def _timedelta(self) -> int:
        elapse = self.end_time - self.start_time
        return elapse.total_seconds()

    def equal_start_end(self) -> bool:
        start = self.df.index[0]
        end = self.df.index[len(self.df.index) - 1]
        if start == end:
            return True
        return False

    def convert_byte(self):
        self.total_bytes = self._byte(self.total_bytes)

        target = [
            self.bytes,
        ]
        for t in target:
            if isinstance(t, dict):
                for k, v in t.items():
                    t[k] = self._byte(v)

    def _byte(self, val: Union[int, float]) -> float:
        if self.byte_unit == "k":
            return round(float(val / 1024), self.decimal)
        elif self.byte_unit == "m":
            return round(float(val / (1024**2)), self.decimal)
        if self.byte_unit == "g":
            return round(float(val / (1024**3)), self.decimal)
        if self.byte_unit == "t":
            return round(float(val / (1024**4)), self.decimal)
        else:
            return round(float(val), self.decimal)

    def get_unit(self) -> str:
        return Statistic.byte_table.get(self.byte_unit, "Byte")
