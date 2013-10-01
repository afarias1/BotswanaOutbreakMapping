#
#SMS test via Google Voice
#
from pygeocoder import Geocoder, GeocoderError
from googlevoice import Voice
import sys
import BeautifulSoup
import time
from time import gmtime, strftime

import MySQLdb as mdb

from local_settings import *

last_msg = ""

def setup_db():
  """Setup mysql db"""

  mysql_host = host
  mysql_username = user
  mysql_password = passwd
  mysql_database = database
  try:
    con = mdb.connect(mysql_host, mysql_username, mysql_password, mysql_database, charset='utf8')
    cur = con.cursor()

  except mdb.Error, e:
    logger.error("Database Connection Error %d: %s", e.args[0], e.args[1])
    sys.exit(1)

  return con, cur


def newsms(htmlsms) :
    """
    newsms  -- get new SMS messages since last call to extractsms or newsms

    Output is a list of dictionaries, one per message.
    """
    msgitems = []										# accum message items here
    #	Extract all conversations by searching for a DIV with an ID at top level.
    tree = BeautifulSoup.BeautifulSoup(htmlsms)			# parse HTML into tree
    conversations = tree.findAll("div",attrs={"id" : True},recursive=False)
    for conversation in conversations :
        #	For each conversation, extract each row, which is one SMS message.
        rows = conversation.findAll(attrs={"class" : "gc-message-sms-row"})
        for row in rows[::-1] :								# for all rows
            #	For each row, which is one message, extract all the fields.
            msgitem = {"id" : conversation["id"]}		# tag this message with conversation ID
            spans = row.findAll("span",attrs={"class" : True}, recursive=False)
            for span in spans :							# for all spans in row
                cl = span["class"].replace('gc-message-sms-', '')
                msgitem[cl] = (" ".join(span.findAll(text=True))).strip()	# put text in dict
                msgitem['time'] = strftime("%Y-%m-%d %H:%M:%S", gmtime())
            if msgitem["id"] + msgitem["text"] == last_msg:
                return msgitems
            if msgitem['from'] == 'Me:':
                return msgitems
            msgitems.append(msgitem)					# add msg dictionary to list
    return msgitems


last_msg = ""
thanks = """Thank you for submitting your report."""
prompt = """This is the Botswana Outbreak Report System. Please text back:
[illness, ex: Malaria]
[location, ex: 555 Palo Rd, Gaborone]"""
be_more_specific = """Sorry, we could not find your location. Please:
1) check your spelling
2) use the full address (including city) or
3) use a more prominent street
and text back."""

voice = Voice()
voice.login()

con, cur = setup_db()

voice.sms()
msgs = newsms(voice.sms.html)
if msgs:
    last_msg = msgs[0]['id'] + msgs[0]['text']

while True:
    voice.sms()
    msgs = newsms(voice.sms.html)
    if msgs:
        for m in msgs:
            lines = m['text'].splitlines()
            if len(lines) < 2:
                try:
                    voice.send_sms(m['from'], prompt)
                    print "Sending prompt to", m['from']
                except:
                    print "Failed to send prompt to", m['from']
                continue
            condi = lines[0].upper()
            loc = lines[1]
            t = m['time']
            
            try:
                g=Geocoder.geocode(loc)
            except GeocoderError:
                print "Google maps couldn't find", loc
                voice.send_sms(m['from'], be_more_specific)
                continue
            lon, lat = g.coordinates
            print "Report of %s at %s (%s, %s) at time %s" % (condi, loc, lon, lat, t)
            try:
                cur.execute("INSERT INTO reports (condi, location, date) VALUES (%s, GeomFromText('POINT(%s %s)'), NOW())", (condi, lon, lat))
                con.commit()
                voice.send_sms(m['from'], thanks)
            except:
                raise
        last_msg = msgs[0]['id'] + msgs[0]['text']
    time.sleep(1)

