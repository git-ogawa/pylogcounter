#!/usr/bin/env python3
import argparse
import sys
from typing import Dict, Optional

from logcounter.counter import (
    BaseCounter,
    DailyCounter,
    HourlyCounter,
    MinutelyCounter,
    SecondCounter,
    TotalCounter,
)
from logcounter.parse import DirectiveError, Parser, ParserError
from logcounter.writer import StdoutWriter, Writer, YamlWriter


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
    ) -> None:
        self.file = infile
        self.output = output
        self.flags = flags
        self.byte_unit = byte_unit
        self.timestamp = timestamp
        self.to_csv = to_csv
        self.verbose = verbose

        self.writer: Optional[Writer] = None
        self._set()

    def _set(self) -> None:
        if self.output == "stdout":
            self.writer = StdoutWriter
        elif self.output == "yaml":
            self.writer = YamlWriter

    def run(self) -> None:
        try:
            p = Parser(self.file, timestamp_format=self.timestamp)
            p.precheck()
            res = p.parse()
        except ParserError as e:
            print(e)
            sys.exit("Try to use a custom timestamp format. See usage for details.")
        except DirectiveError:
            raise

        bc = BaseCounter(res, p.columns, p.timestamp_format)

        tc = TotalCounter(bc.df)
        tc.count()

        self.writer(
            tc, p.timestamp_format, self.byte_unit, verbose=self.verbose
        ).write()

        if self.to_csv is True:
            tc.to_csv()

        if self.flags.get("second", True) is True:
            sc = SecondCounter(bc.df)
            sc.count()
            if sc.equal_start_end() is not True:
                self.writer(
                    sc, p.timestamp_format, self.byte_unit, verbose=self.verbose
                ).write()

            if self.to_csv is True:
                sc.to_csv()

        if self.flags.get("minute", True) is True:
            mc = MinutelyCounter(bc.df)
            mc.count()
            if mc.equal_start_end() is not True:
                self.writer(
                    mc, p.timestamp_format, self.byte_unit, verbose=self.verbose
                ).write()

            if self.to_csv is True:
                mc.to_csv()

        if self.flags.get("hour", True) is True:
            hc = HourlyCounter(bc.df)
            hc.count()
            if hc.equal_start_end() is not True:
                self.writer(
                    hc, p.timestamp_format, self.byte_unit, verbose=self.verbose
                ).write()

            if self.to_csv is True:
                hc.to_csv()

        if self.flags.get("day", True) is True:
            dc = DailyCounter(bc.df)
            dc.count()
            if dc.equal_start_end() is not True:
                self.writer(
                    dc, p.timestamp_format, self.byte_unit, verbose=self.verbose
                ).write()

            if self.to_csv is True:
                dc.to_csv()


def main() -> None:
    usage = "%(prog)s -f [log_file] [options]"
    parser = argparse.ArgumentParser(
        usage=usage,
        description=__doc__,
    )
    parser.add_argument(
        "-f", "--file", metavar="", help="A log file to be parsed.", required=True
    )
    parser.add_argument(
        "-o", "--output", metavar="", default="stdout", help="The output format."
    )
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
        help="If set, the resampled data are ouput to csv.",
    )
    parser.add_argument(
        "-b",
        "--byte",
        metavar="",
        default="b",
        help="Specify prefix unit of byte (k, m, g, t are kilo, mega, giga, tela respectively.)",
    )
    parser.add_argument("--only", metavar="", type=str, help="aaa")

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
    )
    cli.run()
