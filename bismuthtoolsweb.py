# Bismuth Tools Web Edition
# version 1.02_web
# Copyright Maccaspacca 2017
# Copyright Hclivess 2016 to 2017
# Author Maccaspacca

import web
import sqlite3
import time
import re
import os
from multiprocessing import Process
import multiprocessing
import base64
import logging
import random
import ConfigParser
from bs4 import BeautifulSoup
import urllib2

logging.basicConfig(level=logging.INFO, 
                    filename='toolsweb.log', # log to this file
                    format='%(asctime)s %(message)s') # include timestamp

logging.info("logging initiated")

global myaddress
global myrate
global mysponsor

config = ConfigParser.ConfigParser()
config.readfp(open(r'sponsor.txt'))
logging.info("Reading config file.....")
mysponsor = int(config.get('My Sponsors', 'sponsors'))
myaddress = config.get('My Sponsors', 'address')
myrate = float(config.get('My Sponsors', 'rate'))
logging.info("Config file read completed")

if mysponsor == 1:
	mysponsor = True
else:
	mysponsor = False
#mysponsor = False

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

	logging.info("Miner DB: Checkname result: Address {} = {}".format(str(myaddress),goodname))
	
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
	
	logging.info("Miner DB: Checked for zero transactions: {}".format(zeroaddress))
	
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

	print "Building miners db......wait"
	
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

	# Get mining addresses from ledgerdb
	donn = sqlite3.connect(os.path.expanduser('~/Bismuth/static/ledger.db'))
	donn.text_factory = str
	d = donn.cursor()
	d.execute("SELECT distinct recipient FROM transactions WHERE block_height > ? AND reward != 0;",(hyper_limit,))
	miner_list_raw = d.fetchall()
	d.close()

	temp_result = []
	
	# Validate miner address and get info from ledgerdb

	logging.info("Miner DB: Getting new data.....please wait this may take some time!")
	
	for x in miner_list_raw:
		
		temp_miner = str(x[0])
		if len(temp_miner) == 56:
			if not zerocheck(temp_miner):
				m_info = getvars(temp_miner)
				m_name = checkmyname(temp_miner)
				temp_result.append((temp_miner, m_info[0], m_info[1], m_info[2], m_info[3], m_info[4], m_info[5], m_info[6], m_name))

	logging.info("Miner DB: Inserting information into database.....")
			
	bonn = sqlite3.connect('tempminers.db')
	bonn.text_factory = str
	b = bonn.cursor()
	
	time.sleep(1)

	for y in temp_result:

		b.execute('INSERT INTO minerlist VALUES (?,?,?,?,?,?,?,?,?)', (y[0],y[1],y[2],y[3],y[4],y[5],y[6],y[7],y[8]))

	bonn.commit()
	b.close()
	bonn.close()

	if os.path.isfile('miners.db'):
		os.remove('miners.db')
	os.rename('tempminers.db','miners.db')
	logging.info("Miner DB: Done !")
	print "All done....tools are now ready"
	return True

# //////////////////////////////////////////////////////////
# Sponsor databse stuff
# /////////////////////////////////////////////////////////

def getmeta(this_url):
# This module attempts to get Open Graph information for the sponsor site_name
# If this fails it attempts to use the "name" property before just filling the info with the url

	this_property = ("og:title","og:image","og:url","og:description","og:site_name")
	oginfo = []

	url = urllib2.urlopen(this_url)

	webpage = url.read()

	soup = BeautifulSoup(webpage, "html.parser")
	
	for prop in this_property:
		temp_tag = soup.find("meta", {"property": prop})
		if temp_tag is not None:
			oginfo.append(str(temp_tag["content"]))
		else:
			ex_prop = prop.split(":")[1]
			ex_tag = soup.find("meta", {"name": ex_prop})
			if ex_tag is not None:
				oginfo.append(str(ex_tag["content"]))
			else:
				oginfo.append("")

	#print oginfo
	return oginfo

