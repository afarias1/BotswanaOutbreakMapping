# -*- coding: utf-8 -*-
"""
    Flaskr
    ~~~~~~

    A microblog example application written as Flask tutorial with
    Flask and sqlite3.

    :copyright: (c) 2010 by Armin Ronacher.
    :license: BSD, see LICENSE for more details.
"""
import json
import os
import MySQLdb as mdb
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
from local_settings import *

con = None
cur = None
# create our little application :)
app = Flask(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE='/tmp/flaskr.db',
    DEBUG=True,
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
#app.config.from_envvar('FLASKR_SETTINGS', silent=True)#

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

@app.route('/locations')
def get_locs():
    cur.execute('select condi, AsText(location) from reports')
    results = cur.fetchall()
    con.commit()
    data = []
    for condi, loc in results:
        d = {'condi': condi, 'loc':loc[6:-1].split(' ')}
        print d
        data.append(d)
    return json.dumps(data) 

@app.route('/')
def show_entries():
    return render_template('layout.html')

if __name__ == '__main__':
    con, cur = setup_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='localhost', port=port)
