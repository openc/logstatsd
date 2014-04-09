###  A logster parser file that can be used to count the number
###  of sent/deferred/bounced emails from a Postfix log, along with
### some other associated statistics.
###
###  For example:
###  sudo ./logster --dry-run --output=ganglia PostfixParser /var/log/maillog
###
###
###  Copyright 2011, Bronto Software, Inc.
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
        self.time = 0
        self.count = 0.0
        self.regex = re.compile("""
        (.*Rescan\ \(parallel\).*real=([0-9.]+)\ secs|
        .*concurrent\ mode\ failure.*real=([0-9.]+)\ secs|
        .*Full\ GC.*real=([0-9.]+)\ secs)""", re.VERBOSE)

    def parse_line(self, line):
        try:
            # Apply regular expression to each line and extract
            # interesting bits.
            time = self.regex.match(line).groups()[1]
            self.time += float(time)
            self.count += 1
        except Exception, e:
            raise LogsterParsingException, "regmatch or contents failed with %s" % e


    def get_state(self, duration):
        # Return a list of metrics objects
        return [
            MetricObject("logs.jvm.gc.pause.count", self.count, metric_type="c"),
            MetricObject("logs.jvm.gc.pause", str(self.time * 1000), metric_type="ms")
        ]
