# Bismuth Tools
# version 1.02
# Copyright Maccaspacca 2017
# Copyright Hclivess 2016 to 2017
# Author Maccaspacca

import wx
import wx.html
import wx.lib.agw.hyperlink as hl
import sqlite3
import time
import re
from datetime import datetime
import os
import sys
from threading import Thread
import ticons
import hashlib
import base64
import pyqrcode
import logging

import  wx.lib.newevent

from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA

logging.basicConfig(level=logging.INFO, 
                    filename='tools.log', # log to this file
                    format='%(asctime)s %(message)s') # include timestamp

logging.info("logging initiated")

(UpdateStatusEvent, EVT_UPDATE_STATUSBAR) = wx.lib.newevent.NewEvent()

def updatestatus(newstatus,newplace):
	evt = UpdateStatusEvent(msg = newstatus, st_id = int(newplace))
	wx.PostEvent(statusbar,evt)
					
a_txt = "<table>"
a_txt = a_txt + "<tr><td align='right' bgcolor='#DAF7A6'><b>Version:</b></td><td bgcolor='#D0F7C3'>1.02</td></tr>"
a_txt = a_txt + "<tr><td align='right' bgcolor='#DAF7A6'><b>Copyright:</b></td><td bgcolor='#D0F7C3'>Maccaspacca 2017, Hclivess 2016 to 2017</td></tr>"
a_txt = a_txt + "<tr><td align='right' bgcolor='#DAF7A6'><b>Date Published:</b></td><td bgcolor='#D0F7C3'>7th May 2017</td></tr>"
a_txt = a_txt + "<tr><td align='right' bgcolor='#DAF7A6'><b>License:</b></td><td bgcolor='#D0F7C3'>GPL-3.0</td></tr>"
a_txt = a_txt + "</table>"

w_txt = "<table>"
w_txt = w_txt + "<tr><td bgcolor='#D0F7C3'>1. Click on a transaction in the list to get more information.</td></tr>"
w_txt = w_txt + "<tr><td bgcolor='#D0F7C3'>2. Information refreshes every 5 minutes.</td></tr>"
w_txt = w_txt + "</table>"

l_txt = "<table>"
l_txt = l_txt + "<tr><td bgcolor='#D0F7C3'>1. Input a block number, wallet address or hash into the text box.</td></tr>"
l_txt = l_txt + "<tr><td bgcolor='#D0F7C3'>2. Press enter or click submit.</td></tr>"
l_txt = l_txt + "<tr><td bgcolor='#D0F7C3'>3. Click on a transaction to see more detail.</td></tr>"
l_txt = l_txt + "<tr><td bgcolor='#D0F7C3'>4. Latest block information refreshes every 5 minutes.</td></tr>"
l_txt = l_txt + "</table>"

m_txt = "<table>"
m_txt = m_txt + "<tr><td bgcolor='#D0F7C3'>1. Click on the Miner Query tab to view a list of miners.</td></tr>"
m_txt = m_txt + "<tr><td bgcolor='#D0F7C3'>2. Miners are ordered by blocks found in last 10000 blocks.</td></tr>"
m_txt = m_txt + "<tr><td bgcolor='#D0F7C3'>3. Click on a miner to see more detail.</td></tr>"
m_txt = m_txt + "<tr><td bgcolor='#D0F7C3'>4. The miner data will update every 10 minutes.</td></tr>"
m_txt = m_txt + "<tr><td bgcolor='#D0F7C3'>5. On first run a miner database will be created</td></tr>"
m_txt = m_txt + "<tr><td bgcolor='#D0F7C3'>6. Click 'Refresh List' after an update or wait 10 mins for auto-refresh</td></tr>"
m_txt = m_txt + "</table>"

# //////////////////////////////////////////////////////////
# Miner database stuff
# //////////////////////////////////////////////////////////

def i_am_first(my_first,the_address):

	conn = sqlite3.connect(os.path.expanduser('~/Bismuth/static/ledger.db'))
	conn.text_factory = str
	c = conn.cursor()
	c.execute("SELECT MIN(block_height) FROM transactions WHERE openfield = ?;",(my_first,))
	test_min = c.fetchone()[0]
	c.execute("SELECT * FROM transactions WHERE block_height = ? and openfield = ?;",(test_min,my_first))
	test_me = c.fetchone()[2]
	c.close()
	
	#print str(the_address) + " | " + str(test_me)
	
	if the_address == test_me:
		return True
	else:
		return False

def checkmyname(myaddress):
	conn = sqlite3.connect(os.path.expanduser('~/Bismuth/static/ledger.db'))
	conn.text_factory = str
	c = conn.cursor()
	c.execute("SELECT * FROM transactions WHERE address = ? AND recipient = ? AND amount > ? ORDER BY block_height ASC;",(myaddress,myaddress,"1"))
	namelist = c.fetchall()
	c.close()
	
	goodname = ""

	for x in namelist:
		tempfield = str(x[11])
		newfield = ""
		
		if tempfield == "reward" or "":
			goodname = ""
		else:
			try:
				newfield = base64.b64decode(tempfield)
			except:
				pass
			if "Minername=" in newfield:
				if i_am_first(base64.b64encode(newfield),x[2]):
					duff = newfield.split("=")
					goodname = str(duff[1])
				else:
					goodname = ""
			if "Minername=" in tempfield:
				if i_am_first(tempfield,x[2]):
					duff = tempfield.split("=")
					goodname = str(duff[1])
				else:
					goodname = ""

	logging.info("Checkname result: Address {} = {}".format(str(myaddress),goodname))
	
	return goodname

def latest():

	conn = sqlite3.connect(os.path.expanduser('~/Bismuth/static/ledger.db'))
	conn.text_factory = str
	c = conn.cursor()
	c.execute("SELECT * FROM transactions WHERE reward != ? ORDER BY block_height DESC LIMIT 1;", ('0',)) #or it takes the first
	result = c.fetchall()
	c.close()
	db_timestamp_last = result[0][1]
	db_block_height = result[0][0]
	time_now = str(time.time())
	last_block_ago = float(time_now) - float(db_timestamp_last)
	
	global hyper_limit
	
	conn = sqlite3.connect(os.path.expanduser('~/Bismuth/static/ledger.db'))
	conn.text_factory = str
	c = conn.cursor()
	c.execute("SELECT * FROM transactions WHERE address = ? OR address = ? ORDER BY block_height DESC LIMIT 1;", ('Hypoblock','Hyperblock')) #or it takes the first
	hyper_result = c.fetchall()
	
	c.close()
	
	if not hyper_result:
		hyper_limit = 1
	else:
		hyper_limit = (hyper_result[0][0]) + 1
	
	logging.info("Latest block queried: {}".format(str(db_block_height)))
	logging.info("Hyper_Limit is: {}".format(str(hyper_limit)))

	return db_block_height, last_block_ago

