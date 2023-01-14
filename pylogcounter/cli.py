#!/usr/bin/env python3
import argparse
import sys
from typing import Dict, Optional, Type, Union

import pandas as pd

from pylogcounter.counter import (
    BaseCounter,
    CustomCounter,
    DailyCounter,
    HourlyCounter,
    MinutelyCounter,
    SecondCounter,
    TotalCounter,
)
from pylogcounter.parse import DirectiveError, LogLevelParserError, Parser, ParserError
from pylogcounter.stat import Statistic
from pylogcounter.writer import StdoutWriter, YamlWriter


class CLI:
    def __init__(
        self,
        infile: str,
        output: str = "stdout",
        flags: Dict[str, bool] = {},
        verbose: bool = False,
        timestamp: Optional[str] = None,
        to_csv: bool = False,
        byte_unit: str = "b",
        loglevel: bool = False,
        interval: str = "",
    ) -> None:
        self.file = infile
        self.output = output
        self.flags = flags
        self.byte_unit = byte_unit
        self.timestamp = timestamp
        self.to_csv = to_csv
        self.verbose = verbose
        self.loglevel = loglevel
        self.interval = interval

        self.csv_dir = "pylogcounter_csv"
        self.decimal = 3
        self.writer: Type[Union[StdoutWriter, YamlWriter]] = StdoutWriter
        self._set()

    def _set(self) -> None:
        if self.output == "stdout":
            self.writer = StdoutWriter
        elif self.output == "yaml":
            self.writer = YamlWriter

        if self.loglevel is True:
            if self.output != "yaml":
                sys.exit(
                    "Flag '--log' is set, but Flag '--output yaml' is not set.\n"
                    "Currently '--log' is only valid when '--output yaml' is set together."
                )

    def run(self) -> None:
        try:
            self.parser = Parser(self.file, timestamp_format=self.timestamp)
            self.parser.precheck()
            res = self.parser.parse(extract_level=self.loglevel)
        except ParserError as e:
            print(e)
            sys.exit("Try to use a custom timestamp format. See usage for details.")
        except LogLevelParserError as e:
            print(e)
            sys.exit("Check the log includes loglevel.")
        except DirectiveError:
            raise

        assert self.parser.timestamp_format is not None
        bc = BaseCounter(res, self.parser.columns, self.parser.timestamp_format)
        self.run_total_counter(bc.df)

        if self.interval != "":
            self.run_custom_counter(bc.df, self.interval)
        else:
            self.run_counters(bc.df)

    def run_total_counter(self, df: pd.DataFrame) -> None:
        counter = TotalCounter(df)
        if self.loglevel is True:
            counter.split_log_columns()
        stat = Statistic(
            counter.df,
            decimal=self.decimal,
            time_unit=counter.time_unit,
            byte_unit=self.byte_unit,
        )
        stat.extract()

        assert self.parser.timestamp_format is not None
        writer = self.writer(stat, self.parser.timestamp_format, verbose=self.verbose)
        writer.write(counter.kind, show_loglevel=self.loglevel)

        if self.to_csv is True:
            counter.to_csv(self.csv_dir)

    def run_custom_counter(self, df: pd.DataFrame, time_range: str) -> None:
        counter = CustomCounter(df, time_range)
        if self.loglevel is True:
            counter.split_log_columns()
        counter.resample()
        stat = Statistic(
            counter.df,
            decimal=self.decimal,
            time_unit=counter.time_unit,
            byte_unit=self.byte_unit,
        )
        stat.extract()

        assert self.parser.timestamp_format is not None
        writer = self.writer(stat, self.parser.timestamp_format, verbose=self.verbose)
        writer.write(counter.kind, show_loglevel=self.loglevel)

        if self.to_csv is True:
            counter.to_csv(self.csv_dir)

    def run_counters(self, df: pd.DataFrame) -> None:
        counters = {
            "second": SecondCounter,
            "min": MinutelyCounter,
            "hour": HourlyCounter,
            "day": DailyCounter,
        }

        for time, Counter in counters.items():
            if self.flags.get(time, True) is True:
                counter = Counter(df)
                if self.loglevel is True:
                    counter.split_log_columns()

                counter.resample()  # type: ignore
                stat = Statistic(
                    counter.df,
                    decimal=self.decimal,
                    time_unit=counter.time_unit,
                    byte_unit=self.byte_unit,
                )
                stat.extract()
                if stat.equal_start_end() is not True:
                    assert self.parser.timestamp_format is not None
                    writer = self.writer(stat, self.parser.timestamp_format, verbose=self.verbose)
                    writer.write(counter.kind, show_loglevel=self.loglevel)

                if self.to_csv is True:
                    counter.to_csv(self.csv_dir)


def main() -> None:
    usage = "%(prog)s -f [log_file] [options]"
    parser = argparse.ArgumentParser(
        usage=usage,
        description=__doc__,
    )
    parser.add_argument("-f", "--file", metavar="", help="A log file to be parsed.", required=True)
    parser.add_argument("-o", "--output", metavar="", default="stdout", help="The output format.")
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="If set, the detail result will be output.",
    )
    parser.add_argument(
        "-t",
        "--time_format",
        metavar="",
        type=str,
        default=None,
        help="Custom time format.",
    )
    parser.add_argument(
        "-c",
        "--csv",
        action="store_true",
        help="If set, the resampled data are output to csv.",
    )
    parser.add_argument(
        "-b",
        "--byte",
        metavar="",
        default="b",
        help="Specify prefix unit of byte (k, m, g, t are kilo, mega, giga, tera respectively.)",
    )
    parser.add_argument(
        "--only",
        metavar="",
        type=str,
        help="Show only the result of the specify time range.",
    )
    parser.add_argument("-l", "--log", action="store_true", help="If set, count log level in a log.")
    parser.add_argument("-i", "--interval", default="", help="Custom interval.")

    args = parser.parse_args()

    if args.only is not None:
        flags = {
            "second": bool("s" in args.only),
            "minute": bool("m" in args.only),
            "hour": bool("h" in args.only),
            "day": bool("d" in args.only),
        }
    else:
        flags = {}

    cli = CLI(
        args.file,
        args.output,
        flags=flags,
        verbose=args.verbose,
        timestamp=args.time_format,
        to_csv=args.csv,
        byte_unit=args.byte,
        loglevel=args.log,
        interval=args.interval,
    )
    cli.run()
