#!/usr/bin/env python26

import datetime
import os
import sys

def diff_list(l_old, l_new):
    """
    Creates a new dict representing a diff between two lists.
    """

    set_new, set_past = set(l_new), set(l_old)
    intersect = set_new.intersection(set_past)

    added = list(set_new - intersect)
    deleted = list(set_past - intersect)

    # Added and deleted items.
    diff = {'added': added, 'deleted': deleted}

    return diff


# BASE_PATH is the absolute path of '..' relative to this script location.
BASE_PATH = reduce(lambda l, r: l + os.path.sep + r,
    os.path.dirname(os.path.realpath(__file__)).split(os.path.sep)[:-1])

# Append settings directory.
sys.path.append(os.path.join(BASE_PATH, 'secinv'))

from django.core.management import execute_manager
try:
    import settings
except:
    print "Could not import settings"
    sys.exit(1)

# To suppress MySQLdb and haystack warnings.
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

from django.core.management import setup_environ
setup_environ(settings)

from apps.machines.models import *


# TODO: generate auth_keys

class ServerFunctions:
    def __init__(self, AUTH_KEY):
        self.machine_ip = '0.0.0.0'
        self.machine_id = 0
        self.auth_key = AUTH_KEY
        self.is_authenticated = False

        # Create logger.
        #self.logger = logging.getLogger("secinv")

    def authenticate(self, auth_key):
        '''
        Compare server's auth_key against client's auth_key.
        '''
        if self.auth_key != auth_key:
            print 'failed authentication'
            return False

        print 'ok authentication'
        self.is_authenticated = True
        return True

    def machine(self, ip_dict, system_dict, services_dict, rpms_dict):
        if not self.is_authenticated:
            return False

        # Get the machine IP address as the first ethernet interface.
        for interface in ip_dict.keys():
            if interface[0:3] == 'eth':
                self.machine_ip = ip_dict[interface]['i_ip']
                break

        ## Machine.
        try:
            m_obj = None

            m_objs = Machine.objects.filter(sys_ip=self.machine_ip).all()
            if m_objs:
                m_obj = m_objs[0]
            else:
                # Find machine by hostname if we cannot find by ip address.
                m_objs_by_h = Machine.objects.filter(
                    hostname=system_dict['hostname']).all()

                m_obj = m_objs_by_h[0]

            m_obj.date_scanned = datetime.datetime.now()
            m_diff = []

            if m_obj.sys_ip != self.machine_ip:
                m_obj.sys_ip = self.machine_ip
                m_diff.append('sys_ip')

            if m_obj.hostname != system_dict['hostname']:
                m_obj.hostname = system_dict['hostname']
                m_diff.append('hostname')

            if m_diff:
                m_obj.diff = ','.join(m_diff)
                m_obj.date_modified = datetime.datetime.now()

            m_obj.save()

            self.machine_obj = m_obj
            self.machine_id = self.machine_obj.id
        except IndexError:
            # Add machine if not in table.
            mach_dict = {'sys_ip': self.machine_ip,
                         'hostname': system_dict['hostname'],
                         'ext_ip': '',
                         'date_scanned': datetime.datetime.now()}
            m_new = Machine.objects.create(**mach_dict)
            self.machine_obj = m_new
            self.machine_id = m_new.id


        ## Interfaces.
        for interface in ip_dict.keys():
            if ip_dict[interface]['i_mac'] in ('00:00:00:00',
                                               '00:00:00:00:00:00'):
                ip_dict[interface]['i_mac'] = ''

            # If all fields are empty, then device is inactive -- so do not
            # insert a row.
            if ip_dict[interface]['i_ip'] == '' and \
               ip_dict[interface]['i_mac'] == '' and \
               ip_dict[interface]['i_mask'] == '':
                continue

            # If interface already exists in table, update accordingly.
            try:
                i_object = Interface.objects.filter(machine__id=self.machine_id,
                                                    i_name=interface).latest()

                i_diff = []
                if i_object.i_ip != ip_dict[interface]['i_ip']:
                    i_diff.append('i_ip')

                if i_object.i_mac != ip_dict[interface]['i_mac']:
                    i_diff.append('i_mac')

                if i_object.i_mask != ip_dict[interface]['i_mask']:
                    i_diff.append('i_mask')

                if i_diff:
                    i_dict = {'machine': self.machine_obj,
                              'i_name': interface,
                              'i_ip': ip_dict[interface]['i_ip'],
                              'i_mac': ip_dict[interface]['i_mac'],
                              'i_mask': ip_dict[interface]['i_mask']}
                    i_object = Interface.objects.create(**i_dict)

            except Interface.DoesNotExist:
                print 'interface does not exist'

                i_dict = {'machine': self.machine_obj,
                          'i_name': interface,
                          'i_ip': ip_dict[interface]['i_ip'],
                          'i_mac': ip_dict[interface]['i_mac'],
                          'i_mask': ip_dict[interface]['i_mask']}
                i_object = Interface.objects.create(**i_dict)

        # See if any interfaces have since been deactivated.

        # Get latest interfaces (select by distinct interface name).
        distinct_interfaces = Interface.objects.filter(
            machine__id=self.machine_id).values_list(
            'i_name', flat=True).distinct()
        print 'distinct_interfaces:', distinct_interfaces

        i_diff = diff_list(distinct_interfaces, ip_dict.keys())
        print 'i_diff:', i_diff

        # Update each interface as inactive.
        for i in i_diff['deleted']:
            i_latest = Interface.objects.filter(machine__id=self.machine_id,
                                                i_name=i, active=True).latest()

            i_inactive = Interface.objects.filter(machine__id=self.machine_id,
                                                  i_name=i, active=False).all()

            # Check if interface is already listed as inactive.
            if i_inactive.exists():
                continue

            i_dict = {'machine': self.machine_obj,
                      'i_name': i_latest.i_name,
                      'i_ip': i_latest.i_ip,
                      'i_mac': i_latest.i_mac,
                      'i_mask': i_latest.i_mask,
                      'active': False}
            i_object = Interface.objects.create(**i_dict)


        ## System.
        try:
            sys_object = System.objects.filter(
                machine__id=self.machine_id).latest()

            sys_diff = []

            if sys_object.kernel_rel != system_dict['kernel_rel']:
                sys_diff.append('kernel_rel')

            if sys_object.rh_rel != system_dict['rh_rel']:
                sys_diff.append('rh_rel')

            if sys_object.nfs != system_dict['nfs']:
                sys_diff.append('nfs')

            if sys_diff:
                sys_dict = {'machine': self.machine_obj,
                            'kernel_rel': system_dict['kernel_rel'],
                            'rh_rel': system_dict['rh_rel'],
                            'nfs': system_dict['nfs'],
                            'diff': ','.join(sys_diff)}
                sys_object = System.objects.create(**sys_dict)

        except System.DoesNotExist:
            print 'system does not exist'

            sys_dict = {'machine': self.machine_obj,
                        'kernel_rel': system_dict['kernel_rel'],
                        'rh_rel': system_dict['rh_rel'],
                        'nfs': system_dict['nfs']}
            sys_object = System.objects.create(**sys_dict)


        ## Services.
        procs = services_dict.keys()
        csv_procs = ','.join(procs)
        ports = services_dict.values()
        csv_ports = ','.join(ports)

        try:
            s_object = Services.objects.filter(
                machine__id=self.machine_id).latest()

            s_diff = []
            s_diff_ins_processes = []
            s_diff_del_processes = []
            s_diff_ins_ports = []
            s_diff_del_ports = []

            if s_object.processes != csv_procs:
                old = re.split(',', s_object.processes)
                new = procs

                s1 = set(old)
                s2 = set(new)
                print s1
                print s2

                new_procs = s2.difference(s1)
                del_procs = s1.difference(s2)
                print new_procs
                print del_procs

                s_diff_ins_processes = list(s2.difference(s1))
                s_diff_del_processes = list(s1.difference(s2))
                print s_diff_ins_processes
                print s_diff_del_processes

                s_diff.append('processes')

            if s_object.ports != csv_ports:
                old = re.split(',', s_object.ports)
                new = ports

                s1 = set(old)
                s2 = set(new)

                new_procs = s2.difference(s1)
                del_procs = s1.difference(s2)

                s_diff_ins_ports = list(s2.difference(s1))
                s_diff_del_ports = list(s1.difference(s2))

                s_diff.append('ports')

            if s_diff:
                s_dict = {'machine': self.machine_obj,
                          'processes': csv_procs,
                          'ports': csv_ports,
                          'diff': ','.join(s_diff)}
                s_object = Services.objects.create(**s_dict)

        except Services.DoesNotExist:
            print 'services does not exist'

            s_dict = {'machine': self.machine_obj,
                      'processes': csv_procs,
                      'ports': csv_ports}
            s_object = Services.objects.create(**s_dict)


        ## RPMs.
        try:
            r_object = RPMs.objects.filter(machine__id=self.machine_id).latest()

            r_diff = []
            if r_object.rpms != rpms_dict['unserialized']:
                r_diff.append('rpms')

            if r_diff:
                r_dict = {'machine': self.machine_obj,
                          'rpms': rpms_dict['unserialized']}
                r_object = RPMs.objects.create(**r_dict)

        except RPMs.DoesNotExist:
            print 'RPMs does not exist'

            r_dict = {'machine': self.machine_obj,
                      'rpms': rpms_dict['unserialized']}
            r_object = RPMs.objects.create(**r_dict)

        return True
