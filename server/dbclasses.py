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
    #_connection.debug = True
    #number = sqlobject.StringCol(length=14, unique=True)
    hostname = sqlobject.StringCol(length=255)
    sysip = sqlobject.StringCol(length=15)
    ext_ip = sqlobject.StringCol(length=15)
    httpd = sqlobject.BoolCol(default=0)
    mysqld = sqlobject.BoolCol(default=0)
    openvpn = sqlobject.BoolCol(default=0)
    nfs = sqlobject.BoolCol(default=0)
    kernel_rel = sqlobject.StringCol(length=255)
    rh_rel = sqlobject.StringCol(length=255)
    interfaces = sqlobject.MultipleJoin('AssetIp')
    date_added = sqlobject.DateTimeCol(default=None)

#Asset.dropTable()
Asset.createTable(ifNotExists=True)

'''
assets = Asset.select()
asset_count = assets.count()
'''

class AssetIp(sqlobject.SQLObject):
    _connection = connection
    #_connection.debug = True
    asset = sqlobject.ForeignKey('Asset')
    i_name = sqlobject.StringCol(length=255)
    i_ip = sqlobject.StringCol(length=15)
    i_mask = sqlobject.StringCol(length=255)
    i_mac = sqlobject.StringCol(length=255)

#AssetIp.dropTable()
AssetIp.createTable(ifNotExists=True)

'''

# L145
this_asset = Asset.select(Asset.q.sysip=='10.2.72.89')
this_asset_ip = this_asset[0].id if this_asset.count() else 0

#print 'len:', this_asset

#print '\nthis_machine:', this_asset
#print this_machine[0].id

asset_ip_count = AssetIp.select(AssetIp.q.asset==this_asset_ip).count()
print asset_ip_count

'''
class AssetPort(sqlobject.SQLObject):
    _connection = connection
    #_connection.debug = True
    asset = sqlobject.ForeignKey('Asset')

    # TODO: processes, ports
    process = sqlobject.StringCol(length=255)
    port = sqlobject.IntCol(length=5)

    date_added = sqlobject.DateTimeCol(default=None)
    date_updated = sqlobject.DateTimeCol(default=None)

    # TODO: Empty database upon every scan. (?)

AssetPort.createTable(ifNotExists=True)


class ScanHistory(sqlobject.SQLObject):
    _connection = connection
    #_connection.debug = True
    asset = sqlobject.ForeignKey('Asset')
    date_scanned = sqlobject.DateTimeCol(default=None)

ScanHistory.createTable(ifNotExists=True)



Asset.sqlmeta.addJoin(sqlobject.MultipleJoin('AssetIp', joinMethodName='interfaces'))

'''
print 'assets==>', assets
print 'asset_count==>', asset_count

a = Asset.select()


print '------\n\n', list(a), '\n-----\n'
print '------\n\n', a[0].interfaces, '\n-----\n'


a = Asset.select(Asset.q.sysip=='10.2.72.89')
print 'a.columns: ---- ', Asset.sqlmeta.columns, '---\n'
a_id = a[0].id if this_asset.count() else 0

asset_ip_count = AssetIp(asset=a_id, i_name='', i_ip='192.168.1.1', i_mask='', i_mac='')

'''

