#!/usr/bin/env python

from collections import OrderedDict
import datetime
import json
import math
import sys

import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import MultipleLocator

def main(fnames):
    timestamps = []
    dsData = OrderedDict()
    ds31Data = OrderedDict()
    usData = OrderedDict()

    minDsPower = 10000.0
    maxDsPower = -10000.0
    minDs31Power = 10000.0
    maxDs31Power = -10000.0

    minDsSNR = 10000.0
    maxDsSNR = -10000.0
    minDs31SNR = 10000.0
    maxDs31SNR = -10000.0

    minUsPower = 10000.0
    maxUsPower = -10000.0

    for fname in fnames:
        for line in open(fname):
            j = json.loads(line)

            unixTime = int(j['unixTime'])
            timestamp = datetime.datetime.fromtimestamp(unixTime)
            timestamps.append(timestamp)

            for ds in j['dsTable']:
                ch = ds['Channel ID']
                if ch != '0':
                    if not ch in dsData:
                        dsData[ch] = { 'power': [], 'snr': [] }
                    power = float(ds['Power'].partition(' ')[0])
                    snr = float(ds['SNR / MER'].partition(' ')[0])

                    num_missing = 0
                    if len(dsData[ch]['power']) != len(timestamps)-1:
                        num_missing = (len(timestamps)-1) - len(dsData[ch]['power'])
                        dsData[ch]['power'].extend([0] * num_missing)

                    if len(dsData[ch]['snr']) != len(timestamps)-1:
                        num_missing = (len(timestamps)-1) - len(dsData[ch]['snr'])
                        dsData[ch]['snr'].extend([0] * num_missing)

                    dsData[ch]['power'].append(power)
                    dsData[ch]['snr'].append(snr)

                    if num_missing != 0:
                        continue

                    minDsPower = min(minDsPower, power)
                    maxDsPower = max(maxDsPower, power)

                    minDsSNR = min(minDsSNR, snr)
                    maxDsSNR = max(maxDsSNR, snr)

            for ds in j['d31dsTable']:
                ch = ds['Channel ID']
                if ch != '0':
                    if not ch in ds31Data:
                        ds31Data[ch] = { 'power': [], 'snr': [] }
                    power = float(ds['Power'].partition(' ')[0])
                    snr = float(ds['SNR / MER'].partition(' ')[0])

                    num_missing = 0
                    if len(ds31Data[ch]['power']) != len(timestamps)-1:
                        num_missing = (len(timestamps)-1) - len(ds31Data[ch]['power'])
                        ds31Data[ch]['power'].extend([0] * num_missing)

                    if len(ds31Data[ch]['snr']) != len(timestamps)-1:
                        num_missing = (len(timestamps)-1) - len(ds31Data[ch]['snr'])
                        ds31Data[ch]['snr'].extend([0] * num_missing)

                    ds31Data[ch]['power'].append(power)
                    ds31Data[ch]['snr'].append(snr)

                    if num_missing != 0:
                        continue

                    minDs31Power = min(minDs31Power, power)
                    maxDs31Power = max(maxDs31Power, power)

                    minDs31SNR = min(minDs31SNR, snr)
                    maxDs31SNR = max(maxDs31SNR, snr)

            for us in j['usTable']:
                ch = us['Channel ID']
                if ch != '0':
                    if not ch in usData:
                        usData[ch] = { 'power': [] }
                    power = float(us['Power'].partition(' ')[0])

                    if len(usData[ch]['power']) != len(timestamps)-1:
                        num_missing = (len(timestamps)-1) - len(usData[ch]['power'])
                        usData[ch]['power'].extend([0] * num_missing)

                    usData[ch]['power'].append(power)

                    if num_missing != 0:
                        continue

                    minUsPower = min(minUsPower, power)
                    maxUsPower = max(maxUsPower, power)

    timestamps = mdates.date2num(timestamps)
    xfmt = mdates.DateFormatter('%Y-%m-%d %H:%M')

    plt.figure(1)
    plt.title('DOCSIS 3.0 downstream power')

    ax = plt.gca()
    ax.xaxis.set_major_formatter(xfmt)
    ax.xaxis.set_major_locator(MultipleLocator(60/1440.0))
    ax.xaxis.set_minor_locator(MultipleLocator(30/1440.0))
    ax.yaxis.set_major_locator(MultipleLocator(1.0))
    ax.yaxis.set_minor_locator(MultipleLocator(0.2))
    for k in dsData.keys():
        plt.plot(timestamps, dsData[k]['power'], label=str(k), alpha=0.7)
    plt.xticks(rotation=85, fontsize=4)
    plt.grid(True, which='major', linewidth=1)
    plt.grid(True, which='minor', linewidth=0.5, linestyle='dotted')
    plt.ylim(math.floor(minDsPower)-2, math.ceil(maxDsPower)+1)
    plt.ylabel('Power (dBmV)')
    plt.xlabel('Time')
    ax.legend(loc='lower left', ncol=4, fontsize='xx-small')

    plt.tight_layout()
    plt.savefig('dsPower', dpi=300)

    plt.figure(2)
    plt.title('DOCSIS 3.0 downstream SNR')

    ax = plt.gca()
    ax.xaxis.set_major_formatter(xfmt)
    ax.xaxis.set_major_locator(MultipleLocator(60/1440.0))
    ax.xaxis.set_minor_locator(MultipleLocator(30/1440.0))
    ax.yaxis.set_major_locator(MultipleLocator(1.0))
    ax.yaxis.set_minor_locator(MultipleLocator(0.2))
    for k in dsData.keys():
        plt.plot(timestamps, dsData[k]['snr'], label=str(k), alpha=0.5)
    plt.xticks(rotation=85, fontsize=4)
    plt.grid(True, which='major', linewidth=1)
    plt.grid(True, which='minor', linewidth=0.5, linestyle='dotted')
    plt.ylim(math.floor(minDsSNR)-2, math.ceil(maxDsSNR)+1)
    plt.ylabel('SNR (dB)')
    plt.xlabel('Time')
    ax.legend(loc='lower left', ncol=4, fontsize='xx-small')

    plt.tight_layout()
    plt.savefig('dsSNR', dpi=300)

    plt.figure(3)
    plt.title('DOCSIS 3.0 upstream power')

    ax = plt.gca()
    ax.xaxis.set_major_formatter(xfmt)
    ax.xaxis.set_major_locator(MultipleLocator(60/1440.0))
    ax.xaxis.set_minor_locator(MultipleLocator(30/1440.0))
    ax.yaxis.set_major_locator(MultipleLocator(1.0))
    ax.yaxis.set_minor_locator(MultipleLocator(0.2))
    for k in usData.keys():
        plt.plot(timestamps, usData[k]['power'], label=str(k), alpha=0.7, linewidth=2)
    plt.xticks(rotation=85, fontsize=4)
    plt.grid(True, which='major', linewidth=1)
    plt.grid(True, which='minor', linewidth=0.5, linestyle='dotted')
    plt.ylim(math.floor(minUsPower)-2, math.ceil(maxUsPower)+1)
    plt.ylabel('Power (dBmV)')
    plt.xlabel('Time')
    ax.legend(loc='lower left', fontsize='xx-small')

    plt.tight_layout()
    plt.savefig('usPower', dpi=300)

    plt.figure(4)
    plt.title('DOCSIS 3.1 downstream power')

    ax = plt.gca()
    ax.xaxis.set_major_formatter(xfmt)
    ax.xaxis.set_major_locator(MultipleLocator(60/1440.0))
    ax.xaxis.set_minor_locator(MultipleLocator(30/1440.0))
    ax.yaxis.set_major_locator(MultipleLocator(1.0))
    ax.yaxis.set_minor_locator(MultipleLocator(0.2))
    for k in ds31Data.keys():
        plt.plot(timestamps, ds31Data[k]['power'], label=str(k), alpha=0.7)
    plt.xticks(rotation=85, fontsize=4)
    plt.grid(True, which='major', linewidth=1)
    plt.grid(True, which='minor', linewidth=0.5, linestyle='dotted')
    plt.ylim(math.floor(minDs31Power)-2, math.ceil(maxDs31Power)+1)
    plt.ylabel('Power (dBmV)')
    plt.xlabel('Time')
    ax.legend(loc='lower left', ncol=4, fontsize='xx-small')

    plt.tight_layout()
    plt.savefig('ds31Power', dpi=300)

    plt.figure(5)
    plt.title('DOCSIS 3.1 downstream SNR')

    ax = plt.gca()
    ax.xaxis.set_major_formatter(xfmt)
    ax.xaxis.set_major_locator(MultipleLocator(60/1440.0))
    ax.xaxis.set_minor_locator(MultipleLocator(30/1440.0))
    ax.yaxis.set_major_locator(MultipleLocator(1.0))
    ax.yaxis.set_minor_locator(MultipleLocator(0.2))
    for k in ds31Data.keys():
        plt.plot(timestamps, ds31Data[k]['snr'], label=str(k), alpha=0.5)
    plt.xticks(rotation=85, fontsize=4)
    plt.grid(True, which='major', linewidth=1)
    plt.grid(True, which='minor', linewidth=0.5, linestyle='dotted')
    plt.ylim(math.floor(minDs31SNR)-2, math.ceil(maxDs31SNR)+1)
    plt.ylabel('SNR (dB)')
    plt.xlabel('Time')
    ax.legend(loc='lower left', ncol=4, fontsize='xx-small')

    plt.tight_layout()
    plt.savefig('ds31SNR', dpi=300)

if __name__ == '__main__':
    main(sorted(sys.argv[1:]))