def zerocheck(zeroaddress):
	
	conn = sqlite3.connect(os.path.expanduser('~/Bismuth/static/ledger.db'))
	conn.text_factory = str
	c = conn.cursor()
	c.execute("SELECT count(*) FROM transactions WHERE address = ? AND (reward != 0);",(zeroaddress,))
	this_count = c.fetchone()[0]
	c.close()
	
	#logging.info("Checked for zero transactions: " + zeroaddress)
	
	if this_count > 0:
		return False
	else:
		return True

def getvars(myaddress):

	conn = sqlite3.connect(os.path.expanduser('~/Bismuth/static/ledger.db'))
	conn.text_factory = str
	c = conn.cursor()
	
	c.execute("SELECT sum(reward) FROM transactions WHERE address = ?;",(myaddress,))
	r_sum = c.fetchone()[0]
	c.execute("SELECT count(*) FROM transactions WHERE address = ? AND (reward != 0);",(myaddress,))
	b_count = c.fetchone()[0]
	c.execute("SELECT MAX(block_height) FROM transactions WHERE recipient = ?;",(myaddress,))
	b_max = c.fetchone()[0]
	c.execute("SELECT MIN(block_height) FROM transactions WHERE block_height BETWEEN ? and ? AND recipient = ?;",(hyper_limit,b_max,myaddress))
	b_min = c.fetchone()[0]
	c.execute("SELECT timestamp FROM transactions WHERE block_height = ?;",(str(b_max),))
	t_max = c.fetchone()[0]
	c.execute("SELECT timestamp FROM transactions WHERE block_height = ?;",(str(b_min),))
	t_min = c.fetchone()[0]	

	temp_for = (float(t_max) - float(t_min))
	myadjust = 0
	if temp_for == 0:
		miner_for = 0
		b_perday = 0
		c_power = 0.01
	else:
		conn = sqlite3.connect(os.path.expanduser('~/Bismuth/static/ledger.db'))
		c = conn.cursor()
		c.execute("SELECT timestamp FROM transactions WHERE block_height BETWEEN ? and ? AND recipient = ? AND (reward != 0) ORDER BY block_height ASC;", (hyper_limit,b_max,myaddress))
		timeall = c.fetchall()
		c.close()
		
		test_for = float(t_min)

		for x in timeall:

			
			do_test = float(x[0]) - test_for

			if do_test > 86400:
				myadjust = myadjust + do_test

			test_for = float(x[0])
			
		miner_for = (temp_for - myadjust)
		miner_for = miner_for/86400
		
		if miner_for == 0:
			miner_for = 1		
		
		b_perday = b_count/miner_for
		c_power = miner_for * 0.432
		c_power = format(c_power, '.2f')

	miner_for = format(miner_for, '.2f')
	b_perday = format(b_perday, '.0f')
	
	t_min = str(time.strftime("at %H:%M:%S on %d/%m/%Y", time.localtime(float(t_min))))
	t_max = str(time.strftime("at %H:%M:%S on %d/%m/%Y", time.localtime(float(t_max))))
	
#http://energyusecalculator.com/electricity_computer.htm
#Cost using average 180W power use @ $0.10 per kWh = $0.432
#c_power = miner_for * 0.432

	return t_max, t_min, b_count, miner_for, b_perday, r_sum, c_power

def rebuildme():

	# tidy up
	
	if os.path.isfile('tempminers.db'):
		os.remove('tempminers.db')
	
	logging.info("Miner DB: Rebuild")
	# create empty miners database
	minerlist = sqlite3.connect('tempminers.db')
	minerlist.text_factory = str
	m = minerlist.cursor()
	m.execute("CREATE TABLE IF NOT EXISTS minerlist (address, blatest, bfirst, blockcount, minerfor, bday, treward, tenergy, mname)")
	minerlist.commit()
	minerlist.close()
	logging.info("Miner DB: Creating or updating miners database")
	# create empty minerlist
		
	logging.info("Miner DB: Getting up to date list of miners.....")
		
	updatestatus("Getting up to date list of miners.....", 2)
	time.sleep(2)

	# Get mining addresses from ledgerdb
	conn = sqlite3.connect(os.path.expanduser('~/Bismuth/static/ledger.db'))
	conn.text_factory = str
	c = conn.cursor()
	c.execute("SELECT distinct recipient FROM transactions WHERE block_height > ? AND reward != 0;",(hyper_limit,))
	miner_list_raw = c.fetchall()
	c.close()

	temp_result = []
	
	# Validate miner address and get info from ledgerdb

	updatestatus("Getting new data.....please wait this may take some time!", 2)
	
	for x in miner_list_raw:
		
		temp_miner = str(x[0])
		if len(temp_miner) == 56:
			if not zerocheck(temp_miner):
				m_info = getvars(temp_miner)
				m_name = checkmyname(temp_miner)
				temp_result.append((temp_miner, m_info[0], m_info[1], m_info[2], m_info[3], m_info[4], m_info[5], m_info[6], m_name))

	updatestatus("Inserting information into database.....", 2)
	time.sleep(2)
			
	conn = sqlite3.connect('tempminers.db')
	conn.text_factory = str
	c = conn.cursor()

	for y in temp_result:

		c.execute('INSERT INTO minerlist VALUES (?,?,?,?,?,?,?,?,?)', (y[0],y[1],y[2],y[3],y[4],y[5],y[6],y[7],y[8]))

	conn.commit()
	c.close()
	conn.close()

	if os.path.isfile('miners.db'):
		os.remove('miners.db')
	os.rename('tempminers.db','miners.db')
	updatestatus("Done !", 2)
	time.sleep(2)
	return True

def buildminerdb():
	time.sleep(5)
	bobble = rebuildme()
	#bobble = True

	while bobble:
		updatestatus("Waiting for 10 minutes.......", 2)
		time.sleep(600)
		bobble = rebuildme()

def checkstart():

	if not os.path.exists('miners.db'):
		# create empty miners database
		logging.info("Miner DB: Create New as none exisits")
		minerlist = sqlite3.connect('miners.db')
		minerlist.text_factory = str
		m = minerlist.cursor()
		m.execute(
			"CREATE TABLE IF NOT EXISTS minerlist (address, blatest, bfirst, blockcount, minerfor, bday, treward, tenergy, mname)")
		minerlist.commit()
		minerlist.close()
		# create empty minerlist

checkstart()
	
#////////////////////////////////////////////////////////////

def refresh(testAddress):
	conn = sqlite3.connect(os.path.expanduser('~/Bismuth/static/ledger.db'))
	conn.text_factory = str
	c = conn.cursor()
	c.execute("SELECT sum(amount) FROM transactions WHERE recipient = ?;",(testAddress,))
	credit = c.fetchone()[0]
	c.execute("SELECT sum(amount) FROM transactions WHERE address = ?;",(testAddress,))
	debit = c.fetchone()[0]
	c.execute("SELECT sum(fee) FROM transactions WHERE address = ?;",(testAddress,))
	fees = c.fetchone()[0]
	c.execute("SELECT sum(reward) FROM transactions WHERE address = ?;",(testAddress,))
	rewards = c.fetchone()[0]
	c.execute("SELECT MAX(block_height) FROM transactions")
	bl_height = c.fetchone()[0]
	if debit == None:
		debit = 0
	if fees == None:
		fees = 0
	if rewards == None:
		rewards = 0
	if credit == None:
		credit = 0
	balance = credit - debit - fees + rewards

	c.close()

	return str(credit),str(debit),str(rewards),str(fees),str(balance)

