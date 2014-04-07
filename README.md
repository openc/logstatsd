To install:
    apt-get logtail
    apt-get install python-virtualenv
    virtualenv env.
    pip install -r < requirements.txt

As root:

    PYTHONPATH=. logster -p openc.production --output=statsd --statsd-host=localhost:8125 parsers.HAProxyLogster.HAProxyLogster /path/to/haproxy.log


From a crontab:

    /path/to/project/env/bin/python /path/to/project/env/bin/logster <opts>