def updatesponsors():

	print "Building sponsors db..... wait"

	if os.path.isfile('tempsponsors.db'):
		os.remove('tempsponsors.db')

	logging.info("Sponsor DB: Rebuild")
	# create empty sponsors database
	sponsorlist = sqlite3.connect('tempsponsors.db')
	sponsorlist.text_factory = str
	m = sponsorlist.cursor()
	m.execute("CREATE TABLE IF NOT EXISTS sponsorlist (title, image, url, description, end, paid, name)")
	sponsorlist.commit()
	sponsorlist.close()
	logging.info("Sponsor DB: Creating or updating sponsors database")
	# create empty sponsorlist
		
	logging.info("Sponsor DB: Getting up to date list of sponsors.....")

	mysponsors = []

	conn = sqlite3.connect(os.path.expanduser('~/Bismuth/static/ledger.db'))
	c = conn.cursor()
	c.execute("SELECT * FROM transactions WHERE recipient = ? AND instr(openfield, 'sponsor=') > 0;",(myaddress,))

	mysponsors = c.fetchall()

	c.close()

	the_sponsors = []

	for dudes in mysponsors:

		dud = dudes[11].split("=")
		try:
			temp_block = dudes[0]
			temp_paid = float(dudes[4])
			max_block = temp_block + (int(round(temp_paid * myrate)) + 100)

			latest_block = latest()
						
			if latest_block[0] < max_block:
				temp_ogs = getmeta(str(dud[1]))
				the_sponsors.append((temp_ogs[0],temp_ogs[1],temp_ogs[2],temp_ogs[3],str(max_block),str(temp_block),temp_ogs[4]))
			else:
				pass
			
		except:
			pass
	if not the_sponsors:
		the_sponsors.append(("Bismuth","https://i1.wp.com/bismuth.cz/wp-content/uploads/2017/03/cropped-mesh2-2.png?fit=200%2C200","http://bismuth.cz/","In the truly free world, there are no limits","500000","68924","Bismuth"))
			
	logging.info("Sponsor DB: Inserting information into database.....")
			
	conn = sqlite3.connect('tempsponsors.db')
	conn.text_factory = str
	c = conn.cursor()

	for y in the_sponsors:

		c.execute('INSERT INTO sponsorlist VALUES (?,?,?,?,?,?,?)', (y[0],y[1],y[2],y[3],y[4],y[5],y[6]))

	conn.commit()
	c.close()
	conn.close()

	if os.path.isfile('sponsors.db'):
		os.remove('sponsors.db')
	os.rename('tempsponsors.db','sponsors.db')
	logging.info("Sponsor DB: Done !")


def buildminerdb():
	
	bobble = rebuildme()
	#bobble = True
	
	while bobble:
		logging.info("Miner DB: Waiting for 10 minutes.......")
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

	if not os.path.exists('sponsors.db'):
		# create empty sponsors database
		logging.info("Sponsor DB: Created new as none existed")
		sponsorlist = sqlite3.connect('sponsors.db')
		sponsorlist.text_factory = str
		m = sponsorlist.cursor()
		m.execute(
			"CREATE TABLE IF NOT EXISTS sponsorlist (title, image, url, description, end, paid, name)")
		sponsorlist.commit()
		sponsorlist.close()
		# create empty sponsorlist

checkstart()
latest()
updatesponsors()

#////////////////////////////////////////////////////////////

def getall():

	conn = sqlite3.connect(os.path.expanduser('~/Bismuth/static/ledger.db'))
	c = conn.cursor()
	c.execute("SELECT * FROM transactions ORDER BY block_height DESC, timestamp DESC LIMIT 15;")

	myall = c.fetchall()
	
	return myall

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
	
