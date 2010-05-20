#!/usr/bin/python26

import os
import re
import string

class Assets:
    def __init__(self):
        self.assets_dict = {}

    def get_services(self):
        '''
        Check if httpd, mysqld, and openvpn are currently running processes.
        '''
        # Services we need to check for should have a dictionary key below.
        services_dict = {'httpd': 0,
                         'mysqld': 0,
                         'openvpn': 0}

        '''
        # The hard way:
        full_ps = os.popen("ps -ef").read()

        lines = re.split("\n", full_ps)

        for s in services_dict.keys():
            for line in lines:
                if line[-len(s):] == s:
                    services_dict[s] = 1
        '''

        for service in services_dict.keys():
            # If we can get a PID for the process name, it's obviously running.
            dirty_pids = os.popen('/sbin/pidof %s' % service).readline()
            clean_pids = dirty_pids[0]

            p = re.compile(r"\S*(.+)\S*")
            m = p.match(clean_pids)

            if m:
                services_dict[service] = 1

        #self.assets_dict = dict(self.assets_dict.items() + services.dict())
        #print services_dict

        return services_dict

    def get_hostname(self):
        full_hn = os.popen("hostname").read()

        p = re.compile(r"([^\.]+)")
        m = p.match(full_hn)

        hn = ''
        if m:
            hn = m.group(0)

        self.assets_dict['hostname'] = hn
        return hn

    def get_kernel_version(self):
        full_kernel = os.popen("uname -a").read()

        # Get version number.
        kernel_ver = ''

        chunks = re.split(" ", full_kernel)
        if chunks:
            kernel_ver = chunks[2]

        self.assets_dict['kernel_ver'] = kernel_ver
        return kernel_ver

    def get_redhat_version(self):
        rh_version = ''

        try:
            rh_file = open("/etc/redhat-release", "r")

            release_line = rh_file.readline()
            rh_file.close()

            p = re.compile(r"Red Hat Enterprise Linux \S+ release ([^\n].+)\n")
            m = p.match(release_line)
            if m:
                rh_version = m.group(1)

        except IOError:
            # TODO: Logging Error -- cannot open /etc/redhat-release.
            pass

        self.assets_dict['rh_rel'] = rh_version
        return rh_version

    def get_assets_dict(self):
        services_dict = self.get_services()
        assets_dict = {'hostname': self.get_hostname(),
                       'kernel_ver': self.get_kernel_version(),
                       'rh_rel': self.get_redhat_version(),
                       'httpd': services_dict['httpd'],
                       'mysqld': services_dict['mysqld'],
                       'openvpn': services_dict['openvpn']}
        return assets_dict



class AssetsIP:
    def __init__(self):
        self.data = None

    def get_interfaces(self):
        import netifaces

        assets_dict = {}

        for interface in netifaces.interfaces():
            interfaceDict = netifaces.ifaddresses(interface)

            assets_dict[interface] = {
                'i_ip': interfaceDict[netifaces.AF_INET][0]['addr'] \
                        if netifaces.AF_INET in interfaceDict else '',
                'i_mac': interfaceDict[netifaces.AF_LINK][0]['addr'] \
                         if netifaces.AF_LINK in interfaceDict else '',
                'i_mask': interfaceDict[netifaces.AF_INET][0]['netmask'] \
                          if netifaces.AF_INET in interfaceDict else ''
            }

        return assets_dict

