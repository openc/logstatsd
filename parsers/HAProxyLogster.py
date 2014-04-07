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
        self.time = 0
        self.count = 0.0
        self.regex = re.compile('.*?\d+/\d+/\d+/\d+/(\d+).* (\S+) HTTP.*')

    def parse_line(self, line):
        try:
            # Apply regular expression to each line and extract
            # interesting bits.
            time, url = self.regex.match(line).groups()
            self.time += int(time)
            self.count += 1
            if url == "/unblock_requests/new":
                self.unblocks += 1
        except Exception, e:
            raise LogsterParsingException, "regmatch or contents failed with %s" % e


    def get_state(self, duration):
        # Return a list of metrics objects
        if self.count:
            timePerReq = self.time/self.count
        else:
            timePerReq = 0
        return [
            MetricObject("haproxy.blocks", self.unblocks, metric_type="c"),
            MetricObject("openc.production.haproxy.responsetime", str(timePerReq), metric_type="ms")
        ]