def test(testString):

	if (re.search('[abcdef]',testString)):
		if len(testString) == 56:
			test_result = 1
		else:
			test_result = 3
	elif testString.isdigit() == True:
		test_result = 2
	else:
		test_result = 3
		
	return test_result	

def miners():

	logging.info("Miner DB: Get mining addresses from miners.db")
	conn = sqlite3.connect('miners.db')
	conn.text_factory = str
	c = conn.cursor()
	c.execute("SELECT * FROM minerlist ORDER BY blockcount DESC;")
	miner_result = c.fetchall()
	c.close()

	return miner_result

def bgetvars(myaddress):

	conn = sqlite3.connect('miners.db')
	conn.text_factory = str
	c = conn.cursor()
	c.execute("SELECT * FROM minerlist WHERE address = ?;",(myaddress,))
	miner_details = c.fetchone()
	c.close()
	m_info = miner_details
	global addressis
	addressis = "<table>"
	addressis = addressis + "<tr><td align='right' bgcolor='#DAF7A6'><b>Address:</b></td><td bgcolor='#D0F7C3'>" + str(m_info[0]) + "</td></tr>"
	addressis = addressis + "<tr><td align='right' bgcolor='#DAF7A6'><b>Latest Block Found:</b></td><td bgcolor='#D0F7C3'>" + str(m_info[1]) + "</td></tr>"
	addressis = addressis + "<tr><td align='right' bgcolor='#DAF7A6'><b>First Block Found:</b></td><td bgcolor='#D0F7C3'>" + str(m_info[2]) + "</td></tr>"
	addressis = addressis + "<tr><td align='right' bgcolor='#DAF7A6'><b>Total Blocks Found:</b></td><td bgcolor='#D0F7C3'>" + str(m_info[3]) + "</td></tr>"
	addressis = addressis + "<tr><td align='right' bgcolor='#DAF7A6'><b>Time Spent Mining:</b></td><td bgcolor='#D0F7C3'>" + str(m_info[4]) + " Days (Adjusted Estimate)</td></tr>"
	addressis = addressis + "<tr><td align='right' bgcolor='#DAF7A6'><b>Blocks Per Day:</b></td><td bgcolor='#D0F7C3'>" + str(m_info[5]) + " (Estimate)</td></tr>"
	addressis = addressis + "<tr><td align='right' bgcolor='#DAF7A6'><b>Total Rewards:</b></td><td bgcolor='#D0F7C3'>" + str(m_info[6]) + "</td></tr>"
	addressis = addressis + "<tr><td align='right' bgcolor='#DAF7A6'><b>Total Energy Cost:</b></td><td bgcolor='#D0F7C3'>$" + str(m_info[7]) + " (Estimate | 180W PC usage | USD)</td></tr>"
	addressis = addressis + "</table>"
	
	return True

def tgetvars(myblock,myamount,mytitle):

	conn = sqlite3.connect(os.path.expanduser('~/Bismuth/static/ledger.db'))
	conn.text_factory = str
	c = conn.cursor()
	c.execute("SELECT * FROM transactions WHERE block_height = ? AND amount = ?;", (myblock, myamount))
	trans_details = c.fetchone()
	c.close()
	m_info = trans_details
	if str(m_info[10]) == "1":
		keepme = "Yes"
	else:
		keepme = "No"
	global transis
	transis = []
	tempsis = "<table>"
	tempsis = tempsis + "<tr><td align='right' bgcolor='#DAF7A6'><b>Block:</b></td><td bgcolor='#D0F7C3'>" + str(m_info[0]) + "</td></tr>"
	tempsis = tempsis + "<tr><td align='right' bgcolor='#DAF7A6'><b>Timestamp:</b></td><td bgcolor='#D0F7C3'>" + str(time.strftime("%d/%m/%Y at %H:%M:%S", time.localtime(float(m_info[1])))) + "</td></tr>"
	tempsis = tempsis + "<tr><td align='right' bgcolor='#DAF7A6'><b>From:</b></td><td bgcolor='#D0F7C3'>" + str(m_info[2]) + "</td></tr>"
	tempsis = tempsis + "<tr><td align='right' bgcolor='#DAF7A6'><b>To:</b></td><td bgcolor='#D0F7C3'>" + str(m_info[3]) + "</td></tr>"
	tempsis = tempsis + "<tr><td align='right' bgcolor='#DAF7A6'><b>Amount:</b></td><td bgcolor='#D0F7C3'>" + str(m_info[4]) + "</td></tr>"
	tempsis = tempsis + "<tr><td align='right' bgcolor='#DAF7A6'><b>Block Hash:</b></td><td bgcolor='#D0F7C3'>" + str(m_info[7]) + "</td></tr>"
	tempsis = tempsis + "<tr><td align='right' bgcolor='#DAF7A6'><b>Fee:</b></td><td bgcolor='#D0F7C3'>" + str(m_info[8]) + "</td></tr>"
	tempsis = tempsis + "<tr><td align='right' bgcolor='#DAF7A6'><b>Reward:</b></td><td bgcolor='#D0F7C3'>" + str(m_info[9]) + "</td></tr>"
	tempsis = tempsis + "<tr><td align='right' bgcolor='#DAF7A6'><b>Keep:</b></td><td bgcolor='#D0F7C3'>" + keepme + "</td></tr>"
	tempsis = tempsis + "</table>"
	
	transis.append(tempsis)
	transis.append(mytitle)
	
	return True

def wgetrans(thisaddress):

	# transaction table
	# data
	#datasheet = ["Time", "From", "To", "Amount", "Block"]

	datasheet = []

	rows_total = 20

	mempool = sqlite3.connect('../mempool.db')
	mempool.text_factory = str
	m = mempool.cursor()

	conn = sqlite3.connect(os.path.expanduser('~/Bismuth/static/ledger.db'))
	conn.text_factory = str
	c = conn.cursor()

	for row in m.execute("SELECT * FROM transactions WHERE address = ? OR recipient = ? ORDER BY timestamp DESC LIMIT 19;",(thisaddress,)+(thisaddress,)):
		rows_total = rows_total - 1

		datasheet.append("unconfirmed")
		mempool_address = row[1]
		datasheet.append(mempool_address)
		mempool_recipient = row[2]
		datasheet.append(mempool_recipient)
		mempool_amount = row[3]
		datasheet.append(mempool_amount)
		mempool_block = "X"
		datasheet.append(mempool_block)		
	mempool.close()

	for row in c.execute("SELECT * FROM transactions WHERE address = ? OR recipient = ? ORDER BY block_height DESC LIMIT ?;",(thisaddress,)+(thisaddress,)+(rows_total,)):
		db_timestamp = row[1]
		datasheet.append(datetime.fromtimestamp(float(db_timestamp)).strftime('%Y-%m-%d %H:%M:%S'))
		db_address = row[2]
		datasheet.append(db_address)
		db_recipient = row[3]
		datasheet.append(db_recipient)
		db_amount = row[4]
		datasheet.append(db_amount)
		db_block = row[0]
		datasheet.append(db_block)
	conn.close()
	# data

	if len(datasheet) == 0:
		table_limit = 0
		#datasheet = []
	elif len(datasheet) < 20 * 5:
		table_limit = len(datasheet) / 5
	else:
		table_limit = 20

	return datasheet, table_limit

