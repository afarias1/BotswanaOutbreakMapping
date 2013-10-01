#! /usr/bin/env python
import MySQLdb

from local_settings import *

db = MySQLdb.connect(host=host, user=user, passwd=passwd, db=database)
cursor = db.cursor()

cursor.execute("ALTER DATABASE `%s` CHARACTER SET 'utf8' COLLATE 'utf8_general_ci'" % database)

sql = "SELECT DISTINCT(table_name) FROM information_schema.columns WHERE table_schema = '%s'" % database
cursor.execute(sql)

results = cursor.fetchall()
for row in results:
  sql = "ALTER TABLE `%s` convert to character set DEFAULT COLLATE DEFAULT" % (row[0])
  cursor.execute(sql)
db.close()
