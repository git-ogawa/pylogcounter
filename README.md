# pylogcounter
[![LICENSE](https://img.shields.io/github/license/git-ogawa/pylogcounter?style=plastic)](https://github.com/git-ogawa/pylogcounter/blob/main/LICENSE)
[![Version](https://img.shields.io/pypi/v/pylogcounter?style=plastic)](https://pypi.python.org/pypi/pylogcounter/)
![Python versions](https://img.shields.io/pypi/pyversions/pylogcounter?style=plastic)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![Downloads](https://static.pepy.tech/badge/pylogcounter)](https://pepy.tech/project/pylogcounter)

pylogcounter is a simple, compact CLI to check lines and size of a log file. It is also possible to resample the contents based on timestamps and show the mean of lines and size per minute, hour and etc.

The tool will be useful when you want to check log size and loglevel trends before monitoring and visualizing logs on large-scale platforms such as elasticsearch.


# Table of Contents
- [pylogcounter](#pylogcounter)
- [Table of Contents](#table-of-contents)
- [Install](#install)
- [Usage](#usage)
  - [Simple usage](#simple-usage)
  - [Run on docker](#run-on-docker)
  - [Custom timestamp format](#custom-timestamp-format)
  - [Show details](#show-details)
  - [Output to csv](#output-to-csv)
  - [Custom time interval](#custom-time-interval)
  - [Loglevel Classification](#loglevel-classification)


# Install
Install with pip.
```
$ pip install pylogcounter
```

Alternatively, you can pull a docker image from [dockerhub](https://hub.docker.com/r/docogawa/pylogcounter).
```
# docker pull docogawa/pylogcounter
```

# Usage
You need a log file to be parsed that meets the following requirements.

- A file must include a timestamp per line.
- multiline log is not supported.
- The format of timestamp must be one of the following (See [Custom timestamp format](#custom-timestamp-format) if you use your own format).

| Type | Format | Example |
| - | - | - |
| ISO 8601 | %Y-%m-%dT%H:%M:%S.%fZ | 2022-05-18T11:40:22.519222Z |
| RFC 3164 | %b %m %H:%M:%S | Jan  7 16:55:01  |
| General format | %Y-%m-%d %H:%M:%S | 2023-01-08 11:15:24 |


## Simple usage
Run `pylogcounter` with `-f` option to pass the path to the log file. The results are shown on the stdout.

```
$ pylogcounter -f syslog
Kind : Total
--------------------------------------------------------------------------------
Item                        | Value                       | Unit
--------------------------------------------------------------------------------
Start time                  | Jul 07 00:00:01             |
End time                    | Jul 07 16:55:07             |
Elapsed time                | 60906.0                     |
Total line                  | 2683                        | Line
Total bytes                 | 2353790.0                   | Byte
Mean line                   | 1.0                         | Line
Mean bytes                  | 877.298                     | Byte
--------------------------------------------------------------------------------

Kind : Second
--------------------------------------------------------------------------------
Item                        | Value                       | Unit
--------------------------------------------------------------------------------
Start time                  | Jul 07 00:00:01             |
End time                    | Jul 07 16:55:07             |
Mean line                   | 0.044                       | Line/sec
Mean bytes                  | 38.646                      | Byte/sec
--------------------------------------------------------------------------------

Kind : Minutely
--------------------------------------------------------------------------------
Item                        | Value                       | Unit
--------------------------------------------------------------------------------
Start time                  | Jul 07 00:00:01             |
End time                    | Jul 07 16:55:01             |
Mean line                   | 2.641                       | Line/min
Mean bytes                  | 2316.722                    | Byte/min
--------------------------------------------------------------------------------

Kind : Hourly
--------------------------------------------------------------------------------
Item                        | Value                       | Unit
--------------------------------------------------------------------------------
Start time                  | Jul 07 00:00:01             |
End time                    | Jul 07 16:00:01             |
Mean line                   | 157.824                     | Line/hour
Mean bytes                  | 138458.235                  | Byte/hour
--------------------------------------------------------------------------------

Kind : Daily
--------------------------------------------------------------------------------
Item                        | Value                       | Unit
--------------------------------------------------------------------------------
Start time                  | Jul 07 00:00:01             |
End time                    | Jul 07 00:00:01             |
Mean line                   | 2683.0                      | Line/day
Mean bytes                  | 2353790.0                   | Byte/day
--------------------------------------------------------------------------------
```

In the total section (Table below `kind: Total`), the overall result of the log file is displayed. See below for details on each item.

| Item | Description |
| - | - |
| Start time | The start time of log. |
| End time | The end time of log. |
| Elapsed time | The difference between the start and the end [sec]. |
| Total line | The number of lines in log. |
| Total bytes | Total bytes in log. |
| Mean line | The mean lines (equals to `total_line/elapsed_time`). |
| Mean bytes | The mean number of bytes per line (equals to `total_bytes/total_lines`). |


In each time section, resampled statistics are output for each period. For example, in the minutely section, start time and end time means the start and end time of the log resampled in minutes.


With `--only` option, show only the result of the specified time range. To display multiple time range, separate them by `,` such as `--only s,m,h`.

```
$ pylogcounter -f syslog --only s,h
Kind : Total
--------------------------------------------------------------------------------
Item                        | Value                       | Unit
--------------------------------------------------------------------------------
Start time                  | Jul 07 00:00:01             |
End time                    | Jul 07 16:55:07             |
Elapsed time                | 60906.0                     |
Total line                  | 2683                        | Line
Total bytes                 | 2353790.0                   | Byte
Mean line                   | 1.0                         | Line
Mean bytes                  | 877.298                     | Byte
--------------------------------------------------------------------------------

Kind : Second
--------------------------------------------------------------------------------
Item                        | Value                       | Unit
--------------------------------------------------------------------------------
Start time                  | Jul 07 00:00:01             |
End time                    | Jul 07 16:55:07             |
Mean line                   | 0.044                       | Line/sec
Mean bytes                  | 38.646                      | Byte/sec
--------------------------------------------------------------------------------

Kind : Hourly
--------------------------------------------------------------------------------
Item                        | Value                       | Unit
--------------------------------------------------------------------------------
Start time                  | Jul 07 00:00:01             |
End time                    | Jul 07 16:00:01             |
Mean line                   | 157.824                     | Line/hour
Mean bytes                  | 138458.235                  | Byte/hour
--------------------------------------------------------------------------------
```

Use `-o yaml` in order to show the result in yaml syntax.

```yaml
$ pylogcounter -f tmp/syslog -o yaml
total:
  start_time: Jul 07 00:00:01
  end_time: Jul 07 16:55:07
  elapsed_time: 60906.0
  total_lines: 2683
  total_bytes: 2353790.0
  mean_lines: 1.0
  mean_bytes: 877.298
  byte_unit: byte
second:
  start_time: Jul 07 00:00:01
  end_time: Jul 07 16:55:07
  mean_lines: 0.044
  mean_bytes: 38.646
  byte_unit: byte
minutely:
  start_time: Jul 07 00:00:01
  end_time: Jul 07 16:55:01
  mean_lines: 2.641
  mean_bytes: 2316.722
  byte_unit: byte
hourly:
  start_time: Jul 07 00:00:01
  end_time: Jul 07 16:00:01
  mean_lines: 157.824
  mean_bytes: 138458.235
  byte_unit: byte
daily:
  start_time: Jul 07 00:00:01
  end_time: Jul 07 00:00:01
  mean_lines: 2683.0
  mean_bytes: 2353790.0
  byte_unit: byte
```

To change the unit of bytes, specify the byte prefix in the `-b` option. All byte units in the result are replaced by the specified unit.

```
$ pylogcounter -f tmp/syslog --only m -b m
ind : Total
--------------------------------------------------------------------------------
Item                        | Value                       | Unit
--------------------------------------------------------------------------------
Start time                  | Jul 07 00:00:01             |
End time                    | Jul 07 16:55:07             |
Elapsed time                | 60906.0                     |
Total line                  | 2683                        | Line
Total bytes                 | 2.245                       | MB
Mean line                   | 1.0                         | Line
Mean bytes                  | 0.001                       | MB
--------------------------------------------------------------------------------

Kind : Minutely
--------------------------------------------------------------------------------
Item                        | Value                       | Unit
--------------------------------------------------------------------------------
Start time                  | Jul 07 00:00:01             |
End time                    | Jul 07 16:55:01             |
Mean line                   | 2.641                       | Line/min
Mean bytes                  | 0.002                       | MB/min
--------------------------------------------------------------------------------
```

## Run on docker
If you use pylogcounter using docker image, run the following commands.

- Mount the directory including a log to be parsed to `/work`. the following example mounts the current directory to /work, so pass `/work/[logfile]` to `-f`.


```
# docker run -it --rm -v ${PWD}:/work docogawa/pylogcounter -f /work/syslog
```

## Custom timestamp format
To parse the timestamp that is not in the table in [Usage](#usage), specify your custom timestamp format with  `-t`. For example, timestamp `2023-01-08T09:59:10.197397+0000` can be parsed by the directive `%Y-%m-%dT%H:%M:%S.%f%z`, so you should use `pylogcounter -t "%Y-%m-%dT%H:%M:%S.%f%z"`.

```
# custom.log
[2023-01-08T09:59:10.197397+0000] error test
[2023-01-08T09:59:33.197397+0000] warn test
[2023-01-08T09:59:35.197397+0000] info test
[2023-01-08T09:59:55.197397+0000] info test
[2023-01-08T10:00:22.197397+0000] debug test
...

$ pylogcounter -f custom.log -t "%Y-%m-%dT%H:%M:%S.%f%z" --only s
----------------------------------------------------------------------------------------------------
Item                                | Value                               | Unit
----------------------------------------------------------------------------------------------------
Start time                          | 2023-01-08T09:59:10.197397+0000     |
End time                            | 2023-01-08T14:20:34.197397+0000     |
Elapsed time                        | 15684.0                             |
Total line                          | 1000                                | Line
Total bytes                         | 44500.0                             | Byte
Mean line                           | 1.0                                 | Line
Mean bytes                          | 44.5                                | Byte
----------------------------------------------------------------------------------------------------

Kind : Second
----------------------------------------------------------------------------------------------------
Item                                | Value                               | Unit
----------------------------------------------------------------------------------------------------
Start time                          | 2023-01-08T09:59:10.197397+0000     |
End time                            | 2023-01-08T14:20:34.197397+0000     |
Mean line                           | 0.064                               | Line/sec
Mean bytes                          | 2.837                               | Byte/sec
----------------------------------------------------------------------------------------------------
```

## Show details
The `-v` option show the max, min, standard deviation and 50 % of the mean size and lines in addition to the result. This may be useful to see trends when the log output varies widely over time.

```
Kind : Minutely
----------------------------------------------------------------------------------------------------
Item                                | Value                               | Unit
----------------------------------------------------------------------------------------------------
Start time                          | Jul 07 00:00:01                     |
End time                            | Jul 07 16:55:01                     |
Mean line                           | 2.641                               | Line/min
Mean line max                       | 93.0                                | Line/min
Mean line min                       | 2.0                                 | Line/min
Mean line std                       | 4.72                                | Line/min
Mean line 50%                       | 2.0                                 | Line/min
Mean bytes                          | 2316.722                            | Byte/min
Mean bytes max                      | 19370.0                             | Byte/min
Mean bytes min                      | 291.0                               | Byte/min
Mean bytes std                      | 729.233                             | Byte/min
Mean bytes 50%                      | 2236.5                              | Byte/min
----------------------------------------------------------------------------------------------------
```


## Output to csv
Run pylogcounter with `-c` option to write resampled data in each time range to csv. The results are stored in `pylogcounter_csv`.

```
pylogcounter_csv
├── daily.csv
├── hourly.csv
├── minutely.csv
├── second.csv
└── total.csv
```

The csv has the following columns. The data will be useful when you analyze the log in your way.

| Column | Description |
| - | - |
| timestamp | Resampled timestamp |
| bytes | The sum of bytes included in the resampled time range. |
| lines | The sum of lines included in the resampled time range. |

```
# minutely.csv
timestamp,bytes,line
2023-01-08 04:26:28.141265,235,6
2023-01-08 04:27:28.141265,118,3
2023-01-08 04:28:28.141265,159,4
2023-01-08 04:29:28.141265,118,3
2023-01-08 04:30:28.141265,118,3
2023-01-08 04:31:28.141265,118,3
2023-01-08 04:32:28.141265,79,2
```

## Custom time interval
Run pylogcounter with `-i [interval]` to resample a log at the specified time interval. The following example resamples a log `syslog` every 15 minutes and output the mean of lines and bytes per 15 minutes as `Mean line`, `Mean bytes` respectively in the custom section.

```
$ pylogcounter -f syslog  -i 15m
Kind : Total
----------------------------------------------------------------------------------------------------
Item                                | Value                               |Unit
----------------------------------------------------------------------------------------------------
Start time                          | Jul 07 00:00:01                     |
End time                            | Jul 07 16:55:07                     |
Elapsed time                        | 60906.0                             |
Total line                          | 2683                                | Line
Total bytes                         | 2353790.0                           | Byte
Mean line                           | 1.0                                 | Line
Mean bytes                          | 877.298                             | Byte
----------------------------------------------------------------------------------------------------

Kind : Custom
----------------------------------------------------------------------------------------------------
Item                                | Value                               |Unit
----------------------------------------------------------------------------------------------------
Start time                          | Jul 07 00:00:01                     |
End time                            | Jul 07 16:45:01                     |
Mean line                           | 39.456                              | Line
Mean bytes                          | 34614.559                           | Byte
----------------------------------------------------------------------------------------------------
```

The time interval must be `[digit]:[unit_prefix]`. The valid unit prefixes are the following.

| Prefix | unit | Example |
| - | - | - |
| s, sec | second | 10s, 10sec |
| m, min | minute | 5m, 5min |
| h, hour | hour | 2h, 2hour |
| d, day | day | 1d, 1day |
| w, week | week | 1w, 1week |
| M, month | month | 1M, 1month |


If you want to check that the data are correctly resampled at the specified time interval, run pylogcounter with `-c` to write the processed data to `pylogcounter_csv/custom.csv`. You find that the timestamp columns are separated by the time (per 15 minutes in the example below).

```
# pylogcounter_csv/custom.csv
timestamp,bytes,line
2023-01-13 18:10:43.960345,4238,62
2023-01-13 18:25:43.960345,3860,58
2023-01-13 18:40:43.960345,3765,55
2023-01-13 18:55:43.960345,4141,62
2023-01-13 19:10:43.960345,4374,67
...
```

## Loglevel Classification
If a log have messages with loglevel per line, you can count the mean by running pylogcounter with `--log`  and `-o yaml`. The pylogcounter detect and parse the message with loglevel per line automatically. The loglevel that can be parsed are the following.

- alert
- debug
- notice
- info
- warn
- error
- critical
- fatal

The results are shown under `log` field in the total and each time section.  In the total section, the fields show the mean of messages with the loglevel in a log. For example, debug `0.256` below means that the ratio of the messages with debug level to total lines `1000` is 0.256. Thus 256 of the 1000 lines are debug messages.

Similarly in the minutely section, the field show the mean of messages with log level per minute.

```yaml
$ pylogcounter -f test.log --log -o yaml --only m
total:
  start_time: '2023-01-08T03:25:08.897592Z'
  end_time: '2023-01-08T03:41:47.897592Z'
  elapsed_time: 999.0
  total_lines: 1000
  total_bytes: 39508.0
  mean_lines: 1.0
  mean_bytes: 39.508
  byte_unit: byte
  log:
    alert: 0.0
    debug: 0.256
    notice: 0.0
    info: 0.253
    warn: 0.239
    error: 0.252
    critical: 0.0
    fatal: 0.0
minutely:
  start_time: '2023-01-08T03:25:08.897592Z'
  end_time: '2023-01-08T03:41:08.897592Z'
  lines: 58.824
  bytes: 2324.0
  byte_unit: byte
  log:
    alert: 0.0
    debug: 15.059
    notice: 0.0
    info: 14.882
    warn: 14.059
    error: 14.824
    critical: 0.0
    fatal: 0.0
```

Run with `-c` to write the number of loglevels in each time range after being resampled to csv for detailed analysis. The csv contains loglevel columns in addition to the standard columns (timestamp, bytes, line). The log_total_count columns is the sum of all loglevels (`log_total_count = alert + debug + ... + fatal`).

Note: The each row in the csv show the **sum** of messages with the loglevels per time, not the **mean**.
```
# pylogcounter_csv/daily.csv
timestamp,bytes,line,alert,debug,notice,info,warn,error,critical,fatal,log_total_count
2023-01-13 18:10:43.960345,378911,5627,663,686,681,729,742,677,754,695,5627
2023-01-14 18:10:43.960345,377875,5634,720,732,694,670,701,717,723,677,5634
2023-01-15 18:10:43.960345,370591,5514,729,691,708,699,665,667,667,688,5514
2023-01-16 18:10:43.960345,376211,5580,658,688,677,713,702,748,722,672,5580
2023-01-17 18:10:43.960345,375614,5587,687,657,699,710,728,708,702,696,5587
2023-01-18 18:10:43.960345,372907,5526,674,727,662,735,689,691,711,637,5526
2023-01-19 18:10:43.960345,374474,5567,698,711,699,689,689,721,665,695,5567
```

you can use the data to visualize how many messages the log include per loglevel at the time, or to see how them change over time as shown in the figure below.

![](docs/images/count_daily_log.png)