#////////////////////////////////////////////////////////////////////////
# Classes
#////////////////////////////////////////////////////////////////////////

class HtmlWindow(wx.html.HtmlWindow):
    def __init__(self, parent, id, size=(1,1)):
        wx.html.HtmlWindow.__init__(self,parent, id, size=size)
        if "gtk2" in wx.PlatformInfo:
            self.SetStandardFonts()
      
class AboutBoxM(wx.Dialog):
	def __init__(self):
		wx.Dialog.__init__(self, None, -1, "Miner Query Tool | Miner Details",
			style=wx.DEFAULT_DIALOG_STYLE|wx.THICK_FRAME|wx.RESIZE_BORDER|
				wx.TAB_TRAVERSAL)
		hwin = HtmlWindow(self, -1, size=(560,260))
		aboutText = '<p style="color:#08750A";>{}</p>'.format(addressis)
		hwin.SetPage(aboutText)
		btn = hwin.FindWindowById(wx.ID_OK)
		irep = hwin.GetInternalRepresentation()
		hwin.SetSize((irep.GetWidth()+40, irep.GetHeight()+10))
		self.SetClientSize(hwin.GetSize())
		self.CentreOnParent(wx.BOTH)
		self.SetFocus()

class AboutBoxT(wx.Dialog):
	def __init__(self):
		wx.Dialog.__init__(self, None, -1, transis[1],
			style=wx.DEFAULT_DIALOG_STYLE|wx.THICK_FRAME|wx.RESIZE_BORDER|
				wx.TAB_TRAVERSAL)
		hwin = HtmlWindow(self, -1, size=(560,260))
		aboutText = '<p style="color:#08750A";>{}</p>'.format(transis[0])
		hwin.SetPage(aboutText)
		btn = hwin.FindWindowById(wx.ID_OK)
		irep = hwin.GetInternalRepresentation()
		hwin.SetSize((irep.GetWidth()+40, irep.GetHeight()+10))
		self.SetClientSize(hwin.GetSize())
		self.CentreOnParent(wx.BOTH)
		self.SetFocus()

class AboutBox(wx.Dialog):
	def __init__(self):
		wx.Dialog.__init__(self, None, -1, thistitle,
			style=wx.DEFAULT_DIALOG_STYLE|wx.THICK_FRAME|wx.RESIZE_BORDER|
				wx.TAB_TRAVERSAL)
		hwin = HtmlWindow(self, -1, size=(420,300))
		if thisid == 101:
			aboutText = '<p style="color:#08750A">{}</p>'.format(w_txt)
		elif thisid == 102:
			aboutText = '<p style="color:#08750A">{}</p>'.format(a_txt)
		elif thisid == 103:
			aboutText = '<p style="color:#08750A">{}</p>'.format(l_txt)
		elif thisid == 104:
			aboutText = '<p style="color:#08750A">{}</p>'.format(m_txt)
		hwin.SetPage(aboutText)
		irep = hwin.GetInternalRepresentation()
		hwin.SetSize((irep.GetWidth()+10, irep.GetHeight()+10))
		self.SetClientSize(hwin.GetSize())
		self.CentreOnParent(wx.BOTH)
		self.SetFocus()
#---------------------------------------------------------------------------

class PageOne(wx.Window):
    def __init__(self, parent):
		wx.Window.__init__(self, parent, -1, style = wx.NO_BORDER)
		
		box1 = wx.BoxSizer(wx.VERTICAL)
		
		topbox1 = wx.BoxSizer(wx.HORIZONTAL) # logo
		
		t = wx.StaticText(self, -1, "Welcome to Bismuth Tools")
		self.SetBackgroundColour("#FFFFFF")
		t.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))
		t.SetForegroundColour("#444995")
		t.SetSize(t.GetBestSize())
		topbox1.Add(t, 0, wx.ALL|wx.CENTER, 10)
				
		logo = ticons.bismuthlogo.GetBitmap()
		self.image1 = wx.StaticBitmap(self, -1, logo)
		topbox1.Add(self.image1, 0, wx.ALL|wx.RIGHT, 10)
		
		box1.Add(topbox1, 0, wx.ALL|wx.CENTER, 10)
		
		i = wx.StaticText(self, -1, "Please choose your tool from the tabs above")
		i.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL))
		i.SetForegroundColour("#444995")
		i.SetSize(i.GetBestSize())
		box1.Add(i, 0, wx.ALL|wx.CENTER, 5)

		ins1 = wx.StaticText(self, -1, "Use the window menu above for help")
		ins1.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL))
		ins1.SetForegroundColour("#444995")
		ins1.SetSize(ins1.GetBestSize())
		box1.Add(ins1, 0, wx.ALL|wx.CENTER, 5)
	
		hyper2 = wx.StaticText(self, -1, "Query information is limited to blocks after the latest hyperblock in the ledger")
		hyper2.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL))
		hyper2.SetForegroundColour("#444995")
		hyper2.SetSize(hyper2.GetBestSize())
		box1.Add(hyper2, 0, wx.ALL|wx.CENTER, 5)

		self.SetSizer(box1)
		self.Layout()


