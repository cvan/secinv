#!/usr/bin/python26

#import sqlobject
from dbclasses import *

# TODO: generate auth_keys and remove DB_LOGIN

class ServerFunctions:
    def __init__(self, AUTH_KEY, DB_LOGIN):
        self.machine_ip = '0.0.0.0'
        self.machine_id = 0
        self.auth_key = AUTH_KEY
        self.is_authenticated = False

        # Create logger.
        #self.logger = logging.getLogger("secinv")

        # To suppress MySQLdb DeprecationWarning.
        import warnings
        warnings.filterwarnings("ignore", category=DeprecationWarning)

        self.cursor = None

        # TODO: add support for other DB engines
        if DB_LOGIN['engine'] == 'mysql':
            import MySQLdb
            import MySQLdb.cursors

            #self.connection = DBConnect()

            db = MySQLdb.connect(host=DB_LOGIN['host'],
                                 user=DB_LOGIN['user'],
                                 passwd=DB_LOGIN['passwd'],
                                 db=DB_LOGIN['db'],
                                 cursorclass=MySQLdb.cursors.DictCursor)
            self.cursor = db.cursor()

    def authenticate(self, auth_key):
        '''
        Compare server's auth_key against client's auth_key.
        '''
        if self.auth_key != auth_key:
            return False

        self.is_authenticated = True
        return True

    def assets(self, assets_dict):
        if not self.is_authenticated:
            return False

        self.cursor.execute("""SELECT COUNT(*) as c FROM history
                               WHERE machine_id = '%s'""" % self.machine_id)
        count = self.cursor.fetchone()
        count = int(count['c'])

        if count:
            # Update 'date_scanned' field for this system.
            self.cursor.execute("""UPDATE history SET date_scanned = NOW()
                                   WHERE machine_id = '%s'""" % self.machine_id)
        else:
            # Add a row for this system.
            self.cursor.execute("""INSERT INTO history (machine_id, date_scanned)
                                   VALUES ('%s', NOW())""" % self.machine_id)


        self.cursor.execute("""SELECT COUNT(*) as c, hostname, httpd, mysqld,
                               openvpn, nfs, kernel_rel, rh_rel FROM assets
                               WHERE machine_id = '%s'""" % self.machine_id)
        assets_row = self.cursor.fetchone()
        count = int(assets_row['c'])
        is_same = False

        if count:
            '''
            self.cursor.execute("""UPDATE assets SET hostname = '%s',
                                   httpd = '%s', mysqld = '%s', openvpn = '%s',
                                   nfs = '%s', kernel_rel = '%s', rh_rel = '%s'
                                   WHERE sys_ip = '%s'""" %
                                (assets_dict['hostname'],
                                 assets_dict['httpd'],
                                 assets_dict['mysqld'],
                                 assets_dict['openvpn'],
                                 assets_dict['nfs'],
                                 assets_dict['kernel_rel'],
                                 assets_dict['rh_rel'],
                                 self.asset_ip))
            '''

            del assets_row['c']
            for k, old_v in assets_row.iteritems():
                if assets_dict[k] == old_v:
                    is_same = True

        # Insert a row only if the assets values have changed.
        if not is_same:
            # TODO: 'ext_ip'?
            self.cursor.execute("""INSERT INTO assets (hostname,
                                   machine_id, httpd, mysqld, openvpn, nfs,
                                   kernel_rel, rh_rel, date_added)
                                   VALUES ('%s', '%s', '%s', '%s', '%s',
                                   '%s', '%s', '%s', NOW())""" %
                                (assets_dict['hostname'],
                                 self.machine_id,
                                 assets_dict['httpd'],
                                 assets_dict['mysqld'],
                                 assets_dict['openvpn'],
                                 assets_dict['nfs'],
                                 assets_dict['kernel_rel'],
                                 assets_dict['rh_rel']))


        print "\nInserted into assets:", assets_dict

        self.cursor.execute("""SELECT * FROM assets""")
        self.cursor.fetchall()

        for rows in self.cursor:
            print ''.join(str(rows))


        return True

    def assets_ip(self, assets_ip_dict):
        if not self.is_authenticated:
            return False

        # Get the machine IP address as the first ethernet interface.
        for interface in assets_ip_dict.keys():
            if interface[0:3] == 'eth':
                self.machine_ip = assets_ip_dict[interface]['i_ip']
                break

        self.cursor.execute("""SELECT id FROM machines
                               WHERE sys_ip = '%s'""" % self.machine_ip)
        machines_row = self.cursor.fetchone()
        if machines_row:
            self.machine_id = int(machines_row['id'])

        # Add machine if not already in database table.
        if not self.machine_id:
            self.cursor.execute("""INSERT INTO machines (sys_ip, date_added)
                                   VALUES ('%s', NOW())""" % self.machine_ip)

            self.cursor.execute("""SELECT id FROM machines
                                   WHERE sys_ip = '%s'""" % self.machine_ip)
            machines_row = self.cursor.fetchone()
            if machines_row:
                self.machine_id = int(machines_row['id'])


        for interface in assets_ip_dict.keys():
            if assets_ip_dict[interface]['i_mac'] in ('00:00:00:00',
                                                      '00:00:00:00:00:00'):
                assets_ip_dict[interface]['i_mac'] = ''

            # If all fields are empty, then device is inactive -- so do not
            # insert a row.
            if assets_ip_dict[interface]['i_ip'] == '' and \
               assets_ip_dict[interface]['i_mac'] == '' and \
               assets_ip_dict[interface]['i_mask'] == '':
                continue

            # If already exists in table, update row(s) accordingly.
            self.cursor.execute("""SELECT COUNT(*) as c FROM assets_ip
                                   WHERE machine_id = '%s'""" % self.machine_id)
            assets_ip_row = self.cursor.fetchone()
            count = int(assets_ip_row['c'])

            is_same = False
            if count:
                del assets_ip_row['c']
                for k, old_v in assets_ip_row.iteritems():
                    print k, '===>', old_v
                    if assets_ip_dict[k] == old_v:
                        is_same = True

            if not is_same:
                # Insert a row only if the assets_ip values have changed.
                self.cursor.execute("""INSERT INTO assets_ip (machine_id, i_name,
                                       i_ip, i_mac, i_mask)
                                  VALUES ('%s', '%s', '%s', '%s', '%s')""" %
                                   (self.machine_id,
                                    interface,
                                    assets_ip_dict[interface]['i_ip'] \
                                    if interface[0:3] != 'eth' else '',
                                    assets_ip_dict[interface]['i_mac'],
                                    assets_ip_dict[interface]['i_mask']))

        print "\nInserted into assets_ip:", assets_ip_dict

        self.cursor.execute("""SELECT * FROM assets_ip""")
        self.cursor.fetchall()

        for rows in self.cursor:
            print ''.join(str(rows))

        return True

    def rpms(self, rpms_dict):
        if not self.is_authenticated:
            return False

        #print "\nInserted into rpms:", rpms_dict

        self.cursor.execute("""SELECT COUNT(*) as c FROM assets_rpms
                               WHERE machine_id = '%s'""" % self.machine_id)
        assets_rpms_row = self.cursor.fetchone()
        count = int(assets_rpms_row['c'])

        if count:
            # Update all rpms from last scan for this machine_id.
            self.cursor.execute("""UPDATE assets_rpms SET rpms = '%s',
                                   date_updated = NOW()
                                   WHERE machine_id = '%s'""" %
                                (MySQLdb.escape_string(rpms_dict['serialized']),
                                 self.machine_id))
        else:
            # If this machine doesn't have a rpms row, create one.
            self.cursor.execute("""INSERT INTO assets_rpms (machine_id, rpms,
                                   date_added)
                                   VALUES ('%s', '%s', NOW())""" %
                                (self.machine_id,
                                 MySQLdb.escape_string(rpms_dict['serialized'])))

        return True

    def ports(self, ports_dict):
        if not self.is_authenticated:
            return False

        print "\nInserted into ports:", ports_dict

        csv_procs = ','.join(ports_dict.keys())
        csv_ports = ','.join(ports_dict.values())

        self.cursor.execute("""SELECT COUNT(*) as c FROM assets_ports
                               WHERE machine_id = '%s'""" % self.machine_id)
        assets_ports_row = self.cursor.fetchone()
        count = int(assets_ports_row['c'])

        if count:
            # Update all ports from last scan for this machine_id.
            self.cursor.execute("""UPDATE assets_ports SET processes = '%s',
                                   ports = '%s', date_updated = NOW()
                                   WHERE machine_id = '%s'""" %
                                (csv_procs, csv_ports, self.machine_id))
        else:
            # If this machine doesn't have a ports row, create one.
            self.cursor.execute("""INSERT INTO assets_ports (machine_id, processes,
                                   ports, date_added)
                                   VALUES ('%s', '%s', '%s', NOW())""" %
                                (self.machine_id, csv_procs, csv_ports))

        return True

