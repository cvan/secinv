#!/usr/bin/python26
import MySQLdb
import netifaces

db = MySQLdb.connect(passwd="", db="secinv")
cursor = db.cursor()

cursor.execute("""SELECT * FROM assets_ip""")
cursor.fetchall()

for rows in cursor:
    print ''.join(str(rows))


assets_dict = {'i_ip': netifaces.ifaddresses('eth0')[netifaces.AF_INET][0]['addr'],
               'i_mac': netifaces.ifaddresses('eth0')[netifaces.AF_LINK][0]['addr'],
               'i_mask': netifaces.ifaddresses('eth0')[netifaces.AF_INET][0]['netmask']}

cursor.execute("""INSERT INTO assets_ip (i_ip, i_mac, i_mask) VALUES ('%s', '%s', '%s')""" %
               (assets_dict['i_ip'], assets_dict['i_mac'], assets_dict['i_mask']))
