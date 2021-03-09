#!/usr/bin/python3

import configparser
import dbm
import logging
import requests
import sys
import twitter

from datetime import datetime
from datetime import timedelta

from CGE import CGE
from SAISP import SAISP
from alagamentosbot import alagamentosbot

# command line
if len(sys.argv) < 2 :
    configfile = 'radarsjc.ini'
else :
    configfile = sys.argv[1]

if len(sys.argv) < 3 : 
    execmode = 'FLOOD'
else : 
    execmode = sys.argv[2]

if execmode not in ['FLOOD', 'PLUV'] : 
    execmode = 'FLOOD'

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
CONSUMER_KEY = config['ALAGAMENTOS']['ALAGAMENTOS_CONSUMER_KEY']
CONSUMER_SECRET = config['ALAGAMENTOS']['ALAGAMENTOS_CONSUMER_SECRET']
ACCESS_TOKEN_KEY = config['ALAGAMENTOS']['ALAGAMENTOS_ACCESS_TOKEN_KEY']
ACCESS_TOKEN_SECRET = config['ALAGAMENTOS']['ALAGAMENTOS_ACCESS_TOKEN_SECRET']
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

# connect to Telegram
logging.info("Connecting to Telegram")
bot = alagamentosbot(config, logging)

if execmode == 'FLOOD' : 
    BASEURL = config['ALAGAMENTOS']['ALAGAMENTOS_BASE']
    DETAILURL = config['ALAGAMENTOS']['ALAGAMENTOS_DETAIL']
    DATAPATH = config['ALAGAMENTOS']['ALAGAMENTOS_PATH']
    FLOODINGDBM = config['ALAGAMENTOS']['ALAGAMENTOS_CURRENT']

    # ### DATA FROM TOTAL FLOODINGS ### #
    logging.info('Retrieving data from total floodings: ' + BASEURL)
    basepage = requests.get(BASEURL)
    basecontent = basepage.content.decode('utf-8')
    logging.info('Parsing data total floodings')
    basecge = CGE()
    basecge.feed(basecontent)
    logging.info('Total active floodings: ' + str(basecge.getTotalAtivos()))
    
    # retrieve last data from file
    logging.info('Retrieving data from last data retrieval')
    totalfile = open(DATAPATH + '/lasttotal.txt', 'r')
    lasttotal = int(totalfile.read())
    totalfile.close()
    
    if lasttotal != basecge.getTotalAtivos() : 
        update = today + ' ' + time + ' - #Alagamentos ativos em SP: ' + str(basecge.getTotalAtivos())
        logging.info('Twitter update: ' + update)
        api.PostUpdate(update)
        bot.broadcastUsers(update)
    
        totalfile = open(DATAPATH + '/lasttotal.txt', 'w')
        totalfile.write(str(basecge.getTotalAtivos()))
        totalfile.close()
    else : 
        logging.info('No change on total floodings')
    
    
    
    # ### DETAIL DATA ABOUT FLOODINGS ### #
    logging.info('Retrieving details from floodings: ' + DETAILURL)
    detailpage = requests.get(DETAILURL)
    detailcontent = detailpage.content.decode('utf-8')
    logging.info('Parsing detail flooding data')
    detailcge = CGE() 
    detailcge.feed(detailcontent)
    
    # build flooding data
    cgefloodings = detailcge.getFloodings()
    newfloodings = []
    for flooding in cgefloodings : 
        logging.info('ALAGAMENTO ' + flooding['type'] +  ': ' + 
            flooding['local'] + ' x ' + 
            flooding['reference'] + ' (' + 
            flooding['direction'] + ')'
        )
        newfloodings.append('ALAGAMENTO ' + flooding['type'] +  ': ' + 
            flooding['local'] + ' x ' + 
            flooding['reference'] + ' (' + 
            flooding['direction'] + ')'
        )
    logging.info('Total parsed floodings: ' + str(len(newfloodings)))

    oldfloodings = []
    with dbm.open(FLOODINGDBM, 'c') as db : 
        for bflooding in db.keys() : 
            oldfloodings.append(bflooding.decode())

    logging.info('Total saved floodings: ' + str(len(oldfloodings)))

    # removed floodings
    for flooding in oldfloodings : 
        if flooding not in newfloodings : 
            update = today + ' ' + time + ' FIM #' + flooding
            logging.info('Flooding end: ' + flooding)
            api.PostUpdate(update)
            bot.broadcastUsers(update)
    
    # new floodings 
    for flooding in newfloodings : 
        if flooding not in oldfloodings : 
            update = today + ' ' + time + ' INICIO #' + flooding
            logging.info('Flooding start: ' + flooding)
            api.PostUpdate(update)
            bot.broadcastUsers(update)
    
    # save flooding data
    logging.info('Saving flooding details')
    with dbm.open(FLOODINGDBM, 'n') as db : 
        for flooding in newfloodings : 
            bflooding = flooding.encode('ascii')
            db[bflooding] = 'true'

    
elif execmode == 'PLUV' : 
    QUERYURL = config['SAISP']['ESTACOES_QUERYURL']
    LISTS = config['SAISP']['ESTACOES_LISTS'].split(';')

    logging.info('Retrieve data from telemetry')
    for LIST in LISTS :
        telem = LIST.split(',')[0]
        telemname = LIST.split(',')[1]
		
        stations = config['SAISP'][telem].split(';')
        update = ''
        for station in stations : 
            stationname = station.split(',')[0]
            stationid = station.split(',')[1]
            url = QUERYURL + stationid
            headers = {'referer': 'https://www.cgesp.org/'}
            logging.info('Retrieving data from ' + stationname + ': ' + url)

            stationpage = requests.get(url, headers=headers)
            stationcontent = stationpage.content.decode('utf-8')
            parser = SAISP()
            parser.feed(stationcontent)
            pluv = round(parser.getPluv(), 1)
            if pluv > 0 : 
                logging.info(stationname + ': '+ f'{pluv:.1f}' + ' mm')
                update += stationname + ': ' + f'{pluv:.1f}' + ' mm. '
            if pluv >= 10.0 and pluv < 50.0 : 
                logging.info('Detected strong rain on ' + stationname + ': ' + f'{pluv:.1f}' + ' mm')
                heavyrain = '#ATENÇÃO! Chuva forte detectada em ' + stationname + ': ' + f'{pluv:.1f}' + ' mm'
                api.PostUpdate(heavyrain)
                bot.broadcastUsers(heavyrain)
            if pluv >= 50.0 : 
                logging.info('Detected intense rain on ' + stationname + ': ' + f'{pluv:.1f}' + ' mm')
                intenserain = '#ATENÇÃO! Chuva intensa detectada em ' + stationname + ': ' + f'{pluv:.1f}' + ' mm'
                api.PostUpdate(intenserain)
                bot.broadcastUsers(intenserain)

    

        if update != '' : 
            update = '#Chuva 60 mins ' + telemname + ': ' + update
            api.PostUpdate(update)
            bot.broadcastUsers(update)