def get_sponsor():

	if mysponsor:

		logging.info("Sponsors: Get sites from sponsors.db")
		conn = sqlite3.connect('sponsors.db')
		conn.text_factory = str
		c = conn.cursor()
		c.execute("SELECT * FROM sponsorlist;")
		sponsor_result = c.fetchall()
		c.close()
		
		x_top = len(sponsor_result) -1
		x_go = random.randint(0,x_top)
		
		sponsor_display = []
		
		sponsor_display.append('<table style="width: 200px;">\n')
		sponsor_display.append('<tr style="text-align: center;">\n')
		sponsor_display.append('<td style="border:hidden;"><a href="{}" style="text-decoration:none;">'.format(sponsor_result[x_go][2]))
		sponsor_display.append('{}</a></td>\n'.format(sponsor_result[x_go][6]))
		sponsor_display.append('</tr>\n')
		sponsor_display.append('<tr style="text-align: center;">\n')
		sponsor_display.append('<td style="border:hidden;">\n')
		sponsor_display.append('<a href="{}" style="text-decoration:none;">'.format(sponsor_result[x_go][2]))
		sponsor_display.append('<img src="{}" alt="{}" height="100px">'.format(sponsor_result[x_go][1],sponsor_result[x_go][3]))
		sponsor_display.append('</img></a>\n')
		sponsor_display.append('</td>\n')
		sponsor_display.append('</tr>\n')
		sponsor_display.append('<tr style="text-align: center;">\n')
		sponsor_display.append('<td style="border:hidden;"><a href="{}" style="text-decoration:none;">'.format(sponsor_result[x_go][2]))
		sponsor_display.append('{}</a></td>\n'.format(sponsor_result[x_go][0]))
		sponsor_display.append('</tr>\n')
		sponsor_display.append('</table>\n')
		
		logging.info("Sponsors: {} was displayed".format(sponsor_result[x_go][2]))
	
	else:
		sponsor_display = []
		sponsor_display.append('<p></p>')

	return sponsor_display

def bgetvars(myaddress):

	conn = sqlite3.connect('miners.db')
	conn.text_factory = str
	c = conn.cursor()
	c.execute("SELECT * FROM minerlist WHERE address = ?;",(myaddress,))
	miner_details = c.fetchone()
	c.close()
	
	return miner_details

def my_head(bo):

	mhead = []
	
	mhead.append('<!doctype html>\n')
	mhead.append('<html>\n')
	mhead.append('<head>\n')
	mhead.append('<link rel = "icon" href = "static/explorer.ico" type = "image/x-icon" />\n')
	mhead.append('<style>\n')
	mhead.append('h1, h2, p, li, td, label {font-family: Verdana;}\n')
	mhead.append('body {font-size: 75%;}\n')
	mhead.append('ul {list-style-type: none;margin: 0;padding: 0;overflow: hidden;background-color: #333;}\n')
	mhead.append('li {float: left;}\n')
	mhead.append('li a {display: inline-block;color: white;text-align: center;padding: 14px 16px;text-decoration: none;}\n')
	mhead.append('li a:hover {background-color: #111;}\n')
	mhead.append('.btn-link{border:none;outline:none;background:none;cursor:pointer;color:#0000EE;padding:0;text-decoration:underline;font-family:inherit;font-size:inherit;}\n')
	mhead.append(bo + '\n')
	mhead.append('</style>\n')
	mhead.append('<title>Bismuth Tools</title>\n')
	mhead.append('</head>\n')
	mhead.append('<body background="static/explorer_bg.png">\n')
	mhead.append('<center>\n')
	mhead.append('<table style="border:0">\n')
	mhead.append('<tr style="border:0"><td style="border:0">\n')
	mhead.append('<ul>\n')
	mhead.append('<li><a href="">Menu:</a></li>\n')
	mhead.append('<li><a href="/">Home</a></li>\n')
	mhead.append('<li><a href="/ledgerquery">Ledger Query</a></li>\n')
	mhead.append('<li><a href="/minerquery">Miner Query</a></li>\n')
	if mysponsor:
		mhead.append('<li><a href="/sponsorinfo">Sponsors</a></li>\n')
	mhead.append('</ul>\n')
	mhead.append('</td></tr>\n')
	mhead.append('</table>\n')

	return mhead


urls = (
    '/', 'index',
	'/minerquery', 'minerquery',
	'/ledgerquery', 'ledgerquery',
	'/sponsorinfo', 'sponsorinfo'
)

