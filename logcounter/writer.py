import sys
from datetime import datetime
from typing import Union

import yaml

from logcounter.counter import BaseCounter


class Writer:

    byte_table = {"b": "Byte", "k": "KB", "m": "MB", "g": "GB", "t": "TB"}

    def __init__(
        self,
        counter: BaseCounter,
        time_format: str,
        byte_unit: str = "b",
        decimal_point: int = 3,
        verbose: bool = False,
    ):
        self.counter = counter
        self.time_format = time_format

        self.kind = self.counter.kind
        self.decimal_point = decimal_point
        self.time_unit = self.counter.time_unit
        self.start_time = self.counter.start_time
        self.end_time = self.counter.end_time
        self.timedelta = self.counter.timedelta
        self.total_bytes = self.counter.total_bytes
        self.total_lines = self.counter.total_lines
        self.mean_lines = self.counter.mean_lines
        self.mean_lines_std = self.counter.mean_lines_std
        self.mean_lines_max = self.counter.mean_lines_max
        self.mean_lines_min = self.counter.mean_lines_min
        self.mean_lines_50per = self.counter.mean_lines_50per
        self.mean_bytes = self.counter.mean_bytes
        self.mean_bytes_std = self.counter.mean_bytes_std
        self.mean_bytes_max = self.counter.mean_bytes_max
        self.mean_bytes_min = self.counter.mean_bytes_min
        self.mean_bytes_50per = self.counter.mean_bytes_50per

        self.byte_unit = byte_unit
        self.verbose = verbose

    def convert_byte(self, val: Union[int, float]) -> float:
        if self.byte_unit == "k":
            return round(float(val / 1024), self.decimal_point)
        elif self.byte_unit == "m":
            return round(float(val / (1024**2)), self.decimal_point)
        if self.byte_unit == "g":
            return round(float(val / (1024**3)), self.decimal_point)
        if self.byte_unit == "t":
            return round(float(val / (1024**4)), self.decimal_point)
        else:
            return round(float(val), self.decimal_point)

    def get_unit(self) -> str:
        return Writer.byte_table.get(self.byte_unit, "Byte")


class StdoutWriter(Writer):
    def __init__(
        self,
        counter: BaseCounter,
        time_format: str,
        byte_unit: str = "b",
        verbose: bool = False,
    ):
        super().__init__(counter, time_format, byte_unit, verbose=verbose)
        self.width = 100
        self.header = ["Item", "Value", "Unit"]
        self.columns = len(self.header)
        self.partition_char = "|"
        self.unit_width_ratio = 2 / 3
        self._calc_width()

    def _calc_width(self):
        self.col_width = int(round((self.width - ((self.columns) - (self.columns - 1))) / self.columns, 0))
        self.unit_width = int(round(self.col_width * self.unit_width_ratio, 0))
        space = self.col_width - self.unit_width
        self.col_width = int(round(self.col_width + (space / self.columns - 1)))

    def write(self):
        start_time = datetime.strftime(self.start_time, self.time_format)
        end_time = datetime.strftime(self.end_time, self.time_format)

        if self.time_unit == "":
            per_line = "Line"
            per_byte = f"{self.get_unit()}"
        else:
            per_line = f"Line/{self.time_unit}"
            per_byte = f"{self.get_unit()}/{self.time_unit}"

        print(f"Kind : {self.kind}")
        print("-" * self.width)
        print(
            f"{self.header[0]:<{self.col_width}}| {self.header[1]:<{self.col_width}}| {self.header[2]:<{self.unit_width}}"
        )
        print("-" * self.width)
        print(f"{'Start time':<{self.col_width}}| {start_time:<{self.col_width}}| {'':<{self.unit_width}}")
        print(f"{'End time':<{self.col_width}}| {end_time:<{self.col_width}}| {'':<{self.unit_width}}")
        if self.kind == "Total":
            print(
                f"{'Elapsed time':<{self.col_width}}| {self.timedelta:<{self.col_width}}| {self.time_unit:<{self.unit_width}}"
            )
            print(
                f"{'Total line':<{self.col_width}}| {self.total_lines:<{self.col_width}}| {'Line':<{self.unit_width}}"
            )
            byte = self.convert_byte(self.total_bytes)
            u = self.get_unit()
            print(f"{'Total bytes':<{self.col_width}}| {byte:<{self.col_width}}| {u:<{self.unit_width}}")
        ml = round(self.mean_lines, self.decimal_point)
        print(f"{'Mean line':<{self.col_width}}| {ml:<{self.col_width}}| {per_line:<{self.unit_width}}")
        if self.verbose is True:
            mx = round(self.mean_lines_max, self.decimal_point)
            mi = round(self.mean_lines_min, self.decimal_point)
            ms = round(self.mean_lines_std, self.decimal_point)
            m5 = round(self.mean_lines_50per, self.decimal_point)
            print(f"{'Mean line max':<{self.col_width}}| {mx:<{self.col_width}}| {per_line:<{self.unit_width}}")
            print(f"{'Mean line min':<{self.col_width}}| {mi:<{self.col_width}}| {per_line:<{self.unit_width}}")
            print(f"{'Mean line std':<{self.col_width}}| {ms:<{self.col_width}}| {per_line:<{self.unit_width}}")
            print(f"{'Mean line 50%':<{self.col_width}}| {m5:<{self.col_width}}| {per_line:<{self.unit_width}}")

        mb = self.convert_byte(self.mean_bytes)
        print(f"{'Mean bytes':<{self.col_width}}| {mb:<{self.col_width}}| {per_byte:<{self.unit_width}}")
        if self.verbose is True:
            mx = self.convert_byte(self.mean_bytes_max)
            mi = self.convert_byte(self.mean_bytes_min)
            ms = self.convert_byte(self.mean_bytes_std)
            m5 = self.convert_byte(self.mean_bytes_50per)
            print(f"{'Mean bytes max':<{self.col_width}}| {mx:<{self.col_width}}| {per_byte:<{self.unit_width}}")
            print(f"{'Mean bytes min':<{self.col_width}}| {mi:<{self.col_width}}| {per_byte:<{self.unit_width}}")
            print(f"{'Mean bytes std':<{self.col_width}}| {ms:<{self.col_width}}| {per_byte:<{self.unit_width}}")
            print(f"{'Mean bytes 50%':<{self.col_width}}| {m5:<{self.col_width}}| {per_byte:<{self.unit_width}}")

        print("-" * self.width)
        print()