class PageTwo(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)
		
		self.timer1 = wx.Timer(self)
		self.Bind(wx.EVT_TIMER, self.update, self.timer1)
				
		l_text1 = wx.StaticText(self, -1, "Bismuth Ledger Query Tool")
		l_text1.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))
		l_text1.SetSize(l_text1.GetBestSize())
		
		l_text2 = wx.StaticText(self, -1, "Get a List of Transactions")
		l_text2.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL))
		l_text2.SetSize(l_text2.GetBestSize())
		
		hbox2 = wx.BoxSizer(wx.HORIZONTAL)

		l_text3 = wx.StaticText(self, -1, "Enter a Block Number, Hash or Address:")
		l_text3.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD))
		l_text3.SetSize(l_text3.GetBestSize())

		self.lt1 = wx.TextCtrl(self, size=(350, -1), style=wx.TE_PROCESS_ENTER)
		self.lt1.Bind(wx.EVT_TEXT_ENTER, self.OnSubmit)
		self.lt1.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))
		
		hbox2.Add(l_text3, 0, wx.ALL|wx.RIGHT, 2)
		hbox2.Add(self.lt1, 0, wx.ALL|wx.LEFT, 2)
		
		hbox3 = wx.BoxSizer(wx.HORIZONTAL)

		l_text4 = wx.StaticText(self, -1, "             Click Submit to List Transactions")
		l_text4.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD))
		l_text4.SetSize(l_text4.GetBestSize())

		l_submit = wx.Button(self, wx.ID_APPLY, "Submit Query")
		l_submit.Bind(wx.EVT_BUTTON, self.OnSubmit)
		
		hbox3.Add(l_text4, 0, wx.ALL|wx.RIGHT, 2)
		hbox3.Add(l_submit, 0, wx.ALL|wx.LEFT, 2)
		
		self.mylatest = latest()
		
		self.p2text = "The latest block: {} was found {} seconds ago\n".format(str(self.mylatest[0]),str(int(self.mylatest[1])))
		#self.p2text = self.p2text + "The latest Hyperblock was at block number: {}\n".format(str(hyper_limit -1))
		self.p2text = self.p2text + "Queries for blocks before {} will not be found\n".format(str(hyper_limit))
		
		self.l_text5 = wx.StaticText(self, -1, self.p2text)
		self.l_text5.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))
		self.l_text5.SetForegroundColour("#08750A")		
		self.l_text5.SetSize(self.l_text5.GetBestSize())
		
		hbox4 = wx.BoxSizer(wx.HORIZONTAL)
		
		self.l_text6 = wx.StaticText(self, -1, "")
		self.l_text6.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))
		self.l_text6.SetForegroundColour("#08750A")		
		self.l_text6.SetSize(self.l_text6.GetBestSize())
		
		self.l_text7 = hl.HyperLinkCtrl(self, -1, "")
		self.l_text7.Bind(hl.EVT_HYPERLINK_LEFT, self.OnLeft)
		self.l_text7.AutoBrowse(False)
		self.l_text7.SetSize(self.l_text7.GetBestSize())
		
		self.l_text8 = hl.HyperLinkCtrl(self, -1, "")
		self.l_text8.Bind(hl.EVT_HYPERLINK_LEFT, self.OnRight)
		self.l_text8.AutoBrowse(False)
		self.l_text8.SetSize(self.l_text8.GetBestSize())

		hbox4.Add(self.l_text7, 0, wx.ALL|wx.LEFT, 2)
		hbox4.Add(self.l_text6, 0, wx.ALL|wx.RIGHT, 2)
		hbox4.Add(self.l_text8, 0, wx.ALL|wx.CENTER, 2)		

		self.index = 0

		self.list_ctrl = wx.ListCtrl(self, size=(-1,425),
						 style=wx.LC_REPORT
						 |wx.BORDER_SUNKEN
						 )
		self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnAbout, self.list_ctrl)
		self.list_ctrl.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD))
		self.list_ctrl.InsertColumn(0, 'Block Number')
		self.list_ctrl.InsertColumn(1, 'To')
		self.list_ctrl.InsertColumn(2, 'Amount')
		self.list_ctrl.InsertColumn(3, 'Reward')
		
		self.list_ctrl.SetColumnWidth(0, -2)
		self.list_ctrl.SetColumnWidth(1, -1)
		self.list_ctrl.SetColumnWidth(2, -2)
		self.list_ctrl.SetColumnWidth(3, -2)		
		
		self.box2 = wx.BoxSizer(wx.VERTICAL)
		self.box2.Add(l_text1, 0, wx.ALL|wx.CENTER, 2)
		self.box2.Add(l_text2, 0, wx.ALL|wx.CENTER, 2)
		self.box2.Add(hbox2, 0, wx.ALL|wx.LEFT, 2)
		self.box2.Add(hbox3, 0, wx.ALL|wx.LEFT, 2)
		self.box2.Add(self.l_text5, 0, wx.ALL|wx.CENTER, 2)
		self.box2.Add(hbox4, 0, wx.ALL|wx.CENTER, 2)
		self.box2.Add(self.list_ctrl, 0, wx.ALL|wx.EXPAND, 2)
		
		self.SetSizer(self.box2)
		
		self.timer1.Start(300 * 1000)

	def OnSubmit(self, event):

		myblock = str(self.lt1.GetValue())
		logging.info("Ledger: Query for: {}".format(str(myblock)))
		
		if not myblock: #Nonetype handling - simply replace with "0"
			myblock = "0"
		if not myblock.isalnum():
			myblock = "0"
			#print "has dodgy characters but now fixed"
		my_type = test(myblock)
		
		if my_type == 3:
			myblock = "0"
			my_type = 2

		if my_type == 1:
			
			myxtions = refresh(myblock)
			
			if float(myxtions[4]) > 0:
			
				self.l_text6.SetForegroundColour("#08750A")
				extext = "Success !! Transactions found for address: {}\n".format(myblock)
				extext = extext + "Credits: {} | Debits: {} | Rewards: {} |".format(myxtions[0],myxtions[1],myxtions[2])
				extext = extext + " Fees: {} | BALANCE: {}".format(myxtions[3],myxtions[4])
				self.cleantxt()
				
				conn = sqlite3.connect(os.path.expanduser('~/Bismuth/static/ledger.db'))
				c = conn.cursor()
				c.execute("SELECT * FROM transactions WHERE address = ? OR recipient = ? ORDER BY block_height DESC;", (str(myblock),str(myblock)))

				all = c.fetchall()
				
				c.close()
			else:
				
				conn = sqlite3.connect(os.path.expanduser('~/Bismuth/static/ledger.db'))
				c = conn.cursor()
				c.execute("SELECT * FROM transactions WHERE block_hash = ?;", (str(myblock),))

				all = c.fetchall()
				
				c.close()
				
				if not all:
					self.l_text6.SetForegroundColour(wx.RED)
					self.cleantxt()
					extext = "Error !!! Nothing found for the address or block hash you entered"
				else:
					self.l_text6.SetForegroundColour("#08750A")
					self.cleantxt()
					extext = "Success !! Transactions found for block hash: {}".format(myblock)	

		if my_type == 2:

			if myblock == "0":
				self.l_text6.SetForegroundColour(wx.RED)
				self.cleantxt()
				extext = "Error !!! Block, address or hash not found. Maybe you entered bad data or nothing at all?"
				all = []
			
			if int(myblock) < hyper_limit:
				self.l_text6.SetForegroundColour(wx.RED)
				self.cleantxt()
				extext = "Error !!! Block, address or hash not found. Maybe you entered bad data or nothing at all?"
				all = []
			
			else:
					
				conn = sqlite3.connect(os.path.expanduser('~/Bismuth/static/ledger.db'))
				c = conn.cursor()
				c.execute("SELECT * FROM transactions WHERE block_height = ?;", (myblock,))

				all = c.fetchall()
				#print all
				
				c.close()
				
			if not all:
				self.l_text6.SetForegroundColour(wx.RED)
				self.cleantxt()
				extext = "Error !!! Block, address or hash not found. Maybe you entered bad data or nothing at all?"
			else:
				self.l_text6.SetForegroundColour("#08750A")
				self.cleantxt()
				extext = "Transactions found for block {}".format(myblock)
				
				if int(myblock) > (hyper_limit):
					self.l_text7.SetLabel("<< Previous ")
					self.l_text7.SetToolTip(wx.ToolTip("Go to block {}".format(str(int(myblock) - 1))))
				
				if (int(myblock) + 1) < (self.mylatest[0] + 1):
					self.l_text8.SetLabel("Next >>")
					self.l_text8.SetToolTip(wx.ToolTip("Go to block {}".format(str(int(myblock) + 1))))
				
		
		self.l_text6.SetLabel(extext)
		self.box2.Layout()
		
		index = 0
		
		self.list_ctrl.DeleteAllItems()
		
		for data in all:
			if index % 2 == 0:
				color_cell = "#E8E8E8"
			else:
				color_cell = ""#FFFFFF""
			self.list_ctrl.InsertStringItem(index, str(data[0]))
			self.list_ctrl.SetStringItem(index, 1, str(data[3]))
			self.list_ctrl.SetStringItem(index, 2, str(data[4]))
			self.list_ctrl.SetStringItem(index, 3, str(data[9]))
			self.list_ctrl.SetItemBackgroundColour(item=index, col=color_cell)
			self.list_ctrl.SetItemData(index, index)
			index += 1
		
		self.list_ctrl.SetColumnWidth(0, -2)
		self.list_ctrl.SetColumnWidth(1, -1)
		self.list_ctrl.SetColumnWidth(2, -2)
		self.list_ctrl.SetColumnWidth(3, -2)

	
	def OnAbout(self, event):
		l_event = event.GetIndex()
		l_item1 = self.list_ctrl.GetItem(l_event, 0)
		l_item2 = self.list_ctrl.GetItem(l_event, 2)
		getblock = l_item1.GetText()
		getamount = l_item2.GetText()
		gettitle = "Ledger Query Tool | Transaction Details"
		logging.info("Ledger: Transaction details request")

		if tgetvars(getblock,getamount,gettitle):
			dlg = AboutBoxT()
			dlg.ShowModal()
			dlg.Destroy()

	def update(self, event):
		self.timer1.Stop()
		self.mylatest = latest()
		self.p2text = "The latest block: {} was found {} seconds ago".format(str(self.mylatest[0]),str(int(self.mylatest[1])))
		self.l_text5.SetLabel(self.p2text)
		logging.info("Ledger: Latest block refresh")
		self.timer1.Start(300 * 1000)
		
	def OnLeft(self, event):
		currblock = str(self.lt1.GetValue())
		if currblock.isdigit():
			currblock = int(currblock)
			prevblock = currblock - 1
			if prevblock == hyper_limit or prevblock > hyper_limit:
				self.lt1.SetValue(str(prevblock))
				self.l_text7.SetLabel("<< Previous ")
				self.OnSubmit(wx.EVT_BUTTON)
			else:
				self.lt1.SetValue(str(hyper_limit))
				self.l_text7.SetLabel("")
				self.l_text7.SetToolTip(wx.ToolTip(""))
		else:
			pass

	def OnRight(self, event):
		currblock = str(self.lt1.GetValue())
		if currblock.isdigit():
			currblock = int(currblock)
			nextblock = currblock + 1
			if nextblock < (self.mylatest[0] + 1):
				self.lt1.SetValue(str(nextblock))
				self.l_text8.SetLabel("Next >>")
				self.OnSubmit(wx.EVT_BUTTON)
			else:
				self.lt1.SetValue(str(self.mylatest[0]))
				self.l_text8.SetLabel("")
				self.l_text8.SetToolTip(wx.ToolTip(""))
		else:
			pass

	def cleantxt(self):
		self.l_text7.SetLabel("")
		self.l_text7.SetToolTip(wx.ToolTip(""))
		self.l_text8.SetLabel("")
		self.l_text8.SetToolTip(wx.ToolTip(""))
		
	

