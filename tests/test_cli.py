import sys
from pathlib import Path
from typing import Union

import pandas as pd
import pytest
import yaml

from pylogcounter.cli import CLI
from pylogcounter.parse import LogLevelParser
from pylogcounter.stat import Statistic

test_dir = Path("tests/testdata")


class TestCLIOptions:
    log = test_dir / "timestamp_iso.log"

    def test_output(self):
        cli = CLI(TestCLIOptions.log, output="stdout")
        cli.run()

        cli = CLI(TestCLIOptions.log, output="yaml")
        cli.run()


class TestCsvOutput:
    log = test_dir / "timestamp_iso.log"

    def test_csv(self):
        cli = CLI(TestCsvOutput.log, output="yaml", to_csv=True)
        cli.run()

        p = Path(cli.csv_dir)
        assert p.exists()

        # Check the csv are loaded as a dataframe.
        csv_list = ["total", "second", "minutely", "hourly", "daily"]
        for c in csv_list:
            pp = p / f"{c}.csv"
            pd.read_csv(pp)


class TestCustomTimestamp:
    def test_error_exit(self, capfd):
        f = test_dir / "timestamp_custom.log"
        _, err = capfd.readouterr()
        cli = CLI(f)
        with pytest.raises(SystemExit):
            cli.run()
            assert err == "Timestamp cannot be parsed in tests/testdata/timestamp_custom.log."

    def test_custom_timestamp(self, capfd):
        f = test_dir / "timestamp_custom.log"
        timestamp = "%Y-%m-%dT%H:%M:%S.%f%z"
        cli = CLI(f, timestamp=timestamp)
        assert cli.run() is None


class TestByteUnit:
    log = test_dir / "timestamp_iso.log"

    def test_byte(self, tmp_path):
        # base data
        output = tmp_path / "byte.yml"
        stream = open(str(output), "w")
        tmp = sys.stdout
        sys.stdout = stream
        cli = CLI(TestByteUnit.log, byte_unit="b", output="yaml")
        cli.run()
        sys.stdout = tmp
        with open(output, "r") as f:
            base_result = yaml.safe_load(f)

        # Check the unit and value for each byte prefix.
        for prefix, unit in Statistic.byte_table.items():
            output = tmp_path / f"{prefix}.yml"
            stream = open(str(output), "w")
            tmp = sys.stdout
            sys.stdout = stream
            cli = CLI(TestByteUnit.log, byte_unit=prefix, output="yaml")
            cli.run()
            sys.stdout = tmp
            with open(output, "r") as f:
                result = yaml.safe_load(f)

            assert result["total"]["byte_unit"] == unit.lower()
            total = from_byte(base_result["total"]["total_bytes"], prefix, decimal=cli.decimal)
            assert total == result["total"]["total_bytes"]


class TestCustomInterval:
    log = test_dir / "timestamp_iso.log"

    def test_wrong_interval(self):
        wrong_formats = ["2222", "bbb", "s1"]
        for w in wrong_formats:
            cli = CLI(TestCustomInterval.log, interval=w)
            with pytest.raises(Exception) as e:
                cli.run()
            assert str(e.value) == f"Cannot parse {w}."

        wrong_unit = "1a"
        cli = CLI(TestCustomInterval.log, interval=wrong_unit)
        with pytest.raises(Exception) as e:
            cli.run()
        assert str(e.value) == f"{wrong_unit} is invalid datetime unit."

    def test_interval(self):
        intervals = ["10s", "10m", "10h", "10d"]
        for interval in intervals:
            cli = CLI(TestCustomInterval.log, interval=interval)
            cli.run()


class TestLoglevelCategorize:
    log = test_dir / "timestamp_iso.log"

    def test_miss_yaml_option(self):
        with pytest.raises(SystemExit):
            CLI(TestLoglevelCategorize.log, loglevel=True)

    def test_categorize_loglevel(self, tmp_path):
        output = tmp_path / "loglevel.yml"
        stream = open(str(output), "w")
        tmp = sys.stdout
        sys.stdout = stream
        cli = CLI(TestLoglevelCategorize.log, loglevel=True, output="yaml")
        cli.run()
        sys.stdout = tmp
        with open(output, "r") as f:
            result = yaml.safe_load(f)

        for level in LogLevelParser.levels:
            assert level in result["total"]["log"]


def from_byte(val: Union[int, float], prefix: str, decimal: int) -> float:
    if prefix == "k":
        return round(float(val / 1024), decimal)
    elif prefix == "m":
        return round(float(val / (1024**2)), decimal)
    if prefix == "g":
        return round(float(val / (1024**3)), decimal)
    if prefix == "t":
        return round(float(val / (1024**4)), decimal)
    else:
        return round(float(val), decimal)
