#!/usr/bin/python3

import configparser
import logging
import requests
import sys
import twitter

from datetime import datetime
from datetime import timedelta

from CET import CET
from Metro import Metro
from CPTM import CPTM
from SPTrans import SPTrans
from transitospagorabot import transitospagorabot

# command line
if len(sys.argv) < 2 :
    configfile = 'transitospagora.ini'
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
CONSUMER_KEY = config['TRANSITOSPAGORA']['TRANSITOSPAGORA_CONSUMER_KEY']
CONSUMER_SECRET = config['TRANSITOSPAGORA']['TRANSITOSPAGORA_CONSUMER_SECRET']
ACCESS_TOKEN_KEY = config['TRANSITOSPAGORA']['TRANSITOSPAGORA_ACCESS_TOKEN_KEY']
ACCESS_TOKEN_SECRET = config['TRANSITOSPAGORA']['TRANSITOSPAGORA_ACCESS_TOKEN_SECRET']
TRAFFICURL = config['TRANSITOSPAGORA']['TRANSITOSPAGORA_TRAFFICURL']
DATAPATH = config['TRANSITOSPAGORA']['TRANSITOSPAGORA_PATH']
METROURL = config['METRO']['METRO_URL']
CPTMURL = config['CPTM']['CPTM_URL']
SPTRANSURL = config['SPTRANS']['SPTRANS_URL']

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

logging.info("Connecting to Telegram")
bot = transitospagorabot(config, logging)


# ### DATA FROM TRAFFIC ### #
logging.info('Retrieving data from traffic: ' + TRAFFICURL)
try : 
    trafficpage = requests.get(TRAFFICURL)
    trafficcontent = trafficpage.content.decode('utf-8')
    logging.info('Parsing data about traffic')
    trafficcet = CET()
    trafficcet.feed(trafficcontent)
    logging.info('Total traffic: ' + str(trafficcet.getTotal()) + ' km')
    newdata = str(trafficcet.getNorth()) + ';' + str(trafficcet.getSouth()) + ';' + str(trafficcet.getEast()) + ';' + str(trafficcet.getWest())

    # retrieve old data
    logging.info('Retrieving data from last traffic update from ' + DATAPATH + '/traffic.txt')
    trafficfile = open(DATAPATH + '/traffic.txt', 'r')
    olddata = trafficfile.read()
    trafficfile.close()

    # post if needed
    if newdata != olddata : 
        update = today + ' ' + time + ' - #Lentidão em SP. ' + 'TOTAL: ' + str(trafficcet.getTotal()) + ' km, ' + 'Z/N: ' + str(trafficcet.getNorth()) + ' km, ' + 'Z/S: ' + str(trafficcet.getSouth()) + ' km, ' + 'Z/L: ' + str(trafficcet.getEast()) + ' km, ' + 'Z/O: ' + str(trafficcet.getWest()) + ' km'
        logging.info('Posting traffic update: ' + update)
        api.PostUpdate(update)
        bot.broadcastUsers(update)

    # save current data
    logging.info('Saving current traffic data into file: ' + DATAPATH + '/traffic.txt')
    trafficfile = open(DATAPATH + '/traffic.txt', 'w')
    trafficfile.write(newdata)
    trafficfile.close()

except request.exception.RequestException as err : 
    logging.error('Cannot request data from CET: ' + str(err))

except twitter.error.TwitterError : 
    logging.error('Cannot post CET data to Twitter: ' + str(err))



# ### DATA FROM METRO AND CPTM ### #
logging.info('Retrieving data from Metro')
try : 
    metropage = requests.get(METROURL)
    metrocontent = metropage.content.decode('utf-8')
    logging.info('Parsing metro status')
    metro = Metro()
    metro.feed(metrocontent)
    
    lines = metro.getLines()
    update = ''
    for idx in sorted(lines.keys()) : 
        if lines[idx]['status'] == 'Operação Normal' or lines[idx]['status'] == '' : 
            continue
        if update != '' : 
            update += ', '
        update += lines[idx]['color'] + ': ' + lines[idx]['status']
    
    if update != '' : 
        update = 'Situação #MetroSP. ' + update
        logging.info('Posting situacao MetroSP: ' + update)
        api.PostUpdate(update)
        bot.broadcastUsers(update)
    else : 
        logging.info('MetroSP: Regular operation')

except request.exception.RequestException as err : 
    logging.error('Cannot request data from Metro: ' + str(err))

except twitter.error.TwitterError : 
    logging.error('Cannot post Metro data to Twitter: ' + str(err))



logging.info('Retrieving data from CPTM')
try : 
    cptmpage = requests.get(CPTMURL)
    cptmcontent = cptmpage.content.decode('utf-8')
    logging.info('Parsing CPTM status')
    cptm = CPTM()
    cptm.feed(cptmcontent)

    lines = cptm.getLines()
    update = ''
    for idx in sorted(lines.keys()) : 
        if lines[idx]['status'] == 'Operação Normal' : 
            continue
        if update != '' : 
            update += ', '
        update += lines[idx]['color'] + ': ' + lines[idx]['status']

    if update != '' : 
        update = 'Situação #CPTM. ' + update
        logging.info('Posting situacao CPTM: ' + update)
        api.PostUpdate(update)
        bot.broadcastUsers(update)
    else : 
        logging.info('CPTM: Regular operation')

except request.exception.RequestException as err : 
    logging.error('Cannot request data from CPTM: ' + str(err))

except twitter.error.TwitterError : 
    logging.error('Cannot post CPTM data to Twitter: ' + str(err))



logging.info('Retrieving data from SPTrans')
try : 
    sptpage = requests.get(SPTRANSURL)
    sptcontent = sptpage.content.decode('utf-8')
    logging.info('Parsing SPTrans status')
    sptrans = SPTrans()
    sptrans.feed(sptcontent)

    newspeed = str(sptrans.getSpeedDowntown()) + ';' + str(sptrans.getSpeedUptown())

    logging.info('Restoring last SPTrans data')
    speedfile = open(DATAPATH + '/sptrans.txt', 'r')
    oldspeed = speedfile.read()
    speedfile.close()

    if newspeed != oldspeed : 
        update = today + ' ' + time + ' - Veloc Média dos ônibus #SPTrans. Sentido Centro: ' + str(sptrans.getSpeedDowntown()) + ' km/h. Sentido Bairro: ' + str(sptrans.getSpeedUptown()) + ' km/h.'
        logging.info('Posting speed SPTrans: ' + update)
        api.PostUpdate(update)
        bot.broadcastUsers(update)

        logging.info('Saving data from SPTrans speed')
        speedfile = open(DATAPATH + '/sptrans.txt', 'w')
        speedfile.write(newspeed)
        speedfile.close()

except request.exception.RequestException as err : 
    logging.error('Cannot request data from SPTrans: ' + str(err))

except twitter.error.TwitterError : 
    logging.error('Cannot post SPTrans data to Twitter: ' + str(err))



