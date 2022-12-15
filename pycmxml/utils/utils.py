import urllib
import os
import sys
import subprocess

# UIX
from rich import print
from rich.progress import track
from rich.progress import Progress


from re import split, sub
from datetime import datetime, date, tzinfo, timedelta
import time


# === === === === === === === ===  Library Section  === === === === === === === === #

# TODO build this as package


def camelize(string):
    return ''.join(a.capitalize() for a in split('([^a-zA-Z0-9])', string)
                   if a.isalnum())


def camel_case(s):
    s = sub(r"(_|-)+", " ", s).title().replace(" ", "")
    return ''.join([s[0].lower(), s[1:]])


# === === === === === === === ===  Library Section  === === === === === === === === #
def date_expand(date):

    dates = []
    ldates = []
    if(str((date).split(':')).split(',')):
        print("range or selection:" + str(date))
        if ((date).find(',') > 0):
            spl_date = str(date).split(',')
            ldates = spl_date
        elif((date).find(':') > 0):
            spl_date = str(date).split(':')
            for date_obj in spl_date:
                dates.append(datetime.strptime(
                    date_obj, '%Y-%m-%d').date())
            days = max(dates)-min(dates)
            ldates.append(str(min(dates)))
            d = 1
            for list_dates in range(days.days):
                ldates.append(str(min(dates)+timedelta(days=d)))
                d = d+1
        else:
            ldates.append(date)
    return ldates
