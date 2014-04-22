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

class HAProxyLogster(LogsterParser):

    def __init__(self, option_string=None):
        '''Initialize any data structures or variables needed for keeping track
        of the tasty bits we find in the log we are parsing.'''
        self.unblocks = 0
        self.all_time = 0
        self.all_count = 0.0
        self.www_count = 0.0
        self.www_time = 0
        self.api_count = 0.0
        self.api_time = 0
        self.regex = re.compile('.*? ([^ ]+) \d+/\d+/\d+/\d+/(\d+).* (\S+) HTTP.*')

    def parse_line(self, line):
        try:
            # Apply regular expression to each line and extract
            # interesting bits.
            backend, time, url = self.regex.match(line).groups()
            self.all_time += int(time)
            self.all_count += 1
            if url == "/unblock_requests/new":
                self.unblocks += 1
            if backend.startswith("www"):
                self.www_count += 1
                self.www_time += int(time)
            elif backend.startswith("api"):
                self.api_count += 1
                self.api_time += int(time)
        except Exception, e:
            raise LogsterParsingException, "regmatch or contents failed with %s" % e


    def get_state(self, duration):
        # Return a list of metrics objects
        if self.all_count:
            all_timePerReq = self.all_time/self.all_count
        else:
            all_timePerReq = 0
        if self.www_count:
            www_timePerReq = self.www_time/self.www_count
        else:
            www_timePerReq = 0
        if self.api_count:
            api_timePerReq = self.api_time/self.api_count
        else:
            api_timePerReq = 0
        return [
            MetricObject("logs.haproxy.blocks", self.unblocks, metric_type="c"),
            MetricObject("logs.haproxy.requests", self.all_count, metric_type="c"),
            MetricObject("logs.haproxy.www.requests", self.www_count, metric_type="c"),
            MetricObject("logs.haproxy.api.requests", self.api_count, metric_type="c"),
            MetricObject("logs.haproxy.responsetime", str(all_timePerReq), metric_type="ms"),
            MetricObject("logs.haproxy.www.responsetime", str(www_timePerReq), metric_type="ms"),
            MetricObject("logs.haproxy.api.responsetime", str(api_timePerReq), metric_type="ms")
        ]