class index:

    def GET(self):
	
		thisall = getall()
		
		thisview = []

		i = 0

		for x in thisall:
			if i % 2 == 0:
				color_cell = "#E8E8E8"
			else:
				color_cell = "white"
			thisview.append('<tr bgcolor ="{}">'.format(color_cell))
			thisview.append('<td>{}</td>'.format(str(x[0])))
			thisview.append('<td>{}'.format(str(time.strftime("%Y/%m/%d,%H:%M:%S", time.localtime(float(x[1]))))))
			thisview.append('<td>{}</td>'.format(str(x[2])))
			thisview.append('<td>{}</td>'.format(str(x[3].encode('utf-8'))))
			thisview.append('<td>{}</td>'.format(str(x[4])))
			thisview.append('<td>{}</td>'.format(str(x[7])))
			thisview.append('<td>{}</td>'.format(str(x[8])))
			thisview.append('<td>{}</td>'.format(str(x[9])))
			thisview.append('<td>{}</td>'.format(str(x[10])))
			thisview.append('</tr>\n')
			i = i+1		
		
	
		#initial = my_head('table, th, td {border: 0;}')
		initial = my_head('table, th, td {border: 1px solid black;border-collapse: collapse;padding: 5px;-webkit-column-width: 100%;-moz-column-width: 100%;column-width: 100%;}')
	
		initial.append('<table ><tbody><tr>\n')
		initial.append('<td align="center" style="border:hidden;">')
		sponsor1 = get_sponsor()
		initial = initial + sponsor1
		initial.append('</td>\n')
		initial.append('<td align="center" style="border:hidden;">\n')
		initial.append('<h1>Bismuth Cryptocurrency</h1>\n')
		initial.append('<h2>Welcome to the Bismuth Tools Web Edition</h2>\n')
		initial.append('<p>Choose what you want to to do next by clicking an option from the menu above</p>\n')
		initial.append('<h2>Last 15 Transactions</h2>\n')
		initial.append('</td>\n')
		initial.append('<td align="center" style="border:hidden;">')
		sponsor2 = get_sponsor()
		initial = initial + sponsor2
		initial.append('</td>\n')
		initial.append('</tr></tbody></table>\n')
		initial.append('<table style="font-size: 70%">\n')
		initial.append('<tr>\n')
		initial.append('<td>Block</td>\n')
		initial.append('<td>Timestamp</td>\n')
		initial.append('<td>From</td>\n')
		initial.append('<td>To</td>\n')
		initial.append('<td>Amount</td>\n')
		initial.append('<td>Block Hash</td>\n')
		initial.append('<td>Fee</td>\n')
		initial.append('<td>Reward</td>\n')
		initial.append('<td>Keep</td>\n')
		initial.append('</tr>\n')
		initial = initial + thisview
		initial.append('</table>\n')
		initial.append('<p>&copy; Copyright: Maccaspacca and HCLivess, 2017</p>')
		initial.append('</center>\n')
		initial.append('</body>\n')
		initial.append('</html>')

		starter = "" + str(''.join(initial))

		return starter
		
