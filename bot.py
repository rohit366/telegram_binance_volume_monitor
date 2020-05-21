#!/usr/bin/python

# CONFIG
telegram_token = '1016028649:AAFvJC4D1Kae5NNhvipLoxkOFwFkbNuvH4g' # Telegram Bot TOKEN
bot_name = 'Binance Volume Monitor  v0.0.1'
bot_admin = 'Sl0vtski'

bot_subscribed = [
#	-430993883, # test group
	628373642, # zotil
]

bot_admins = [
	55405522, # zotil
	628373642 # slovatski
]

#------------------------------
# Programming
import requests
import json
import logging
import PySignal

from modules.binance_volume_monitor import binance_volume_monitor

from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram import ParseMode

users_list = []
bot_subscribed = bot_subscribed + bot_admins

# LOG
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
					 level=logging.INFO)



class bot:
	def __init__(self):
		global telegram_token
		
		# Start volume monitor
		print("Starting Binance Volume Monitor")
		self.bvm = binance_volume_monitor()
		self.bvm.signals.update.connect(self.notify_ping)
		self.bvm.start()

		
		# bot 
		print("Starting Telegram")
		self.updater = Updater(telegram_token, use_context=True)
		self.dispatcher = self.updater.dispatcher
		
		#-------------------
		# Command handlers
		#-------------------

		# /start
		start_handler = CommandHandler('start', self.start)
		self.dispatcher.add_handler(start_handler)

		 # /stop
		stop_handler = CommandHandler('stop', self.stop_bot)
		self.dispatcher.add_handler(stop_handler)
		
		# /help
		help_handler = CommandHandler('help', self.help_bot)
		self.dispatcher.add_handler(help_handler)

		# /ping
		ping_handler = CommandHandler('ping', self.set_ping)
		self.dispatcher.add_handler(ping_handler)

		# /nvolbtc
		nvolbtc_handler = CommandHandler('nvolbtc', self.set_nvolbtc)
		self.dispatcher.add_handler(nvolbtc_handler)
		
		#-------------------
		
		# Start polling
		self.updater.start_polling()
		self.updater.idle()
	
	def user_msg(self, chat_id, msg):
		self.updater.bot.send_message(chat_id=chat_id, text=msg, parse_mode=ParseMode.MARKDOWN, timeout=15)

	def all_msg(self, msg):
		global users_list
		
		for chat_id in users_list:
			self.updater.bot.send_message(chat_id, msg, parse_mode=ParseMode.MARKDOWN, timeout=15)
	
	#*******************
	# Notify when monitor get results
	#*******************
	def notify_ping(self, m):
		msg = '''
- MOVE DETECTED -

Symbol: %s
PING: %s
Net Vol BTC: %s
Net Vol %% : %s
Recent Total Vol BTC: %s
Recent Vol %% : %s
Recent Net Vol: %s
Datetime(UTC): %s''' % (m['symbol'],m['pings'],m['nvol_btc'],m['nvol_per'],m['rvol_btc'],m['rvol_per'],m['rnvol'],m['ts'])
		
		self.all_msg(msg)
	
	# -------
	# /ping N: FILTER PING TO NOTIFY
	# -------
	def set_ping(self, update, context):
		global bot_admins, bot_admin
		
		user_id = update.message.chat_id
		if user_id not in users_list:
			return
		try:
			_ping = int(context.args[0])
			self.bvm.set_ping(_ping)
			msg = 'Filter set Ping: [%s]' % _ping
		except:
			msg = 'Ping must be a number'

		self.user_msg(update.message.chat_id, msg)
	# -------
	# /nvolbtc N: FILTER NVOLBTC TO NOTIFY
	# -------
	def set_nvolbtc(self, update, context):
		global bot_admins, bot_admin
		
		user_id = update.message.chat_id
		if user_id not in users_list:
			return
		try:
			_nvolbtc = float(context.args[0])
			self.bvm.set_nvolbtc(_nvolbtc)
			msg = 'Filter set Net Vol BTC: [%s]' % _nvolbtc
		except:
			msg = 'Net Vol BTC must be a number'

		self.user_msg(update.message.chat_id, msg)
		pass

	# -------
	# /start: SUBSCRIBE TO THE BOT IF APPLY
	# -------
	def start(self, update, context):
		global users_list, bot_admins, bot_subscribed, bot_admin
		
		user_id = update.message.chat_id
		user_name = update.message.from_user.username
		
		if user_id not in bot_subscribed and user_id not in bot_admins:
			msg = 'To use this bot please contact %s' % bot_admin
			self.user_msg(user_id, msg)
			
			for uid in bot_admins:
				_msg = "User @%s (id: %s) is trying to subscribe to the bot" % (user_name, user_id)
				self.user_msg(uid, _msg)
		else:
			if user_id not in users_list:
				users_list.append(user_id)
				msg = "Welcome to %s. Type /help to see the available commands." % bot_name
			else:
				msg = "You're already subscribed"
			self.user_msg(user_id, msg)
	# -------
	# /stop: STOP BOT SUBSCRIPTION
	# -------
	def stop_bot(self, update, context):
		global users_list, bot_admins, bot_subscribed, bot_admin
		
		user_id = update.message.chat_id
		#user_name = update.message.from_user.username
		
		if user_id in users_list:
			users_list.remove(user_id)
			msg = "Bot stopped"
			self.user_msg(user_id, msg)
	# -------
	# /help: SHOW INFO ABOUT BOT
	# -------
	def help_bot(self, update, context):
		global users_list
		
		user_id = update.message.chat_id
		if user_id not in users_list:
			return
			
		msg = '''
/start (start the bot)
/ping NUM (set the Ping to chase)
/nvolbtc NUM (set the Net Vol BTC to chase)
/stop (stop the bot)
/help (show this help)
		'''
		
		self.user_msg(update.message.chat_id, msg)



def main():
	print("Starting [%s]...." % bot_name)
	while True:
		try:
			b = bot()
		except KeyboardInterrupt:
			print("[X] Quitting...")
			quit()

if __name__ == '__main__':
	main()

