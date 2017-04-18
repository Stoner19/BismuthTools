# Bismuth Tools Web Edition | Sponsors Module
# version 0.42_Web
# Copyright Maccaspacca 2017
# Copyright Hclivess 2016 to 2017
# Author Maccaspacca

import sqlite3
import time
import os
import logging
import ConfigParser
from bs4 import BeautifulSoup
import urllib2


logging.basicConfig(level=logging.INFO, 
                    filename='sponsors.log', # log to this file
                    format='%(asctime)s %(message)s') # include timestamp

logging.info("logging initiated")

global myaddress
global myrate

config = ConfigParser.ConfigParser()
config.readfp(open(r'sponsor.txt'))
logging.info("Reading config file.....")
myaddress = config.get('My Sponsors', 'address')
myrate = float(config.get('My Sponsors', 'rate'))
logging.info("Config file read completed")

def latest():

	conn = sqlite3.connect('../static/ledger.db')
	conn.text_factory = str
	c = conn.cursor()
	c.execute("SELECT * FROM transactions WHERE reward != ? ORDER BY block_height DESC LIMIT 1;", ('0',)) #or it takes the first
	result = c.fetchall()
	c.close()
	db_block_height = result[0][0]
	
	return db_block_height

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
				oginfo.append(this_url)

	#print oginfo
	return oginfo

def updateme():

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

	conn = sqlite3.connect('../static/ledger.db')
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
			
			if latest_block < max_block:
				temp_ogs = getmeta(str(dud[1]))
				the_sponsors.append((temp_ogs[0],temp_ogs[1],temp_ogs[2],temp_ogs[3],str(max_block),str(temp_block),temp_ogs[4]))
			else:
				pass
			
		except:
			pass
			
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
	
	return True

def buildsponsordb():
	time.sleep(5)
	bibble = updateme()
	#bibble = True

	while bibble:
		logging.info("Sponsor DB: Waiting for 10 minutes.......")
		print "Sponsor DB: Waiting for 10 minutes......."
		time.sleep(600)
		bibble = updateme()

def checkstart():

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
buildsponsordb()