class minerquery:

    def GET(self):
	
		newform = web.input(myaddy="myaddy")

		getaddress = "%s" %(newform.myaddy)

		#Nonetype handling - simply replace with ""

		if not getaddress:
			addressis = ""
		elif getaddress == "myaddy":
			addressis = ""
		else:
			#print "Info requested: " + getaddress
			m_info = bgetvars(getaddress)
			addressis = "<table style='width:50%;'>"
			addressis = addressis + "<tr><td align='right' bgcolor='#DAF7A6'><b>Address:</b></td><td bgcolor='#D0F7C3'>{}</td></tr>".format(str(m_info[0]))
			addressis = addressis + "<tr><td align='right' bgcolor='#DAF7A6'><b>Latest Block Found:</b></td><td bgcolor='#D0F7C3'>{}</td></tr>".format(str(m_info[1]))
			addressis = addressis + "<tr><td align='right' bgcolor='#DAF7A6'><b>First Block Found:</b></td><td bgcolor='#D0F7C3'>{}</td></tr>".format(str(m_info[2]))
			addressis = addressis + "<tr><td align='right' bgcolor='#DAF7A6'><b>Total Blocks Found:</b></td><td bgcolor='#D0F7C3'>{}</td></tr>".format(str(m_info[3]))
			addressis = addressis + "<tr><td align='right' bgcolor='#DAF7A6'><b>Time Spent Mining:</b></td><td bgcolor='#D0F7C3'>{} Days (Adjusted Estimate)</td></tr>".format(str(m_info[4]))
			addressis = addressis + "<tr><td align='right' bgcolor='#DAF7A6'><b>Blocks Per Day:</b></td><td bgcolor='#D0F7C3'>{} (Estimate)</td></tr>".format(str(m_info[5]))
			addressis = addressis + "<tr><td align='right' bgcolor='#DAF7A6'><b>Total Rewards:</b></td><td bgcolor='#D0F7C3'>{}</td></tr>".format(str(m_info[6]))
			addressis = addressis + "<tr><td align='right' bgcolor='#DAF7A6'><b>Total Energy Cost:</b></td><td bgcolor='#D0F7C3'>${} (Estimate | 180W PC usage | USD)</td></tr>".format(str(m_info[7]))
			addressis = addressis + "</table>"
	
		all = miners()
		
		view = []
		i = 0
		j = 1
		for x in all:
			thisminer = str(x[0])
			if len(thisminer) == 56:
				if j % 2 == 0:
					color_cell = "white"
				else:
					color_cell = "#E8E8E8"
				view.append("<tr bgcolor ='{}'>".format(color_cell))
				view.append("<td>{}</td>".format(str(j)))
				if len(str(x[8])) > 0:
					view.append("<td><a href='/minerquery?myaddy={}'>{}</a></td>".format(thisminer,str(x[8])))
				else:
					view.append("<td><a href='/minerquery?myaddy={}'>{}</a></td>".format(thisminer,thisminer))					
				view.append("<td>{}</td>".format(str(x[3])))				
				j = j+1
			view.append("</tr>\n")
			i = i+1
		
		lister = my_head('table, th, td {border: 1px solid black;border-collapse: collapse;padding: 5px;-webkit-column-width: 100%;-moz-column-width: 100%;column-width: 100%;}')
		
		lister.append('<h2>Bismuth Miner Query Tool</h2>\n')
		lister.append('<p><b>Mining statistics since block number: {}</b></p>\n'.format(str(hyper_limit)))
		lister.append('<p><b>Hint: Click on an address to see more detail</b></p>\n')
		lister.append('<p>Note: this page may be up to 20 mins behind</p>\n')
		lister.append('<p style="color:#08750A">{}</p>\n'.format(addressis))
		lister.append('<p></p>\n')
		lister.append('<table style="width:60%" bgcolor="white">\n')
		lister.append('<tr>\n')
		lister.append('<td>Rank</td>\n')
		lister.append('<td>List of Miners</td>\n')
		lister.append('<td>Blocks Found</td>\n')
		lister.append('</tr>\n')
		lister = lister + view
		lister.append('</table>\n')
		lister.append('<p>&copy; Copyright: Maccaspacca and HCLivess, 2017</p>')
		lister.append('</center>\n')
		lister.append('</body>\n')
		lister.append('</html>')

		html = "" + str(''.join(lister))

		return html

