from pathlib import Path
from typing import Dict, List

import pandas as pd

from pylogcounter.parse import LogLevelParser


class BaseCounter:
    kind = "Base"
    time_unit = ""

    def __init__(self, data: List[List], columns: List, timestamp_format: str) -> None:
        self.df = pd.DataFrame(data, columns=columns)
        self.time_format = timestamp_format
        self.set_time_index()

    def set_time_index(self) -> None:
        self.df.index = pd.to_datetime(self.df["timestamp"], format=self.time_format)
        self.df = self.df.drop(["timestamp"], axis=1)

    def count(self) -> None:
        self.total_bytes = self.df["bytes"].sum()
        self.total_lines = len(self.df.index)
        self.start_time = self.df.index[0]
        self.end_time = self.df.index[len(self.df.index) - 1]
        self.timedelta = self._timedelta()

        stat = self.df.describe()
        self.properties = ["mean", "std", "max", "min", "50%"]
        self.lines = {p: stat["line"][p] for p in self.properties}
        self.bytes = {p: stat["bytes"][p] for p in self.properties}

        if LogLevelParser.total in self.df.columns:
            self.log_levels = {}
            for level in LogLevelParser.levels:
                data: Dict[str, Dict[str, float]] = {level: {}}
                for prop in self.properties:
                    data[level][prop] = stat[level][prop]
                self.log_levels.update(data)

    def _timedelta(self) -> int:
        elapse = self.end_time - self.start_time
        return elapse.total_seconds()

    def _resample(self, unit: str, method: str = "mean") -> None:
        r = self.df.resample(unit, origin="start")
        # Sum dataframe
        _sum = r.sum(numeric_only=True)
        self.df = _sum

    def to_csv(self, base_dir: str = ".") -> str:
        p = Path(base_dir)
        p.mkdir(exist_ok=True)

        path = p / f"{self.kind.lower()}.csv"
        self.df.to_csv(path)
        return str(path)

    def _replace(self, x: str, level: str) -> int:
        if x == level:
            return 1
        else:
            return 0

    def split_log_columns(self) -> None:
        for level in LogLevelParser.levels:
            tmp = self.df.copy()
            try:
                col = tmp["log_level"].apply(lambda x: self._replace(x, level))
                self.df[level] = col
            except KeyError:
                raise KeyError("Columns 'log_level' dose not exist in dataframe.")

        # Add total count
        self.add_total_column()

    def add_total_column(self) -> None:
        self.df[LogLevelParser.total] = self.df[LogLevelParser.levels].sum(axis=1)


class TotalCounter(BaseCounter):
    kind = "Total"
    unit = ""
    time_unit = ""

    def __init__(self, df: pd.DataFrame) -> None:
        self.df = df


class SecondCounter(BaseCounter):
    unit = "1S"
    kind = "Second"
    time_unit = "sec"

    def __init__(self, df: pd.DataFrame) -> None:
        self.df = df

    def resample(self):
        super()._resample(SecondCounter.unit)

    def count(self) -> None:
        super().count()


class MinutelyCounter(BaseCounter):
    unit = "1min"
    kind = "Minutely"
    time_unit = "min"

    def __init__(self, df: pd.DataFrame) -> None:
        self.df = df

    def resample(self):
        super()._resample(MinutelyCounter.unit)

    def count(self) -> None:
        super().count()


class HourlyCounter(BaseCounter):
    unit = "1H"
    kind = "Hourly"
    time_unit = "hour"

    def __init__(self, df: pd.DataFrame) -> None:
        self.df = df

    def resample(self):
        super()._resample(HourlyCounter.unit)

    def count(self) -> None:
        super().count()


class DailyCounter(BaseCounter):
    unit = "1D"
    kind = "Daily"
    time_unit = "day"

    def __init__(self, df: pd.DataFrame) -> None:
        self.df = df

    def resample(self):
        super()._resample(DailyCounter.unit)

    def count(self) -> None:
        super().count()


class WeeklyCounter(BaseCounter):
    unit = "1W"
    kind = "Weekly"
    time_unit = "week"

    def __init__(self, df: pd.DataFrame) -> None:
        self.df = df

    def resample(self):
        super()._resample(WeeklyCounter.unit)

    def count(self) -> None:
        super().count()

    def to_csv(self) -> None:
        super().to_csv()
