#!/usr/bin/env python
import sys
import logging
import os
import re
import datetime
import json
from ftplib import FTP


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

LINE_RE = re.compile(r"^\S{10}\s+\d+\s+\w+\s+\w+\s+\d+\s+(\w+\s+\d+\s+\S+)\s+(\S+)-\d+\.log$")
TIME_RE = re.compile("(\d+):(\d+)")
THIS_YEAR = datetime.datetime.today().year

CONFIG = {}

def load_config():
    config = json.load(open('config.json'))
    for site in config['sites']:
        site['regex'] = re.compile(site['regex'])
    return config

def process_line(data, line):
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
        data.append((timestamp, filename))
        

def graph(since, by_site):
    import matplotlib.pyplot as plt
    sites = by_site.keys()
    site_count = len(sites)

    ind = range(site_count)
    width = 0.35

    widthscale = len(sites)/9 
    figsize = (8*widthscale,6) # fig size in inches (width,height)
    fig = plt.figure(figsize = figsize) # set the figsize

    ax = fig.add_subplot(111)
    counts = [by_site[s] for s in sites]
    logger.info("site_count: %r", site_count)
    rects1 = ax.bar(ind, counts)
    ax.set_ylabel('Uses')
    ax.set_title('Usage by site since %s' % since)
    ax.set_xticks([i+width for i in ind])
    ax.set_xticklabels(sites, rotation=90)
    plt.subplots_adjust(bottom=0.55)
    plt.show()


def main(argv=None):
    global CONFIG
    if argv is None:
        argv = sys.argv
    logging.basicConfig()
    CONFIG = load_config()

    data = []

    host = os.environ['YUSADGE_HOST']
    user = os.environ['YUSADGE_USER']
    password = os.environ['YUSADGE_PASSWORD']
    path = os.environ['YUSADGE_PATH']

    ftp = FTP(host, user, password)
    ftp.cwd(path)
    ftp.retrlines('LIST', lambda line: process_line(data, line))

    #for line in open('sample.txt'):
    #    process_line(data, line)
   
    by_site = {}
    data.sort(reverse=True)
    since = data[-1][0]
    for timestamp, hostname in data:
        found_site = False
        for site in CONFIG['sites']:
            site_match = site['regex'].match(hostname)
            if site_match:
                found_site = True
                if site['name'] == 'Unknown':
                    site_name = site_match.group(1)
                else:
                    site_name = "%s %s" % (site['organization'], site['name']) 
                try:
                    by_site[site_name] += 1
                except KeyError:
                    by_site[site_name] = 1
                break
        if not found_site:
            msg = "Invalid site for %s" % hostname
            logger.warn(msg)

    graph(since, by_site)

if __name__ == '__main__':
    sys.exit(main())