class ledgerquery:


    def GET(self):
			
		mylatest = latest()
		
		plotter = my_head('table, th, td {border: 1px solid black;border-collapse: collapse;padding: 5px;-webkit-column-width: 100%;-moz-column-width: 100%;column-width: 100%;}')
		
		plotter.append('<h2>Bismuth Ledger Query Tool</h2>\n')
		plotter.append('<p>Get a List of Transactions</p>\n')
		plotter.append('<form method="post" action="/ledgerquery">\n')
		plotter.append('<table>\n')
		plotter.append('<tr><th><label for="block">Enter a Block Number, Block Hash or Address</label></th><td><input type="text" id="block" name="block" size="58"/></td></tr>\n')
		plotter.append('<tr><th><label for="Submit Query">Click Submit to List Transactions</label></th><td><button id="Submit Query" name="Submit Query">Submit Query</button></td></tr>\n')
		plotter.append('</table>\n')
		plotter.append('</form>\n')
		#plotter.append('</p>\n')
		plotter.append('<p>The latest block: {} was found {} seconds ago</p>\n'.format(str(mylatest[0]),str(int(mylatest[1]))))
		plotter.append('<p>The last Hyperblock was at block: {}</p>\n'.format(str(hyper_limit)))
		plotter.append('<p>Queries for blocks before {} will not be found</p>\n'.format(str(hyper_limit)))
		plotter.append('</body>\n')
		plotter.append('</html>')
		# Initial Form

		html = "" + str(''.join(plotter))

		return html

    def POST(self):
	
		mylatest = latest()
	
		newform = web.input(block="block")
		
		myblock = "%s" %(newform.block)
		
		#Nonetype handling - simply replace with "0"
		
		if not myblock:
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
			
				extext = "<p style='color:#08750A'><b>ADDRESS FOUND | Credits: {} | Debits: {} | Rewards: {} |".format(myxtions[0],myxtions[1],myxtions[2])
				extext = extext + " Fees: {} | BALANCE: {}</b></p>".format(myxtions[3],myxtions[4])
				
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
					extext = "<p style='color:#C70039'>Error !!! Nothing found for the address or block hash you entered</p>"
				else:
					extext = "<p>Transaction found for block hash</p>"
		
		if my_type == 2:
		
			if myblock == "0":
			
				all = []
			
			else:
			
				conn = sqlite3.connect(os.path.expanduser('~/Bismuth/static/ledger.db'))
				c = conn.cursor()
				c.execute("SELECT * FROM transactions WHERE block_height = ?;", (myblock,))

				all = c.fetchall()
				#print all
				
				c.close()
		
			if not all:
				extext = "<p style='color:#C70039'>Error !!! Block, address or hash not found. Maybe you entered bad data or nothing at all?</p>\n"
			else:
				pblock = int(myblock) -1
				nblock = int(myblock) +1
				extext = "<form action='/ledgerquery' method='post'><table><tr>\n"
				if pblock > (hyper_limit - 2):
					extext = extext + "<td style='border:hidden;'><button type='submit' name='block' value='{}' class='btn-link'><< Previous Block</button></td>\n".format(str(pblock))
				else:
					extext = extext + "<td style='border:hidden;'><p></p></td>\n"			
				extext = extext + "<td style='border:hidden;'><p><b>Transactions for block {}</b></p></td>\n".format(str(myblock))
				if nblock < (int(mylatest[0]) + 1):
					extext = extext + "<td style='border:hidden;'><button type='submit' name='block' value='{}' class='btn-link'>Next Block >></button></td>\n".format(str(nblock))
				else:
					extext = extext + "<td style='border:hidden;'><p></p></td>\n"
				extext = extext + "</tr></table></form>\n"
		
		view = []
		i = 0
		for x in all:
			if i % 2 == 0:
				color_cell = "#E8E8E8"
			else:
				color_cell = "white"
			view.append('<tr bgcolor ="{}">'.format(color_cell))
			view.append('<td>{}</td>'.format(str(x[0])))
			view.append('<td>{}'.format(str(time.strftime("%Y/%m/%d,%H:%M:%S", time.localtime(float(x[1]))))))
			view.append('<td>{}</td>'.format(str(x[2])))
			view.append('<td>{}</td>'.format(str(x[3].encode('utf-8'))))
			view.append('<td>{}</td>'.format(str(x[4])))
			view.append('<td>{}</td>'.format(str(x[7])))
			view.append('<td>{}</td>'.format(str(x[8])))
			view.append('<td>{}</td>'.format(str(x[9])))
			view.append('<td>{}</td>'.format(str(x[10])))
			view.append('</tr>\n')
			i = i+1
		
		replot = my_head('table, th, td {border: 1px solid black;border-collapse: collapse;padding: 5px;-webkit-column-width: 100%;-moz-column-width: 100%;column-width: 100%;}')
		
		replot.append('<h2>Bismuth Ledger Query Tool</h2>\n')
		replot.append('<p>Get a List of Transactions</p>\n')
		replot.append('<form method="post" action="/ledgerquery">\n')
		replot.append('<table>\n')
		replot.append('<tr><th><label for="block">Enter a Block Number, Block Hash or Address</label></th><td><input type="text" id="block" name="block" size="58"/></td></tr>\n')
		replot.append('<tr><th><label for="Submit Query">Click Submit to List Transactions</label></th><td><button id="Submit Query" name="Submit Query">Submit Query</button></td></tr>\n')
		replot.append('</table>\n')
		replot.append('</form>\n')
		#replot.append('</p>\n')
		replot.append('<p>The latest block: {} was found {} seconds ago</p>\n'.format(str(mylatest[0]),str(int(mylatest[1]))))
		replot.append(extext)
		replot.append('<table style="font-size: 70%">\n')
		replot.append('<tr>\n')
		replot.append('<td>Block</td>\n')
		replot.append('<td>Timestamp</td>\n')
		replot.append('<td>From</td>\n')
		replot.append('<td>To</td>\n')
		replot.append('<td>Amount</td>\n')
		replot.append('<td>Block Hash</td>\n')
		replot.append('<td>Fee</td>\n')
		replot.append('<td>Reward</td>\n')
		replot.append('<td>Keep</td>\n')
		replot.append('</tr>\n')
		replot = replot + view
		replot.append('</table>\n')
		replot.append('<p>&copy; Copyright: Maccaspacca and HCLivess, 2017</p>')
		replot.append('</center>\n')
		replot.append('</body>\n')
		replot.append('</html>')
		
		html1 = "" + str(''.join(replot))

		return html1

