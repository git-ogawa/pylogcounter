import sys
from datetime import datetime
from typing import TextIO

import numpy as np
import yaml

from pylogcounter.stat import Statistic


class Writer:
    def __init__(
        self,
        stat: Statistic,
        time_format: str,
        verbose: bool = False,
        stream: TextIO = sys.stdout,
    ):
        self.stat = stat
        self.time_format = time_format
        self.verbose = verbose

        self.stream = sys.stdout


class StdoutWriter(Writer):
    def __init__(
        self,
        stat: Statistic,
        time_format: str,
        verbose: bool = False,
        stream: TextIO = sys.stdout,
    ):
        super().__init__(stat, time_format, verbose=verbose, stream=stream)
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

    def write(self, kind: str, show_loglevel: bool = False):
        cw = self.col_width
        uw = self.unit_width

        start_time = datetime.strftime(self.stat.start_time, self.time_format)
        end_time = datetime.strftime(self.stat.end_time, self.time_format)

        if self.stat.time_unit == "":
            per_line = "Line"
            per_byte = f"{self.stat.get_unit()}"
        else:
            per_line = f"Line/{self.stat.time_unit}"
            per_byte = f"{self.stat.get_unit()}/{self.stat.time_unit}"

        print(f"Kind : {kind}")
        print("-" * self.width)
        print(f"{self.header[0]:<{cw}}| {self.header[1]:<{cw}}|" f"{self.header[2]:<{uw}}")
        print("-" * self.width)
        print(f"{'Start time':<{cw}}| {start_time:<{cw}}| {'':<{uw}}")
        print(f"{'End time':<{cw}}| {end_time:<{cw}}| {'':<{uw}}")
        if kind == "Total":
            print(f"{'Elapsed time':<{cw}}| {self.stat.timedelta:<{cw}}|" f"{self.stat.time_unit:<{uw}}")
            print(f"{'Total line':<{cw}}| {self.stat.total_lines:<{cw}}| {'Line':<{uw}}")
            print(f"{'Total bytes':<{cw}}| {self.stat.total_bytes:<{cw}}| {self.stat.get_unit():<{uw}}")

        print(f"{'Mean line':<{cw}}| {self.stat.lines['mean']:<{cw}}| {per_line:<{uw}}")
        if self.verbose is True:
            print(f"{'Mean line max':<{cw}}| {self.stat.lines['max']:<{cw}}| {per_line:<{uw}}")
            print(f"{'Mean line min':<{cw}}| {self.stat.lines['min']:<{cw}}| {per_line:<{uw}}")
            print(f"{'Mean line std':<{cw}}| {self.stat.lines['std']:<{cw}}| {per_line:<{uw}}")
            print(f"{'Mean line 50%':<{cw}}| {self.stat.lines['50%']:<{cw}}| {per_line:<{uw}}")

        print(f"{'Mean bytes':<{cw}}| {self.stat.bytes['mean']:<{cw}}| {per_byte:<{uw}}")
        if self.verbose is True:
            print(f"{'Mean bytes max':<{cw}}| {self.stat.bytes['max']:<{cw}}| {per_byte:<{uw}}")
            print(f"{'Mean bytes min':<{cw}}| {self.stat.bytes['min']:<{cw}}| {per_byte:<{uw}}")
            print(f"{'Mean bytes std':<{cw}}| {self.stat.bytes['std']:<{cw}}| {per_byte:<{uw}}")
            print(f"{'Mean bytes 50%':<{cw}}| {self.stat.bytes['50%']:<{cw}}| {per_byte:<{uw}}")

        print("-" * self.width)
        print()


class YamlWriter(Writer):
    def __init__(
        self,
        stat: Statistic,
        time_format: str,
        verbose: bool = False,
        stream: TextIO = sys.stdout,
    ):
        super().__init__(stat, time_format, verbose=verbose, stream=stream)

    def write(self, kind: str, show_loglevel: bool = False):

        kind = kind.lower()
        if kind == "total":
            data = self._total_data(kind, self.verbose, show_loglevel)
        else:
            data = self._data(kind, self.verbose, show_loglevel)
        data = self.to_float(data)
        yaml.dump(data, self.stream, sort_keys=False)

    def to_float(self, data: dict):
        for k, v in data.items():
            if isinstance(v, np.float64):
                data[k] = float(v)
            if isinstance(v, np.int64):
                data[k] = int(v)

            if isinstance(v, dict):
                self.to_float(v)

        return data

    def _total_data(self, kind: str, verbose: bool, show_loglevel: bool) -> dict:
        start_time = datetime.strftime(self.stat.start_time, self.time_format)
        end_time = datetime.strftime(self.stat.end_time, self.time_format)

        data = {
            kind: {
                "start_time": start_time,
                "end_time": end_time,
                "elapsed_time": self.stat.timedelta,
                "total_lines": self.stat.total_lines,
                "total_bytes": self.stat.total_bytes,
                "mean_lines": self.stat.lines["mean"],
                "mean_bytes": self.stat.bytes["mean"],
                "byte_unit": self.stat.get_unit().lower(),
            }
        }
        if verbose is True:
            data[kind].pop("mean_lines")
            data[kind].pop("mean_bytes")
            data[kind]["lines"] = {p: self.stat.lines[p] for p in self.stat.properties}
            data[kind]["bytes"] = {p: self.stat.bytes[p] for p in self.stat.properties}

        if show_loglevel is True:
            data[kind]["log"] = {}
            for level, prop in self.stat.log_levels.items():
                data[kind]["log"][level] = {}
                for k, v in prop.items():
                    if verbose is True:
                        data[kind]["log"][level][k] = v
                    else:
                        if k == "mean":
                            data[kind]["log"][level] = v

        return data

    def _data(self, kind: str, verbose: bool, show_loglevel: bool) -> dict:
        start_time = datetime.strftime(self.stat.start_time, self.time_format)
        end_time = datetime.strftime(self.stat.end_time, self.time_format)

        data = {
            kind: {
                "start_time": start_time,
                "end_time": end_time,
                "lines": self.stat.lines["mean"],
                "bytes": self.stat.bytes["mean"],
                "byte_unit": self.stat.get_unit().lower(),
            }
        }
        if verbose is True:
            data[kind].pop("lines")
            data[kind].pop("bytes")
            data[kind]["lines"] = {p: self.stat.lines[p] for p in self.stat.properties}
            data[kind]["bytes"] = {p: self.stat.bytes[p] for p in self.stat.properties}

        if show_loglevel is True:
            data[kind]["log"] = {}
            for level, prop in self.stat.log_levels.items():
                data[kind]["log"][level] = {}
                for k, v in prop.items():
                    if verbose is True:
                        data[kind]["log"][level][k] = v
                    else:
                        if k == "mean":
                            data[kind]["log"][level] = v

        return data