class PageThree(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)

		self.timer2 = wx.Timer(self)
		self.Bind(wx.EVT_TIMER, self.OnRefresh, self.timer2)
		
		m_text1 = wx.StaticText(self, -1, "Bismuth Miner Query Tool")
		m_text1.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))
		m_text1.SetSize(m_text1.GetBestSize())

		m_text2 = wx.StaticText(self, -1, "Hint: Click on an address to see more detail")
		m_text2.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
		m_text2.SetSize(m_text2.GetBestSize())
		
		self.l_refresh = wx.Button(self, wx.ID_APPLY, "Refresh List")
		self.l_refresh.Bind(wx.EVT_BUTTON, self.OnRefresh)

		self.index = 0

		self.list_ctrl = wx.ListCtrl(self, size=(-1,425),
						 style=wx.LC_REPORT
						 |wx.BORDER_SUNKEN
						 )
		self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnAbout, self.list_ctrl)
		self.list_ctrl.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
		self.list_ctrl.InsertColumn(0, 'Haddress')
		self.list_ctrl.InsertColumn(1, 'Address')
		self.list_ctrl.InsertColumn(2, 'Blocks Found')
		self.list_ctrl.InsertColumn(3, 'Rank')
		
		items = miners()
		index = 0
		rank = 1
		
		for data in items:
			thisminer = str(data[0])
			thisname = ""
			if len(thisminer) == 56:
				if rank % 2 == 0:
					color_cell = ""#FFFFFF""
				else:
					color_cell = "#E8E8E8"
				self.list_ctrl.InsertStringItem(index, thisminer)
				if str(data[8]) == "":
					thisname = thisminer
				else:
					thisname = str(data[8])
				self.list_ctrl.SetStringItem(index, 1, thisname)
				self.list_ctrl.SetStringItem(index, 2, str(data[3]))
				self.list_ctrl.SetStringItem(index, 3, str(rank))
				self.list_ctrl.SetItemBackgroundColour(item=index, col=color_cell)
				self.list_ctrl.SetItemData(index, index)
				index += 1
				rank +=1
		
		self.list_ctrl.SetColumnWidth(0, 0)
		self.list_ctrl.SetColumnWidth(1, -1)
		self.list_ctrl.SetColumnWidth(2, -2)
		self.list_ctrl.SetColumnWidth(3, -2)
		
		box3 = wx.BoxSizer(wx.VERTICAL)
		box3.Add(m_text1, 0, wx.ALL|wx.CENTER, 5)
		box3.Add(m_text2, 0, wx.ALL|wx.CENTER, 5)
		box3.Add(self.l_refresh, 0, wx.ALL|wx.CENTER, 5)
		box3.Add(self.list_ctrl, 0, wx.ALL|wx.EXPAND, 5)

		self.SetSizer(box3)
	
		self.timer2.Start(600 * 1000)
		
	def MyMiners(self):
	
		items = miners()
		index = 0
		rank = 1
		
		for data in items:
			thisminer = str(data[0])
			if len(thisminer) == 56:
				if rank % 2 == 0:
					color_cell = ""#FFFFFF""
				else:
					color_cell = "#E8E8E8"
				self.list_ctrl.InsertStringItem(index, thisminer)
				if str(data[8]) == "":
					thisname = thisminer
				else:
					thisname = str(data[8])
				self.list_ctrl.SetStringItem(index, 1, thisname)
				self.list_ctrl.SetStringItem(index, 2, str(data[3]))
				self.list_ctrl.SetStringItem(index, 3, str(rank))
				self.list_ctrl.SetItemBackgroundColour(item=index, col=color_cell)
				self.list_ctrl.SetItemData(index, index)
				index += 1
				rank +=1
		self.list_ctrl.SetColumnWidth(0, 0)
		self.list_ctrl.SetColumnWidth(1, -1)
		self.list_ctrl.SetColumnWidth(2, -2)
		self.list_ctrl.SetColumnWidth(3, -2)
	
	def OnAbout(self, event):
		SelectedRow = event.GetText()
		getaddress = str(SelectedRow)
		if bgetvars(getaddress):
			dlg = AboutBoxM()
			dlg.ShowModal()
			dlg.Destroy()
	
	def OnRefresh(self, event):
		self.timer2.Stop()
		logging.info("Miners: Refresh requested")
		self.list_ctrl.DeleteAllItems()
		self.MyMiners()
		self.list_ctrl.Refresh()
		self.timer2.Start(600 * 1000)
		
