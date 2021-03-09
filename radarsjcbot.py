#!/usr/bin/python3

import configparser
import dbm
import json
import logging
import sys

from datetime import datetime

from telegram.ext import Updater, CommandHandler


class radarsjcbot : 
    def __init__(self, config, logging) : 
        self.apikey = config['TELEGRAM']['RADARSJC_APIKEY']
        self.usersfile = config['TELEGRAM']['RADARSJC_USERS']
        self.adminsfile = config['TELEGRAM']['RADARSJC_ADMINS']
        self.helpfile = config['TELEGRAM']['RADARSJC_HELPFILE']
        self.adminhelpfile = config['TELEGRAM']['RADARSJC_ADMINHELPFILE']

        self.logging = logging

        self.updater = Updater(self.apikey, use_context = True)
        self.updater.dispatcher.add_handler(CommandHandler('start', self.hndlrStart))
        self.updater.dispatcher.add_handler(CommandHandler('help', self.hndlrHelp))
        self.updater.dispatcher.add_handler(CommandHandler('seguir', self.hndlrFollow))
        self.updater.dispatcher.add_handler(CommandHandler('cancelar', self.hndlrCancel))

        self.updater.dispatcher.add_handler(CommandHandler('listusers', self.hndlrListUsers))
        self.updater.dispatcher.add_handler(CommandHandler('listadmins', self.hndlrListAdmins))
        self.updater.dispatcher.add_handler(CommandHandler('broadcast', self.hndlrBroadcast))
        self.updater.dispatcher.add_handler(CommandHandler('newadmin', self.hndlrNewAdmin))

        self.updater.dispatcher.add_error_handler(self.hndlrError)


    def start(self) :
        self.logging.info('Starting Radares SJC bot') 
        self.updater.start_polling()
        self.broadcastAdmins("Starting Radares SJC Bot v0.1")
        self.updater.idle()

    def checkAdmin(self, userid) : 
        buserid = userid.encode('ascii')
        with dbm.open(self.adminsfile, 'r') as db : 
            if buserid in db.keys() : 
                return True
        return False

    def broadcastAdmins(self, message) : 
        with dbm.open(self.adminsfile, 'r') as db : 
            for buserid in db.keys() : 
                userid = buserid.decode()
                self.updater.bot.send_message(str(userid), message)

    def broadcastUsers(self, message) : 
        with dbm.open(self.usersfile, 'r') as db : 
            for buserid in db.keys() : 
                userid = buserid.decode()
                self.updater.bot.send_message(str(userid), message)

    def hndlrStart(self, update, context) : 
        message = """
            Radares SJC Bot. Bem-vindo.
            Digite /help para lista de comandos
            Digite /seguir para receber atualizações no Telegram
        """
        update.message.reply_text(message)

    def hndlrHelp(self, update, context) : 
        with open(self.helpfile, 'r') as file : 
            update.message.reply_text(file.read())

        adminid = str(update.message.from_user.id)
        if self.checkAdmin(adminid) : 
            adminname = update.message.from_user.username
            self.logging.info('Admin help requested by admin ' + adminname + ' (userid: ' + adminid + ')')
            with open(self.adminhelpfile, 'r') as file : 
                update.message.reply_text(file.read())

    def hndlrFollow(self, update, context) : 
        userid = str(update.message.from_user.id)
        buserid = userid.encode('ascii')
        username = update.message.from_user.username

        ts = datetime.now()
        timestamp = "%04d/%02d/%02d %02d:%02d:%02d" % (ts.year, ts.month, ts.day, ts.hour, ts.minute, ts.second)

        message = ''
        with dbm.open(self.usersfile, 'c') as db : 
            if buserid in db.keys() : 
                data = json.loads(db.get(userid))
                message = "Assinado desde " + data['since']
            
            else : 
                data = str(json.dumps({'user': username, 'since': timestamp}))
                db[buserid] = data
                self.logging.info('New user follow request: ' + username + ' (userid: ' + userid + ')')
                self.broadcastAdmins('New user follow: ' + username + '(userid: ' + userid + ')')
                message = 'Assinado desde ' + timestamp

        update.message.reply_text(message)

    def hndlrCancel(self, update, context) : 
        userid = str(update.message.from_user.id)
        buserid = userid.encode('ascii')
        username = update.message.from_user.username

        message = 'Não encontrada assinatura para usuário: ' + username
        with dbm.open(self.usersfile, 'w') as db : 
            if buserid in db.keys() :
                del db[buserid]
                self.logging.info('Stop follow request by user: ' + username + ' (userid: ' + userid + ')')
                self.broadcastAdmins('User stopped following bot: ' + username + ' (userid: ' + userid + ')')
                message = 'Assinatura cancelada para usuário: ' + username
        update.message.reply_text(message)        

    def hndlrListUsers(self, update, context) : 
        adminid = str(update.message.from_user.id)
        if self.checkAdmin(adminid) :
            adminname = update.message.from_user.username
            self.logging.info('List users request by admin: ' + adminname + ' (userid: ' + adminid + ')')
            message = ''
            with dbm.open(self.usersfile, 'r') as db :
                message = 'Total usuários: ' + str(len(db.keys())) + "\n" 
                for buserid in db.keys() : 
                    data = json.loads(db.get(buserid))
                    message += data['user'] + ",\n"
        
            update.message.reply_text(message)
                    

    def hndlrListAdmins(self, update, context) : 
        adminid = str(update.message.from_user.id)
        if self.checkAdmin(adminid) : 
            adminname = update.message.from_user.username
            self.logging.info('List admins request by admin: ' + adminname + ' (userid: ' + adminid + ')')
            message = ''
            with dbm.open(self.adminsfile, 'r') as db : 
                message = 'Total administradores: ' + str(len(db.keys())) + "\n"
                for buserid in db.keys() : 
                    data = json.loads(db.get(buserid))
                    message += data['user'] + ",\n"
            
            update.message.reply_text(message)

    def hndlrBroadcast(self, update, context) : 
        adminid = str(update.message.from_user.id)
        if self.checkAdmin(adminid) :
            adminname = update.message.from_user.username
            self.logging.info('User broadcast requested by admin: ' + adminname + ' (userid: ' + adminid + ')')
            message = ' '.join(update.message.text.split(' ')[1:])
            self.logging.info('User broadcast: ' + message)
            self.broadcastUsers(message) 

    def hndlrNewAdmin(self, update, contextd) : 
        adminid = str(update.message.from_user.id)
        adminname = update.message.from_user.username
        newadminname = ' '.join(update.message.text.split(' ')[1:])
        bnewadminid = b''
        with dbm.open(self.usersfile, 'r') as db :
            for buserid in db.keys() :
                data = json.loads(db.get(buserid))
                if data['user'] == newadminname :
                    bnewadminid = buserid
        
        if bnewadminid == b'' : 
            update.message.reply_text('No user ' + newadminname + ' found')

        else : 
            with dbm.open(self.adminsfile, 'c') as db : 
                if bnewadminid in db.keys() : 
                    data = json.loads(db.get(bnewadminid))
                    update.message.reply_text('Administrador desde ' + data['since'])
            
                else : 
                    ts = datetime.now()
                    timestamp = "%04d/%02d/%02d %02d:%02d:%02d" % (ts.year, ts.month, ts.day, ts.hour, ts.minute, ts.second)

                    data = str(json.dumps({'user': newadminname, 'since': timestamp}))

                    db[bnewadminid] = data
                    self.logging.info('New administrator request: ' + adminname + ' (userid: ' + adminid + ')')
                    self.logging.info('New administrator: ' + newadminname + ' (userid: ' + bnewadminid + ')')
                    # self.broadcastAdmins('New administrator: ' + username + '(userid: ' + userid + ')')
                    update.message.reply_text('Administrador desde ' + timestamp)



    def hndlrError(self, update, context) :
        self.logging.error('Update "%s" caused error "%s"', update, context.error)



if __name__ == '__main__' : 
    if len(sys.argv) < 2 : 
        configfile = 'radarsjc.ini'
    else : 
        configfile = sys.argv[1]

    # configuration
    config = configparser.ConfigParser()
    config.read(configfile)

    # logging
    logging.basicConfig(
        format = "%(asctime)s [%(levelname)s] %(message)s",
        datefmt = '%Y-%m-%d.%H:%M:%S',
        level = logging.INFO
    )

    bot = radarsjcbot(config, logging)
    bot.start()

