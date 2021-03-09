#!/usr/bin/python3

import configparser
import logging
import requests
import sys
import twitter

from datetime import datetime
from datetime import timedelta

from RadarParserSJC import RadarParserSJC

# command line
if len(sys.argv) < 2 : 
    configfile = 'radarsjc.ini'
else : 
    configfile = sys.argv[1]

# configuration
config = configparser.ConfigParser()
config.read(configfile)

# log configuration
logging.basicConfig(
    format = "%(asctime)s [%(levelname)s] %(message)s", 
    datefmt = '%Y-%m-%d.%H:%M:%S', 
    level = logging.INFO
)

# configuration retrieval 
logging.info('Retrieving configuration from ' + configfile)
CONSUMER_KEY = config['RADARSJC']['RADARSJC_CONSUMER_KEY']
CONSUMER_SECRET = config['RADARSJC']['RADARSJC_CONSUMER_SECRET']
ACCESS_TOKEN_KEY = config['RADARSJC']['RADARSJC_ACCESS_TOKEN_KEY']
ACCESS_TOKEN_SECRET = config['RADARSJC']['RADARSJC_ACCESS_TOKEN_SECRET']
SJCRADAR_URL = config['RADARSJC']['RADARSJC_URL']
SUNDAYPATH = config['RADARSJC']['RADARSJC_PATH']

# date and time 
ts = datetime.now()
today = "%02d/%02d/%04d" % (ts.day, ts.month, ts.year)
time = "%02d:%02d:%02d" % (ts.hour, ts.minute, ts.second)
logging.info('Detecting current date: ' + today)

# connect to twitter
logging.info("Conneting to Twitter")
api = twitter.Api(
    consumer_key        = CONSUMER_KEY.encode('utf8'),
    consumer_secret        = CONSUMER_SECRET.encode('utf8'),
    access_token_key    = ACCESS_TOKEN_KEY.encode('utf8'),
    access_token_secret    = ACCESS_TOKEN_SECRET.encode('utf8')
)

# retrieve data from SJC radars
logging.info('Retrieving data from SJC radars: ' + SJCRADAR_URL)
sjcradarpage = requests.get(SJCRADAR_URL)
content = sjcradarpage.content.decode('utf-8')
logging.info('Parsing data from SJC radars')
sjc = RadarParserSJC()
sjc.feed(content)

# twitting data from SJC radars
if today in sjc.getRadars() :
    locations = sjc.getRadars()[today]
    update = ''
    warning = ''
    for location in locations : 
        if update != '' : 
            update += ' - '
        update += location['street']
        speed = int(location['speed'].split('k')[0])
        if speed < 60 : 
            if warning != '' : 
                warning += ' - '
            warning += location['street']

    if update != '' : 
        update = '#Radares ' + today + ' ' + time + ': ' + update
        logging.info('Twitter update size: ' + str(len(update)))
        logging.info('Twitter update: ' + update)
        api.PostUpdate(update)
    else : 
        logging.error('No radar streets for today')

    if warning != '' : 
        warning = 'ATENÇÃO! #Radares com fiscalização #irregular ' + today + ' ' + time + ': ' + warning
        logging.info('Twitter warning size: ' + str(len(warning)))
        logging.info('Twitter warning: ' + warning)
        api.PostUpdate(warning)
    else : 
        logging.error("No warnings for today's radars")
else : 
    logging.error('Cannot find radar addresses for today')


if ts.weekday() == 5 : 
    logging.info('On saturdays save sunday information')

    ts1 = ts + timedelta(days=1)
    tomorrow = "%02d/%02d/%04d" % (ts1.day, ts1.month, ts1.year)
    locations = sjc.getRadars()[tomorrow]
    update = ''
    warning = ''
    logging.info('Looking for radars on sunday: ' + tomorrow)
    if tomorrow in sjc.getRadars() :
        for location in locations : 
            if update != '' : 
                update += ' - '
            update += location['street']
            speed = int(location['speed'].split('k')[0])
            if speed < 60 : 
                if warning != '' : 
                    warning += ' - '
                warning += location['street']

        if update != '' : 
            update = '#Radares ' + tomorrow + ' ' + time + ': ' + update
        else : 
            logging.error('No radar streets for today')

        if warning != '' : 
            warning = 'ATENÇÃO! #Radares com fiscalização #irregular ' + tomorrow + ' ' + time + ': ' + warning
        else : 
            logging.error("No warnings for tomorrow's radar")
            

        logging.info('Saving sunday update: ' + update)
        updfile = open(SUNDAYPATH + '/sunday.upd', 'w')
        updfile.write(update)
        updfile.close()

        logging.info('Saving sunday warning: ' + warning)
        wrnfile = open(SUNDAYPATH + '/sunday.wrn', 'w')
        wrnfile.write(warning)
        wrnfile.close()
    
elif ts.weekday() == 6 : 
    logging.info('On sundays retrieve data from file')
    updfile = open(SUNDAYPATH + '/sunday.upd', 'r')
    update = updfile.read()
    logging.info('Twitter update size: ' + str(len(update)))
    logging.info('Twitter update: ' + update)
    api.PostUpdate(update)

    wrnfile = open(SUNDAYPATH + '/sunday.wrn', 'r')
    warning = wrnfile.read()
    logging.info('Twitter warning size: ' + str(len(warning)))
    logging.info('Twitter warning: ' + warning)
    api.PostUpdate(warning)

     