class sponsorinfo:

    def GET(self):
	
		#initial = my_head('table, th, td {border: 0;}')
		initial = my_head('table, th, td {border: 1px solid black;border-collapse: collapse;padding: 5px;-webkit-column-width: 100%;-moz-column-width: 100%;column-width: 100%;}')
	
		initial.append('<table ><tbody><tr>\n')
		initial.append('<td align="center" style="border:hidden;">')
		initial.append('<p></p>')
		initial.append('</td>\n')
		initial.append('<td align="center" style="border:hidden;">\n')
		initial.append('<h1>Bismuth Cryptocurrency</h1>\n')
		initial.append('<h2>Sponsorship Information</h2>\n')
		initial.append('<p>To sponsor and have your weblink and logo appear on the Home page, send at least 1 Bismuth to:</p>\n')
		initial.append('<p><b>{}</b></p>\n'.format(myaddress))
		initial.append('<p>The current rate is {} blocks per Bismuth sent</p>\n'.format(str(int(myrate))))
		initial.append('<p></p>')
		initial.append('<p>When you send your payment include the openfield text: sponsor=your_url</p>\n')
		initial.append('<p>This tool will read the Opengraph properties: title, url, image and site_name - of your site to display its information</p>\n')
		initial.append('<p></p>')
		initial.append('<p><a href="http://ogp.me/" style="text-decoration:none;">Click here for more information about Opengraph</a></p>\n')		
		initial.append('</td>\n')
		initial.append('<td align="center" style="border:hidden;">')
		initial.append('<p></p>')
		initial.append('</td>\n')
		initial.append('</tr></tbody></table>\n')
		initial.append('<p>&copy; Copyright: Maccaspacca and HCLivess, 2017</p>')
		initial.append('</center>\n')
		initial.append('</body>\n')
		initial.append('</html>')

		starter = "" + str(''.join(initial))

		return starter
	
if __name__ == "__main__":
	multiprocessing.freeze_support()
	app = web.application(urls, globals(), True)
	background_thread = Process(target=buildminerdb)
	background_thread.daemon = True
	background_thread.start()
	#background_thread.join()
	logging.info("Miner DB: Start Thread")
	app.run()
