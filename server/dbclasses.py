#!/usr/bin/python26

import sqlobject
from xmlrpcserver import DB_LOGIN

'''
def DBConnect():
    connection = None
    if DB_LOGIN['engine'] == 'mysql':
        import MySQLdb
        import MySQLdb.cursors

        MySQLConnection = sqlobject.mysql.builder()
        connection = MySQLConnection(host=DB_LOGIN['host'],
                                          user=DB_LOGIN['user'],
                                          password=DB_LOGIN['passwd'],
                                          db=DB_LOGIN['db'])
        return connection
'''

connection = None
if DB_LOGIN['engine'] == 'mysql':
    import MySQLdb
    import MySQLdb.cursors

    MySQLConnection = sqlobject.mysql.builder()
    connection = MySQLConnection(host=DB_LOGIN['host'],
                                      user=DB_LOGIN['user'],
                                      password=DB_LOGIN['passwd'],
                                      db=DB_LOGIN['db'])


class Asset(sqlobject.SQLObject):
    _connection = connection
    #number = sqlobject.StringCol(length=14, unique=True)
    hostname = sqlobject.StringCol(length=255)
    sysip = sqlobject.StringCol(length=15)
    ext_ip = sqlobject.StringCol(length=15)
    httpd = sqlobject.BoolCol(default=0)
    mysqld = sqlobject.BoolCol(default=0)
    openvpn = sqlobject.BoolCol(default=0)
    nfs = sqlobject.BoolCol(default=0)
    date_added = sqlobject.DateTimeCol(default=None)
    
Asset.createTable(ifNotExists=True)

class AssetIP(sqlobject.SQLObject):
    _connection = connection
    #asset_ip = ForeignKey('Asset').sysip

