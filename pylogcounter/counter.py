from pathlib import Path
from typing import List

import pandas as pd


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
        self.mean_lines = stat["line"]["mean"]
        self.mean_lines_std = stat["line"]["std"]
        self.mean_lines_max = stat["line"]["max"]
        self.mean_lines_min = stat["line"]["min"]
        self.mean_lines_50per = stat["line"]["50%"]
        self.mean_bytes = stat["bytes"]["mean"]
        self.mean_bytes_std = stat["bytes"]["std"]
        self.mean_bytes_max = stat["bytes"]["max"]
        self.mean_bytes_min = stat["bytes"]["min"]
        self.mean_bytes_50per = stat["bytes"]["50%"]

    def _timedelta(self) -> int:
        elapse = self.end_time - self.start_time
        return elapse.total_seconds()

    def _resample(self, unit: str, method: str = "mean") -> None:
        r = self.df.resample(unit, origin="start")
        mean = r.mean()

        _sum = r.sum()
        mean["bytes"] = _sum["bytes"]
        mean["line"] = _sum["line"]
        self.df = mean

    def to_csv(self) -> None:
        p = Path("pylogcounter_csv")
        p.mkdir(exist_ok=True)

        path = p / f"{self.kind.lower()}.csv"
        self.df.to_csv(path)

    def equal_start_end(self) -> bool:
        start = self.df.index[0]
        end = self.df.index[len(self.df.index) - 1]
        if start == end:
            return True
        return False


class TotalCounter(BaseCounter):
    kind = "Total"
    unit = ""

    def __init__(self, df: pd.DataFrame) -> None:
        self.df = df

    def to_csv(self) -> None:
        super().to_csv()


class SecondCounter(BaseCounter):
    unit = "1S"
    kind = "Second"
    time_unit = "sec"

    def __init__(self, df: pd.DataFrame) -> None:
        self.df = df
        super()._resample(SecondCounter.unit)

    def count(self) -> None:
        super().count()

    def to_csv(self) -> None:
        super().to_csv()


class MinutelyCounter(BaseCounter):
    unit = "1min"
    kind = "Minutely"
    time_unit = "min"

    def __init__(self, df: pd.DataFrame) -> None:
        self.df = df
        super()._resample(MinutelyCounter.unit)

    def count(self) -> None:
        super().count()

    def to_csv(self) -> None:
        super().to_csv()


class HourlyCounter(BaseCounter):
    unit = "1H"
    kind = "Hourly"
    time_unit = "hour"

    def __init__(self, df: pd.DataFrame) -> None:
        self.df = df
        super()._resample(HourlyCounter.unit)

    def count(self) -> None:
        super().count()

    def to_csv(self) -> None:
        super().to_csv()


class DailyCounter(BaseCounter):
    unit = "1D"
    kind = "Daily"
    time_unit = "day"

    def __init__(self, df: pd.DataFrame) -> None:
        self.df = df
        super()._resample(DailyCounter.unit)

    def count(self) -> None:
        super().count()

    def to_csv(self) -> None:
        super().to_csv()


class WeeklyCounter(BaseCounter):
    unit = "1W"
    kind = "Weekly"
    time_unit = "week"

    def __init__(self, df: pd.DataFrame) -> None:
        self.df = df
        super()._resample(WeeklyCounter.unit)

    def count(self) -> None:
        super().count()

    def to_csv(self) -> None:
        super().to_csv()
