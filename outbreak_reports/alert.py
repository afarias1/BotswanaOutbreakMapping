# -*- coding: utf-8 -*-

from twilio.rest import TwilioRestClient
import MySQLdb as mdb
from local_settings import *
from math import *
def setup_db():
    mysql_host = host
    mysql_username = user
    mysql_password = passwd


    try:
        con = mdb.connect(mysql_host, mysql_username, mysql_password, 'outbreak', charset='utf8')
        cur = con.cursor()

    except mdb.Error, e:
        logger.error("Database Connection Error %d: %s", e.args[0], e.args[1])
        sys.exit(1)

    return con, cur


def calc_dist(orig, dest):
    return sqrt((orig['lat']-dest['lat'])**2 + (orig['lon']-dest['lon'])**2)
#    return 3956 * 2 * asin(sqrt( pow(sin((orig.lat - abs(dest.lat)) * pi/180 / 2),2) + \
#                                 cos(orig.lat * pi/180 ) * \
#                                 cos(abs(dest.lat) *  pi/180) * \
#                          pow(sin((orig.lon – dest.lon) *  pi/180 / 2), 2) ))
    

def init_twilio():
    sid = 'AC0ca1be72a71d32acdffd936890bc688a';
    token = '4ef35d697529291c127b94ab0a7d3260';

    client = TwilioRestClient(sid, token)
    return client

con, cur = setup_db()
client = init_twilio()

cur.execute("SELECT AsText(location), number FROM numbers")
num = cur.fetchone()

outbreak_center = raw_input('Location: ')
raw_split = outbreak_center.split(' ,')
orig = {'lat':raw_split[0], 'lon':raw_split[1]}

outbreak_radius = int(raw_input('Radius: '))

while num!=None:
    loc = num[0][6:-1].split(' ')
    dest= {'lat':float(loc[0]), 'lon':float(loc[1])}
    dist = calc_dist(orig, dest)
    if dist < outbreak_radius:
        print "Alerting %s" % num
        message=client.messages.create(to=num, from_='2024704686', body = 'Warning: there is an ongoing breakout of %s in %s. Please visit https://')

    num = cur.fetchone()