class PageFour(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)
		
		self.timer = wx.Timer(self)
		self.Bind(wx.EVT_TIMER, self.update, self.timer)
	
		# import keys
		if not os.path.exists('../privkey_encrypted.der'):
			key = RSA.importKey(open('../privkey.der').read())
			private_key_readable = str(key.exportKey())
			#public_key = key.publickey()
			encrypted = 0
			unlocked = 1
			my_state = "Not encrypted (perhaps you left it unlocked or have never encrypted it?)"
			my_color = wx.RED
		else:
			encrypted = 1
			unlocked = 0
			my_state = "Encrypted and locked - yay!"
			my_color = wx.GREEN
		
		#public_key_readable = str(key.publickey().exportKey())
		public_key_readable = open('../pubkey.der').read()
		public_key_hashed = base64.b64encode(public_key_readable)
		self.myaddress = hashlib.sha224(public_key_readable).hexdigest()
		#private_key_readable = str(key.exportKey())
		
		address_qr = pyqrcode.create(self.myaddress)
		address_qr.png('address_qr.png')

		w_text1 = wx.StaticText(self, -1, "Bismuth Wallet Information")
		w_text1.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))
		w_text1.SetSize(w_text1.GetBestSize())
		
		w_text2 = wx.StaticText(self, -1, "Your address: " + self.myaddress)
		w_text2.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
		w_text2.SetSize(w_text2.GetBestSize())
		
		w_text3 = wx.StaticText(self, -1, my_state)
		w_text3.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))
		w_text3.SetForegroundColour(my_color)
		w_text3.SetSize(w_text3.GetBestSize())
		
		self.list_ctrl = wx.ListCtrl(self, size=(-1,-1),
						 style=wx.LC_REPORT|wx.LC_NO_HEADER
						 |wx.BORDER_NONE
						 )
		
		self.list_ctrl.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD))
		self.list_ctrl.InsertColumn(1, 'Information', wx.LIST_FORMAT_RIGHT)
		self.list_ctrl.InsertColumn(2, 'Value')

		wallet_info = refresh(self.myaddress)
		
		t_row = ["BALANCE:","Spent Total:","Received Total:","Fees Paid:","Rewards:"]
		t_data = [wallet_info[4],wallet_info[1],wallet_info[0],wallet_info[3],wallet_info[2]]
		
		self.index = 0
		
		for items in t_row:
			temp_row = t_row[self.index]
			temp_data = t_data[self.index]
			self.list_ctrl.InsertStringItem(self.index, temp_row)
			self.list_ctrl.SetStringItem(self.index, 1, temp_data)
			self.list_ctrl.SetItemData(self.index, self.index)
			self.index += 1

		#str(credit),str(debit),str(rewards),str(fees),str(balance),str(bl_height)

		self.list_ctrl.SetColumnWidth(0, -1)
		self.list_ctrl.SetColumnWidth(1, -1)
		
		myimage = wx.Image('address_qr.png', wx.BITMAP_TYPE_ANY)
		myimage = myimage.Scale(120,120)
		self.image4 = wx.StaticBitmap(self, wx.ID_ANY, wx.BitmapFromImage(myimage))

		w_text4 = wx.StaticText(self, -1, "Latest transactions:")
		w_text4.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD))
		w_text4.SetForegroundColour("#08750A")
		w_text4.SetSize(w_text4.GetBestSize())

		self.list_ctrl1 = wx.ListCtrl(self, size=(675,500),
						 style=wx.LC_REPORT
						 |wx.BORDER_SUNKEN
						 )
		self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnAbout, self.list_ctrl1)
		self.list_ctrl1.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))
		self.list_ctrl1.InsertColumn(0, 'Block', wx.LIST_FORMAT_RIGHT)
		self.list_ctrl1.InsertColumn(1, 'Date', wx.LIST_FORMAT_RIGHT)
		self.list_ctrl1.InsertColumn(2, 'To', wx.LIST_FORMAT_RIGHT)
		self.list_ctrl1.InsertColumn(3, 'From', wx.LIST_FORMAT_RIGHT)
		self.list_ctrl1.InsertColumn(4, 'Amount', wx.LIST_FORMAT_RIGHT)
		
		w_all = wgetrans(self.myaddress)
		
		if w_all[1] == 0:
			w_text4.SetLabel("No transactions, looks like a new address")
			w_text4.SetForegroundColour(wx.RED)
		else:
			w_trans = w_all[0]
			w_limit = w_all[1]
			
			#build table here
			
			k = 0
			mybacon = []
			for i in range(w_limit):
				if i % 2 == 0:
					color_cell = ""#FFFFFF""
				else:
					color_cell = "#E8E8E8"
				if mybacon == []:
					mybacon = []
				else:
					#print mybacon
					index = i - 1
					self.list_ctrl1.InsertStringItem(index, str(mybacon[4]))
					self.list_ctrl1.SetStringItem(index, 1, mybacon[0])
					self.list_ctrl1.SetStringItem(index, 2, mybacon[1])
					self.list_ctrl1.SetStringItem(index, 3, mybacon[2])
					self.list_ctrl1.SetStringItem(index, 4, mybacon[3])
					self.list_ctrl1.SetItemBackgroundColour(item=index, col=color_cell)
					self.list_ctrl1.SetItemData(index,index)
					mybacon = []
				for j in range(5):			
										
					mybacon.append(w_trans[k])
					k = k + 1
	
		self.list_ctrl1.SetColumnWidth(0, 0)
		self.list_ctrl1.SetColumnWidth(1, -2)
		self.list_ctrl1.SetColumnWidth(2, 210)
		self.list_ctrl1.SetColumnWidth(3, 210)
		self.list_ctrl1.SetColumnWidth(4, 110)
		
		self.hbox4 = wx.BoxSizer(wx.HORIZONTAL)
		self.hbox4.Add(self.image4, 0, wx.ALL|wx.LEFT, 2)
		self.hbox4.Add(self.list_ctrl, 0, wx.ALL|wx.CENTER, 2)
		
		self.box4 = wx.BoxSizer(wx.VERTICAL)
		self.box4.Add(w_text1, 0, wx.ALL|wx.CENTER, 5)
		self.box4.Add(w_text2, 0, wx.ALL|wx.CENTER, 2)
		self.box4.Add(w_text3, 0, wx.ALL|wx.CENTER, 2)
		self.box4.Add(self.hbox4, 0, wx.ALL|wx.CENTER, 2)
		self.box4.Add(w_text4, 0, wx.ALL|wx.LEFT, 2)
		self.box4.Add(self.list_ctrl1, 0, wx.ALL|wx.EXPAND, 2)
		
		self.SetSizer(self.box4)
		
		self.timer.Start(300 * 1000)

	def OnAbout(self, event):
		l_event = event.GetIndex()
		l_item1 = self.list_ctrl1.GetItem(l_event, 0)
		l_item2 = self.list_ctrl1.GetItem(l_event, 4)
		getblock = l_item1.GetText()
		getamount = l_item2.GetText()
		gettitle = "Wallet Information | Transaction Details"

		if tgetvars(getblock,getamount,gettitle):
			dlg = AboutBoxT()
			dlg.ShowModal()
			dlg.Destroy()
	
	def update(self, event):
		#print "Updating"
		self.timer.Stop()
		logging.info("Wallet: update requested")
		self.list_ctrl.DeleteAllItems()
		
		wallet_info = refresh(self.myaddress)
		
		t_row = ["BALANCE:","Spent Total:","Received Total:","Fees Paid:","Rewards:"]
		t_data = [wallet_info[4],wallet_info[1],wallet_info[0],wallet_info[3],wallet_info[2]]
		
		self.index = 0
		
		for items in t_row:
			temp_row = t_row[self.index]
			temp_data = t_data[self.index]
			self.list_ctrl.InsertStringItem(self.index, temp_row)
			self.list_ctrl.SetStringItem(self.index, 1, temp_data)
			self.list_ctrl.SetItemData(self.index, self.index)
			self.index += 1

		#str(credit),str(debit),str(rewards),str(fees),str(balance),str(bl_height)

		self.list_ctrl.SetColumnWidth(0, -1)
		self.list_ctrl.SetColumnWidth(1, -1)

		w_all = wgetrans(self.myaddress)
		self.list_ctrl1.DeleteAllItems()
		
		if w_all[1] == 0:
			w_text4.SetLabel("No transactions, looks like a new address")
			w_text4.SetForegroundColour(wx.RED)
		else:
			w_trans = w_all[0]
			w_limit = w_all[1]
			
			#build table here
			
			k = 0
			mybacon = []
			for i in range(w_limit):
				if i % 2 == 0:
					color_cell = ""#FFFFFF""
				else:
					color_cell = "#E8E8E8"
				if mybacon == []:
					mybacon = []
				else:
					#print mybacon
					index = i - 1
					self.list_ctrl1.InsertStringItem(index, str(mybacon[4]))
					self.list_ctrl1.SetStringItem(index, 1, mybacon[0])
					self.list_ctrl1.SetStringItem(index, 2, mybacon[1])
					self.list_ctrl1.SetStringItem(index, 3, mybacon[2])
					self.list_ctrl1.SetStringItem(index, 4, mybacon[3])
					self.list_ctrl1.SetItemBackgroundColour(item=index, col=color_cell)
					self.list_ctrl1.SetItemData(index,index)
					mybacon = []
				for j in range(5):			
										
					mybacon.append(w_trans[k])
					k = k + 1
	
		self.list_ctrl1.SetColumnWidth(0, 0)
		self.list_ctrl1.SetColumnWidth(1, -2)
		self.list_ctrl1.SetColumnWidth(2, 210)
		self.list_ctrl1.SetColumnWidth(3, 210)
		self.list_ctrl1.SetColumnWidth(4, 110)

		self.timer.Start(300 * 1000)
		#print "Updated"