class YamlWriter(Writer):
    def __init__(
        self,
        counter: BaseCounter,
        time_format: str,
        byte_unit: str = "b",
        verbose: bool = False,
    ):
        super().__init__(counter, time_format, byte_unit, verbose=verbose)

    def _to_float(self, val) -> float:
        return round(float(val), self.decimal_point)

    def write(self):
        start_time = datetime.strftime(self.start_time, self.time_format)
        end_time = datetime.strftime(self.end_time, self.time_format)

        kind = self.kind.lower()
        if kind == "total":
            if self.verbose is True:
                data = {
                    kind: {
                        "start_time": start_time,
                        "end_time": end_time,
                        "elapsed_time": self._to_float(self.timedelta),
                        "total_lines": int(self.total_lines),
                        "total_bytes": self.convert_byte(self.total_bytes),
                        "mean_lines": {
                            "value": self._to_float(self.mean_lines),
                            "max": self._to_float(self.mean_lines_max),
                            "min": self._to_float(self.mean_lines_min),
                            "std": self._to_float(self.mean_lines_std),
                            "50%": self._to_float(self.mean_lines_50per),
                        },
                        "mean_bytes": {
                            "value": self.convert_byte(self.mean_bytes),
                            "max": self.convert_byte(self.mean_bytes_max),
                            "min": self.convert_byte(self.mean_bytes_min),
                            "std": self.convert_byte(self.mean_bytes_std),
                            "50%": self.convert_byte(self.mean_bytes_50per),
                        },
                        "byte_unit": self.get_unit().lower(),
                    }
                }
            else:
                data = {
                    kind: {
                        "start_time": start_time,
                        "end_time": end_time,
                        "elapsed_time": self._to_float(self.timedelta),
                        "total_lines": int(self.total_lines),
                        "total_bytes": self.convert_byte(self.total_bytes),
                        "mean_lines": self._to_float(self.mean_lines),
                        "mean_bytes": self.convert_byte(self.mean_bytes),
                        "byte_unit": self.get_unit().lower(),
                    }
                }
        else:
            if self.verbose is True:
                data = {
                    kind: {
                        "start_time": start_time,
                        "end_time": end_time,
                        "mean_lines": {
                            "value": self._to_float(self.mean_lines),
                            "max": self._to_float(self.mean_lines_max),
                            "min": self._to_float(self.mean_lines_min),
                            "std": self._to_float(self.mean_lines_std),
                            "50%": self._to_float(self.mean_lines_50per),
                        },
                        "mean_bytes": {
                            "value": self.convert_byte(self.mean_bytes),
                            "max": self.convert_byte(self.mean_bytes_max),
                            "min": self.convert_byte(self.mean_bytes_min),
                            "std": self.convert_byte(self.mean_bytes_std),
                            "50%": self.convert_byte(self.mean_bytes_50per),
                        },
                        "byte_unit": self.get_unit().lower(),
                    }
                }
            else:
                data = {
                    kind: {
                        "start_time": start_time,
                        "end_time": end_time,
                        "mean_lines": self._to_float(self.mean_lines),
                        "mean_bytes": self.convert_byte(self.mean_bytes),
                        "byte_unit": self.get_unit().lower(),
                    }
                }

        yaml.dump(data, sys.stdout, sort_keys=False)
