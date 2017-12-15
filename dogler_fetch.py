#!/usr/bin/env python

import collections
import datetime
import json
import re
import sys
import time
import traceback

from lxml import html
import requests
import requests.auth

status_url          = 'http://192.168.100.1/DocsisStatus.asp'
log_url             = 'http://192.168.100.1/EventLog.asp'

hurrdurr            = requests.auth.HTTPBasicAuth('admin', 'password')
sleep_interval      = 3600 - 0.05
strftime_format     = '%Y-%m-%dT%H:%M:%S'

xpath_startup       = '//*[@id="startup_procedure_table"][1]/tr[%s]/td[%s]//text()'
xpath_dsTable       = '//*[@id="dsTable"][1]/tr[%s]/td[%s]//text()'
xpath_usTable       = '//*[@id="usTable"][1]/tr[%s]/td[%s]//text()'
xpath_d31dsTable    = '//*[@id="d31dsTable"][1]/tr[%s]/td[%s]//text()'
xpath_d31usTable    = '//*[@id="d31usTable"][1]/tr[%s]/td[%s]//text()'
xpath_cmTime        = '//td[@id="Current_systemtime"]//text()'

event_table_re      = re.compile("var xmlFormat = '(<docsDevEventTable>.*</docsDevEventTable>)'")

g_last_log = ''

def extract_keys(tree, xpath, n):
    keys = []
    tr = 1
    for td in range(1, n + 1):
        k = tree.xpath(xpath % (tr, td))[0].strip()
        keys.append(k)
    return keys

def extract_items(tree, xpath, n, m):
    keys = extract_keys(tree, xpath, n)
    vals = []
    for tr in range(2, m + 2):
        row = collections.OrderedDict()
        for td in range(1, n + 1):
            k = keys[td-1]
            try:
                v = tree.xpath(xpath % (tr, td))[0].strip()
            except IndexError:
                v = ''
            row[k] = v
        vals.append(row)
    return vals

def extract_data(data):
    tree = html.fromstring(data)
    d = collections.OrderedDict()
    d['cmTime']     = tree.xpath(xpath_cmTime)[1].strip()
    d['startup']    = extract_items(tree, xpath_startup, 3, 6)
    d['dsTable']    = extract_items(tree, xpath_dsTable, 9, 32)
    d['usTable']    = extract_items(tree, xpath_usTable, 7, 8)
    d['d31dsTable'] = extract_items(tree, xpath_d31dsTable, 7, 2)
    d['d31usTable'] = extract_items(tree, xpath_d31usTable, 7, 2)
    return d

def get_data(url):
    r = requests.get(url, auth=hurrdurr)
    if r.status_code == 401:
        # HURRRRRRR DURRRRRRR
        r = requests.get(url, auth=hurrdurr)
    return r.text

def fetch_status(dname):
    now = datetime.datetime.now()
    output = open(dname + '/status.' + now.strftime('%Y%m%d') + '.json', 'a')
    d = collections.OrderedDict()
    d['time'] = now.strftime(strftime_format)
    d['unixTime'] = int(now.strftime('%s'))
    d.update(extract_data(get_data(status_url)))
    json.dump(d, output)
    output.write('\n')
    return d['cmTime']

def extract_log(data):
    tree = html.fromstring(data)
    try:
        script = tree.xpath('//script/text()')[0]
        log = event_table_re.search(script).groups()[0]
        return log
    except:
        return ''

def get_last_log_line(dname):
    global g_last_log

    now = datetime.datetime.now()
    log_fname = dname + '/log.' + now.strftime('%Y%m%d') + '.json'

    try:
        log_file = open(log_fname, 'r')
    except IOError:
        return

    log = ''
    for log in log_file:
        pass

    try:
        j = json.loads(log)
    except:
        return

    g_last_log = j['log']

def fetch_log(dname, cmtime):
    global g_last_log

    log = extract_log(get_data(log_url))
    if log == g_last_log:
        return
    g_last_log = log

    if log != '':
        now = datetime.datetime.now()
        output = open(dname + '/log.' + now.strftime('%Y%m%d') + '.json', 'a')
        d = collections.OrderedDict()
        d['time'] = now.strftime(strftime_format)
        d['unixTime'] = int(now.strftime('%s'))
        d['cmTime'] = cmtime
        d['log'] = log
        json.dump(d, output)
        output.write('\n')

def main(dname):
    get_last_log_line(dname)

    while True:
        now = datetime.datetime.now()
        try:
            cmtime = fetch_status(dname)
            fetch_log(dname, cmtime)
        except Exception:
            traceback.print_exc()
            time.sleep(10)
            continue
        after = datetime.datetime.now()

        secs_taken = (after - now).total_seconds()
        secs_sleep = sleep_interval - secs_taken
        if secs_sleep < 0:
            secs_sleep = sleep_interval

        print 'Fetches took %.3f secs, sleeping for %.3f secs' % (secs_taken, secs_sleep)
        time.sleep(secs_sleep)

if __name__ == '__main__':
    main(sys.argv[1])
