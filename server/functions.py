#!/usr/bin/python26

class ServerFunctions:
    def __init__(self, AUTH_KEY, DB_LOGIN):
        self.data = None
        self.asset_ip = '0.0.0.0'
        self.auth_key = AUTH_KEY
        self.is_authenticated = False

        # Create logger.
        #self.logger = logging.getLogger("secinv")

        #self.connect_database(DB_LOGIN)

    #def connect_database(self, DB_LOGIN):
        # To suppress MySQLdb DeprecationWarning.
        import warnings
        warnings.filterwarnings("ignore", category=DeprecationWarning)

        import MySQLdb


        db = MySQLdb.connect(host=DB_LOGIN['host'],
                             user=DB_LOGIN['user'],
                             passwd=DB_LOGIN['passwd'],
                             db=DB_LOGIN['db'])
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

        '''
        TODO: Do this only if baseline not set.
        '''

        self.cursor.execute("""SELECT COUNT(*) FROM assets
                               WHERE sysip = '%s'""" % self.asset_ip)
        count = self.cursor.fetchone()
        count = int(count[0])
        if count:
            # TODO: Check if the assets values have changed.

            # INSERT INTO assets_checkin.

            '''
            self.cursor.execute("""UPDATE assets sys_name = '%s',
                                   kernel_rel = '%s', rh_rel = '%s',
                                   WHERE sysip = '%s'""" %
                                (assets_dict['hostname'],
                                 assets_dict['kernel_rel'],
                                 assets_dict['rh_rel'],
                                 self.asset_ip))
            '''
        #else:

        # TODO: 'ext_ip' ?
        self.cursor.execute("""INSERT INTO assets (date_added, sysname, sysip,
                          httpd, mysqld, openvpn, kernel_rel, rh_rel)
                          VALUES (NOW(), '%s', '%s', '%s', '%s', '%s', '%s', '%s')""" %
                       (assets_dict['hostname'],
                        self.asset_ip,
                        assets_dict['httpd'],
                        assets_dict['mysqld'],
                        assets_dict['openvpn'],
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

        # TODO: Check if exists: insert or update.

        asset_ip = '0.0.0.0'
        for interface in assets_ip_dict.keys():
            if interface[0:3] == 'eth':
                asset_ip = assets_ip_dict[interface]['i_ip']
                self.asset_ip = asset_ip

        for interface in assets_ip_dict.keys():
            if assets_ip_dict[interface]['i_mac'] in ('00:00:00:00', '00:00:00:00:00:00'):
                assets_ip_dict[interface]['i_mac'] = ''

            # If all fields are empty, do not insert a row for inactive device.
            if assets_ip_dict[interface]['i_ip'] == '' and \
               assets_ip_dict[interface]['i_mac'] == '' and \
               assets_ip_dict[interface]['i_mask'] == '':
                continue

            # If already exists in table, update row(s) accordingly.
            self.cursor.execute("""SELECT COUNT(*) FROM assets_ip
                              WHERE asset_ip = '%s'""" % asset_ip)
            count = self.cursor.fetchone()
            count = int(count[0])
            if count:
                # TODO: Check if the values have changed.
                '''
                self.cursor.execute("""UPDATE assets_ip asset_ip = '%s',
                                  i_name = '%s', i_ip = '%s', i_mac = '%s',
                                  i_mask = '%s' WHERE asset_ip = '%s'""" %
                               (interface,
                                assets_ip_dict[interface]['i_ip'] if interface[0:3] != 'eth' else '',
                                assets_ip_dict[interface]['i_mac'],
                                assets_ip_dict[interface]['i_mask'],
                                asset_ip))
                '''
            #else:
                self.cursor.execute("""INSERT INTO assets_ip (asset_ip, i_name,
                                  i_ip, i_mac, i_mask)
                                  VALUES ('%s', '%s', '%s', '%s', '%s')""" %
                               (asset_ip,
                                interface,
                                assets_ip_dict[interface]['i_ip'] if interface[0:3] != 'eth' else '',
                                assets_ip_dict[interface]['i_mac'],
                                assets_ip_dict[interface]['i_mask']))

        print "\nInserted into assets_ip:", assets_ip_dict

        self.cursor.execute("""SELECT * FROM assets_ip""")
        self.cursor.fetchall()

        for rows in self.cursor:
            print ''.join(str(rows))

        return True

    def mounts(self, mounts_dict):
        if not self.is_authenticated:
            return False

        print "\nInserted into mounts:", mounts_dict

        return True

    def rpms(self, rpms_dict):
        if not self.is_authenticated:
            return False

        print "\nInserted into rpms:", rpms_dict

        return True


