#!/bin/python3

#=== === === === === === === ===  NOTES Section  === === === === === === === === #

# TODO buiild as a package

#=== === === === === === === ===  Import Section  === === === === === === === === #
import sys
import pyodbc
import urllib
import os
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
# libs inherit for cmex
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
        description='Small utility to download zipped xml files and parse contents to a db'
    )
    # parser.add_argument('input')
    # parser.add_argument('output', nargs='?', default=None)

    parser.add_argument('-d', '--dates',
                        default=str(date.today() - timedelta(days=1)),
                        help='Set the date for process files inputs can be --dates={[date:range] , [date0,date1] or [date]}  (default: yesterday)')
    parser.add_argument('-c', '--config', action='store_true',
                        help='Takes dates from configuration values'
                        )
    parser.add_argument('-cc', '--createConfig',action='store_true',
                        help='Create configuration files '
                        )
    parser.add_argument('-x', '--application',
                        help='Set the application to execute [cmex, michelin ]'
                        )
    parser.add_argument('-m', '--modules',
                        help='Set the modules to run for get data from api ws , use whith --application params, and get entry as  module1,module2,...'
                        )
    parser.add_argument('-v', '--debug', action='store_true',
                        help='Set the debug output to true'
                        )
    # parser.add_argument('--version', action='version',
    #                     version='%(prog)s {version}'.format(version=__version__))
    # parser.print_help()
    # parser.parse_args(['-h'])
    return parser.parse_args()


def main():
    # sys.tracebacklimit = 0

    args = get_args()
    # === === === === === === === ===  Config Section  === === === === === === === ===
    if (args.createConfig):
        conf.create_config()
        print("exit?")
        exit()

    config = conf.configuration
    # === === === === === === === ===  Library Section  === === === === === === === === #
    debug = args.debug
    if debug :
        print("[green]" + lib.camelize('initializing')+"...[green]")
        print(args)

    if (args.application in x):
        if debug :
            print(f"[cyan]Set app to cursor: [cyan]")
        # then execute prf or
        if (args.application == 'cmex'):
            if debug :
                for i in track(range(2), description="Connecting to database ..."):
                    time.sleep(1)  # Simulate work being done
            cursor = db.connect(config)

            if(args.config == False):
                if debug:
                    print("[red]Config[red] : [cyan]off[cyan]")
                fecha = args.dates
            else:
                if debug:
                    print("[red]Config[red] : [cyan]on[cyan]")
                if (config['service_params']['fecha'] == '?'):
                    fecha = (str(date.today() - timedelta(days=1)))
                else:
                    fecha = str(config['service_params']['fecha'])

            expanded_dates = lib.date_expand(fecha)

            for dt in expanded_dates:
                if debug:
                    print("[blue] Execute with fecha : [blue]"+str(dt))
                try:
                    prf.parse(cursor, config, fecha=dt)
                except FileNotFoundError:
                    pass
            cursor.close()

        if (args.application == 'michelin'):
            if debug:
                for i in track(range(2), description="Connecting to database ..."):
                    time.sleep(1)  # Simulate work being done
            cursor = db.connect(config)
            if debug:
                print(f"[red]Execute[red]: [cyan]Michelin app[cyan]")
            try:
                prf.fetch_api(cursor, args , False)
            except:
                pass
    else:
        print(
            f"\n[green]must specified an application to execute with -x OR --application parameter[green]")


if __name__ == '__main__':
    log = logging.getLogger()
    log.setLevel(logging.DEBUG)
    log.addHandler(logging.StreamHandler())

    try:
        main()
    except KeyboardInterrupt:
        pass
