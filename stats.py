#!/usr/bin/env python
import sys
import logging
import os
import re
import datetime
from ftplib import FTP


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

LINE_RE = re.compile(r"^\S{10}\s+\d+\s+\w+\s+\w+\s+\d+\s+(\w+\s+\d+\s+\S+)\s+(\S+)\.log$")
TIME_RE = re.compile("(\d+):(\d+)")
THIS_YEAR = datetime.datetime.today().year

DATA = []

def process_line(line):
    logger.debug("line: %s", line)
    line_match = LINE_RE.match(line)
    if line_match:
        logger.debug("line_match: %r", line_match.groups())
        date_string, filename = line_match.groups()
        try:
            ts = datetime.datetime.strptime(date_string, "%b %d %H:%M")
            timestamp = datetime.datetime(THIS_YEAR, ts.month, ts.day, ts.hour,
                                          ts.minute)
        except ValueError:
            timestamp = datetime.datetime.strptime(date_string, "%b %d %Y")
        logger.debug("timestamp: %r", timestamp)
        DATA.append((timestamp, filename))
        

def main(argv=None):
    if argv is None:
        argv = sys.argv
    logging.basicConfig()
    host = os.environ['YUSADGE_HOST']
    user = os.environ['YUSADGE_USER']
    password = os.environ['YUSADGE_PASSWORD']
    path = os.environ['YUSADGE_PATH']

    ftp = FTP(host, user, password)
    ftp.cwd(path)
    ftp.retrlines('LIST', process_line)
    print sorted(DATA, reverse=True)[:5]


if __name__ == '__main__':
    sys.exit(main())
