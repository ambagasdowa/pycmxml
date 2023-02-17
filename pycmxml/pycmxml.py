#!/bin/python3

#=== === === === === === === ===  NOTES Section  === === === === === === === === #

# TODO buiild as a package

#=== === === === === === === ===  Import Section  === === === === === === === === #
import pyodbc
import urllib
import os
import sys
import subprocess
import importlib.metadata
# importing element tree
# under the alias of ET
import xml.etree.ElementTree as ET

# UIX
from rich import print
from rich.progress import track
from rich.progress import Progress

from datetime import datetime, date, tzinfo, timedelta
import time

from pycfdi_transform import CFDI40SAXHandler
from pycfdi_transform.formatters.cfdi40.efisco_corp_cfdi40_formatter import EfiscoCorpCFDI40Formatter
from pycfdi_transform.formatters.cfdi40.cda_cfdi40_formatter import CDACFDI40Formatter

from re import split, sub
# Zip
import zipfile
# md5
import hashlib


# Arguments parse for parsing can use sys.arg[1:]:
import logging
import argparse


#from pkg_resources import get_distribution, DistributionNotFound
#import os.path


# Inner libs

import pycmxml.config.config as conf
import pycmxml.utils.utils as lib
import pycmxml.connection.db as db
import pycmxml.datasave.save as dts
import pycmxml.datasave.process as prf

x = ["cmex", "michelin", "Jupiter", "Neptune", "Earth", "Venus"]


def get_indexes(x, xs): return [i for (
    y, i) in zip(xs, range(len(xs))) if x == y]

# print(get_indexes("Earth",x))


def get_args():
    """Get CLI arguments and options"""
    parser = argparse.ArgumentParser(
        prog='pycmxml',
        description='small utility to download zipped xml files and parse contents to a db'
    )
    # parser.add_argument('input')
    # parser.add_argument('output', nargs='?', default=None)

    parser.add_argument('-d', '--dates',
                        default=str(date.today() - timedelta(days=1)),
                        help='set the date for process files inputs can be --dates={[date:range] , [date0,date1] or [date]}  (default: yesterday)')
    parser.add_argument('-c', '--config', action='store_true',
                        help='takes dates from configuration values'
                        )
    parser.add_argument('-x', '--application',
                        help='Set the application to execute'
                        )
    # parser.add_argument('--version', action='version',
    #                     version='%(prog)s {version}'.format(version=__version__))
    return parser.parse_args()


def main():
    sys.tracebacklimit = 0

    args = get_args()
    # === === === === === === === ===  Config Section  === === === === === === === ===
    config = conf.configuration
    # === === === === === === === ===  Library Section  === === === === === === === === #

    print("[green]" + lib.camelize('connecting')+"...[green]")

    for i in track(range(2), description="Processing..."):
        time.sleep(1)  # Simulate work being done

    cursor = db.connect(config)

    print(args)

    if (args.application in x):
        print(f"[cyan]Set app to cursor: [cyan]")
        # then execute prf or
        if (arg.application == 'cmex'):

            if(args.config == False):
                print("[red]Config[red] : [cyan]off[cyan]")
                fecha = args.dates
            else:
                print("[red]Config[red] : [cyan]on[cyan]")
                if (config['service_params']['fecha'] == '?'):
                    fecha = (str(date.today() - timedelta(days=1)))
                else:
                    fecha = str(config['service_params']['fecha'])

            expanded_dates = lib.date_expand(fecha)

            for dt in expanded_dates:
                print("[blue] Execute with fecha : [blue]"+str(dt))
                try:
                    prf.parse(cursor, config, fecha=dt)
                except FileNotFoundError:
                    pass
            cursor.close()

        if (arg.application == 'michelin'):
            print(f"[red]Execute[red]: [cyan]Michelin app[cyan]")
            # try:
            #     mit.exec()
            # except:
            #     pass


if __name__ == '__main__':
    log = logging.getLogger()
    log.setLevel(logging.DEBUG)
    log.addHandler(logging.StreamHandler())

    try:
        main()
    except KeyboardInterrupt:
        pass