class MainFrame(wx.Frame):
	def __init__(self):
		wx.Frame.__init__(self, None, title="Bismuth Tools", pos=(50,50), size=(700,720))
	
		loc = ticons.bismuthicon.GetIcon()
		self.SetIcon(loc)

		menubar = wx.MenuBar()

		m_file = wx.Menu()
		
		m_exit = m_file.Append(wx.ID_EXIT, '&Quit', 'Quit application')
		
		menubar.Append(m_file, '&File')
		
		help = wx.Menu()
		
		help.Append(101, '&Wallet Info', 'Wallet Information')
		help.Append(103, '&Ledger Query', 'Ledger Query Help')
		help.Append(104, '&Miner Query', 'Miner Query Help')
		help.Append(102, '&About', 'About this Program')
		
		menubar.Append(help, '&Help')
	
		self.SetMenuBar(menubar)
		
		self.Bind(wx.EVT_MENU, self.OnAbout, id=101)
		self.Bind(wx.EVT_MENU, self.OnAbout, id=103)
		self.Bind(wx.EVT_MENU, self.OnAbout, id=104)
		self.Bind(wx.EVT_MENU, self.OnAbout, id=102)
		self.Bind(wx.EVT_MENU, self.OnQuit, m_exit)
		
		global statusbar
		statusbar = self.CreateStatusBar()
		statusbar.SetFieldsCount(3)
		statusbar.SetStatusWidths([-1, -1, -3])
		statusbar.SetStatusText('Version 1.02', 0)
		statusbar.SetStatusText('Miner.db update:', 1)
		statusbar.SetStatusText('', 2)
		
		# Here we create a panel and a notebook on the panel
		p = wx.Panel(self)
		self.nb = wx.Notebook(p)
		
		# create the page windows as children of the notebook
		page1 = PageOne(self.nb)
		page2 = PageFour(self.nb)
		page3 = PageTwo(self.nb)
		page4 = PageThree(self.nb)
				
		# add the pages to the notebook with the label to show on the tab
		self.nb.AddPage(page1, "Home")
		self.nb.AddPage(page2, "Wallet Info")
		self.nb.AddPage(page3, "Ledger Query")
		self.nb.AddPage(page4, "Miner Query")

		# finally, put the notebook in a sizer for the panel to manage
		# the layout
		sizer = wx.BoxSizer()
		sizer.Add(self.nb, 1, wx.EXPAND)
		self.CentreOnParent(wx.BOTH)
		p.SetSizer(sizer)

		statusbar.Bind(EVT_UPDATE_STATUSBAR, self.OnStatus)

	def OnAbout(self, event):
		global thistitle
		global thisid
		thisid = event.Id
		if thisid == 101:
			thistitle = "Wallet Information Help"
		elif thisid == 102:
			thistitle = "About Bismuth Tools"
		elif thisid == 103:
			thistitle = "Ledger Query Help"
		elif thisid == 104:
			thistitle = "Miner Query Help"
		dlg = AboutBox()
		dlg.ShowModal()
		dlg.Destroy()
	
	def updateStatus(self, msg):
		mystatus = msg
		statusbar.SetStatusText(mystatus, 2)

	def OnStatus(self, evt):
		statusbar.SetStatusText(evt.msg, evt.st_id)			
	
    
	def OnQuit(self, event):
		logging.info("App: Quit")
		self.Close()

if __name__ == "__main__":

	background_thread = Thread(target=buildminerdb)
	background_thread.daemon = True
	background_thread.start()
	logging.info("Miner DB: Start Thread")
	app = wx.App()
	MainFrame().Show()
	app.MainLoop()
