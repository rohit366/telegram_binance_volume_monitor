#!/usr/bin/python

import time
import threading
import requests
import json
from PySignal import ClassSignal

class binance_volume_monitor_signals:
	update = ClassSignal()

class binance_volume_monitor(threading.Thread):
	url = 'https://agile-cliffs-23967.herokuapp.com/ok'

	def __init__(self):
		threading.Thread.__init__(self)
		self.setDaemon(True)

		self.signals = binance_volume_monitor_signals()

		# starting variables
		self.max_ping = 0
		self.max_net_vol_btc = 0
		self.last_id = 0
		self.pings = {}
		
	def run(self):
		while True:
			self.update()
			time.sleep(30)

	def set_ping(self, ping):
		self.max_ping = int(ping)
	
	def set_nvolbtc(self, nvolbtc):
		self.max_net_vol_btc = float(nvolbtc)

	def update(self):
		r = requests.post(self.url)
		r = json.loads(r.text)['resu']

		#print(r)
		#print('Set ping [%s]' % self.max_ping)
		#print('Set nvol [%s]' % self.max_net_vol_btc)

		last_id = r[-1]
		if self.last_id == 0:
			self.last_id = last_id
		elif last_id > self.last_id:
			self.last_id = last_id
		else:
			return
		
		if len(r) > 1:
			for i in r:
				if type(i) != int:
					l = i.split('|')

					symbol = l[0]
					data = {
						'symbol': l[0],
						'pings': l[1],
						'nvol_btc': l[2],
						'nvol_per': l[3],
						'rvol_btc': l[4],
						'rvol_per': l[5],
						'rnvol': l[6],
						'ts': l[7]
					}

					self.pings[symbol] = data
					
					if self.max_ping > 0:
						if int(data['pings']) < self.max_ping:
							#notify
							ping_notify = True
						else:
							ping_notify = False
					else:
						ping_notify = True
					
					if self.max_net_vol_btc > 0:
						if float(data['nvol_btc']) < self.max_net_vol_btc:
							nvolbtc_notify = True
						else:
							nvolbtc_notify = False
					else:
						nvolbtc_notify = True
					
					if ping_notify and nvolbtc_notify:
						if self.max_ping != 0 or self.max_net_vol_btc !=0:
							self.signals.update.emit(data)

		

		
		#self.pings 
		#self.signals.update.emit(r)


## test
#def main():
#
#	bve = binance_volume_monitor()
#	bve.update()
#	pass

#if __name__ == '__main__':
#	main()