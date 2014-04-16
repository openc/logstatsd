###  A logster parser file that can be used to measure GC pauses from
### a suitable log
###
### You'll need to add the following GC options to your tomcat startup script:
### export JAVA_OPTS="$JAVA_OPTS -Xloggc:/opt/tomcat7/logs/garbage-collection.log"
### export JAVA_OPTS="$JAVA_OPTS -XX:+PrintGCDetails"
### export JAVA_OPTS="$JAVA_OPTS -XX:+PrintGCTimeStamps"
### export JAVA_OPTS="$JAVA_OPTS -XX:+PrintGCApplicationStoppedTime"

###  Copyright 2014, OpenCorporates
###
###  This parser is free software: you can redistribute it and/or modify
###  it under the terms of the GNU General Public License as published by
###  the Free Software Foundation, either version 3 of the License, or
###  (at your option) any later version.
###
###  This parser is distributed in the hope that it will be useful,
###  but WITHOUT ANY WARRANTY; without even the implied warranty of
###  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
###  GNU General Public License for more details.
###

import time
import re

from logster.logster_helper import MetricObject, LogsterParser
from logster.logster_helper import LogsterParsingException

class JVMGCLogParser(LogsterParser):

    def __init__(self, option_string=None):
        self.pause_time = 0
        self.pause_count = 0.0
        self.stop_time = 0
        self.stop_count = 0.0
        self.pause_regex = re.compile(""".*
        (Rescan\ \(parallel\).*real=([0-9.]+)\ secs|
        concurrent\ mode\ failure.*real=([0-9.]+)\ secs|
        Full\ GC.*real=([0-9.]+)\ secs)""", re.VERBOSE)
        self.stop_regex = re.compile(""".*threads were stopped: ([0-9.]+) seconds""")

    def parse_line(self, line):
        errors = []
        try:
            pause_time = self.pause_regex.match(line).groups()[1]
            self.pause_time += float(pause_time)
            self.pause_count += 1
        except Exception, e:
            errors.append("1: %s" % e)
        try:
            stop_time = self.stop_regex.match(line).groups()[0]
            self.stop_time += float(stop_time)
            self.stop_count += 1
        except Exception, e:
            errors.append("2: %s" % e)
        if errors:
            raise LogsterParsingException, "regmatch or contents failed with %s" % errors

    def get_state(self, duration):
        # Return a list of metrics objects
        return [
            MetricObject("logs.jvm.gc.pause", self.pause_count, metric_type="c"),
            MetricObject("logs.jvm.gc.pause", str(self.pause_time * 1000), metric_type="ms"),
            MetricObject("logs.jvm.gc.stop", self.stop_count, metric_type="c"),
            MetricObject("logs.jvm.gc.stop", str(self.stop_time * 1000), metric_type="ms")
        ]
