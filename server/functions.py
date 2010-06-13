#!/usr/bin/env python26

from __future__ import with_statement

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
except ImportError:
    sys.exit('Error: Could not import Django settings')

# To suppress MySQLdb warning.
import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)

from django.core.management import setup_environ
setup_environ(settings)

import reversion


from apps.machines.models import *
#from apps.machines.models import Interface, System, Services, RPMs, \
#                                 SSHConfig, IPTable, IPTableChain, IPTableRules


class ServerFunctions:
    def __init__(self, AUTH_KEY):
        self.machine_ip = '0.0.0.0'
        self.machine_id = 0
        self.auth_key = AUTH_KEY
        self.is_authenticated = False

        # Create logger.
        #self.logger = logging.getLogger('secinv')

    def authenticate(self, auth_key):
        """
        Compare server's auth_key against client's auth_key.
        """
        if self.auth_key != auth_key:
            return False

        self.is_authenticated = True
        return True

    def machine(self, ip_dict, system_dict, services_dict, rpms_dict,
                sshconfig_dict, ipt_dict):
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
                # TODO: Delete field.
                m_obj.diff = ','.join(m_diff)
                m_obj.date_modified = datetime.datetime.now()

            with reversion.revision:
                m_obj.save()

            self.machine_obj = m_obj
            self.machine_id = self.machine_obj.id
        except IndexError:
            # Add machine if not in table.

            #mach_dict = {'sys_ip': self.machine_ip,
            #             'hostname': system_dict['hostname'],
            #             'ext_ip': '',
            #             'date_scanned': datetime.datetime.now()}
            #m_new = Machine.objects.create(**mach_dict)

            with reversion.revision:
                m_new = Machine.objects.create(sys_ip=self.machine_ip,
                    hostname=system_dict['hostname'],
                    date_scanned=datetime.datetime.now())
                m_new.save()

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

                i_diff = False
                if i_object.i_ip != ip_dict[interface]['i_ip']:
                    i_diff = True

                if i_object.i_mac != ip_dict[interface]['i_mac']:
                    i_diff = True

                if i_object.i_mask != ip_dict[interface]['i_mask']:
                    i_diff = True

                # If it was inactive, it's active now.
                if not i_object.active:
                    i_diff = True

                if i_diff:
                    i_object.machine = self.machine_obj
                    i_object.i_name = interface
                    i_object.i_ip = ip_dict[interface]['i_ip']
                    i_object.i_mac = ip_dict[interface]['i_mac']
                    i_object.i_mask = ip_dict[interface]['i_mask']
                    i_object.active = True
                    i_object.date_added = datetime.datetime.now()
                    with reversion.revision:
                        i_object.save()

                    #i_object = Interface.objects.create(**i_dict)

            except Interface.DoesNotExist:
                #i_dict = {'machine': self.machine_obj,
                #          'i_name': interface,
                #          'i_ip': ip_dict[interface]['i_ip'],
                #          'i_mac': ip_dict[interface]['i_mac'],
                #          'i_mask': ip_dict[interface]['i_mask']}
                #i_object = Interface.objects.create(**i_dict)

                i_new = Interface.objects.create(machine=self.machine_obj,
                    i_name=interface,
                    i_ip=ip_dict[interface]['i_ip'],
                    i_mac=ip_dict[interface]['i_mac'],
                    i_mask=ip_dict[interface]['i_mask'])
                i_new.save()

        # See if any interfaces have since been deactivated.

        # Get latest interfaces (select by distinct interface name).
        distinct_interfaces = Interface.objects.filter(
            machine__id=self.machine_id, active=True).values_list(
            'i_name', flat=True).distinct()

        i_diff = diff_list(distinct_interfaces, ip_dict.keys())

        # Update each interface as inactive.
        for i in i_diff['deleted']:
            try:
                i_latest = Interface.objects.filter(machine__id=self.machine_id,
                                                    i_name=i, active=True).latest()
            except Interface.DoesNotExist:
                continue

            #i_latest = Interface.objects.filter(machine__id=self.machine_id,
            #                                    i_name=i).latest()
            print '- deleting', i
            #i_latest.delete()

            i_latest.active = False
            with reversion.revision:
                i_latest.save()

            #i_dict = {'machine': self.machine_obj,
            #          'i_name': i_latest.i_name,
            #          'i_ip': i_latest.i_ip,
            #          'i_mac': i_latest.i_mac,
            #          'i_mask': i_latest.i_mask,
            #          'active': False}
            #i_object = Interface.objects.create(**i_dict)


        ## System.
        try:
            print 'getting system'
            sys_object = System.objects.filter(
                machine__id=self.machine_id).latest()

            sys_diff = False

            if sys_object.kernel_rel != system_dict['kernel_rel']:
                sys_diff = True

            if sys_object.rh_rel != system_dict['rh_rel']:
                sys_diff = True

            if sys_object.nfs != system_dict['nfs']:
                sys_diff = True

            if sys_object.ip_fwd != system_dict['ip_fwd']:
                sys_diff = True

            print sys_diff
            if sys_diff:
                print 'updating system'
                sys_object.machine = self.machine_obj
                sys_object.kernel_rel = system_dict['kernel_rel']
                sys_object.rh_rel = system_dict['rh_rel']
                sys_object.nfs = system_dict['nfs']
                sys_object.ip_fwd = system_dict['ip_fwd']
                sys_object.iptables = ipt_dict['status']
                sys_object.date_added = datetime.datetime.now()
                with reversion.revision:
                    sys_object.save()

                #sys_dict = {'machine': self.machine_obj,
                #            'kernel_rel': system_dict['kernel_rel'],
                #            'rh_rel': system_dict['rh_rel'],
                #            'nfs': system_dict['nfs'],
                #            'ip_fwd': system_dict['ip_fwd'],
                #            'iptables': ipt_dict['status']}
                #sys_object = System.objects.create(**sys_dict)

        except System.DoesNotExist:
            print 'system does not exist'
            #sys_dict = {'machine': self.machine_obj,
            #            'kernel_rel': system_dict['kernel_rel'],
            #            'rh_rel': system_dict['rh_rel'],
            #            'nfs': system_dict['nfs'],
            #            'ip_fwd': system_dict['ip_fwd'],
            #            'iptables': ipt_dict['status']}
            with reversion.revision:
                sys_object = System.objects.create(machine=self.machine_obj,
                    kernel_rel=system_dict['kernel_rel'],
                    rh_rel=system_dict['rh_rel'],
                    nfs=system_dict['nfs'],
                    ip_fwd=system_dict['ip_fwd'],
                    iptables=ipt_dict['status'])
                sys_object.save()


        ## Services.
        procs = services_dict.keys()
        csv_procs = ','.join(procs)
        ports = services_dict.values()
        csv_ports = ','.join(ports)

        try:
            s_object = Services.objects.filter(
                machine__id=self.machine_id).latest()

            s_diff = False

            if s_object.processes != csv_procs:
                s_diff = True

            if s_object.ports != csv_ports:
                s_diff = True

            if s_diff:
                s_object.machine = self.machine_obj
                s_object.processes = csv_procs
                s_object.ports = csv_ports
                s_object.date_added = datetime.datetime.now()
                with reversion.revision:
                    s_object.save()

                #s_dict = {'machine': self.machine_obj,
                #          'processes': csv_procs,
                #          'ports': csv_ports}
                #s_object = Services.objects.create(**s_dict)

        except Services.DoesNotExist:
            s_dict = {'machine': self.machine_obj,
                      'processes': csv_procs,
                      'ports': csv_ports}
            s_object = Services.objects.create(**s_dict)


        ## RPMs.
        try:
            r_object = RPMs.objects.filter(machine__id=self.machine_id).latest()

            r_diff = False

            if r_object.rpms != rpms_dict['list']:
                r_diff = True

            if r_diff:
                r_object.machine = self.machine_obj
                r_object.rpms = rpms_dict['list']
                r_object.date_added = datetime.datetime.now()
                with reversion.revision:
                    r_object.save()

                #r_dict = {'machine': self.machine_obj,
                #          'rpms': rpms_dict['list']}

                #r_object = RPMs.objects.create(**r_dict)

        except RPMs.DoesNotExist:
            r_dict = {'machine': self.machine_obj,
                      'rpms': rpms_dict['list']}
            r_object = RPMs.objects.create(**r_dict)


        ## SSH configuration file.
        params = sshconfig_dict.keys()
        csv_params = '\n'.join(params)
        values = sshconfig_dict.values()
        csv_values = '\n'.join(values)

        try:
            s_object = SSHConfig.objects.filter(
                machine__id=self.machine_id).latest()

            s_diff = False

            if s_object.parameters != csv_params:
                s_diff = True

            if s_object.values != csv_values:
                s_diff = True

            if s_diff:
                s_object.machine = self.machine_obj
                s_object.parameters = csv_params
                s_object.values = csv_values
                s_object.date_added = datetime.datetime.now()
                with reversion.revision:
                    s_object.save()

                #s_dict = {'machine': self.machine_obj,
                #          'parameters': csv_params,
                #          'values': csv_values}
                #s_object = SSHConfig.objects.create(**s_dict)

        except SSHConfig.DoesNotExist:
            s_dict = {'machine': self.machine_obj,
                      'parameters': csv_params,
                      'values': csv_values}
            s_object = SSHConfig.objects.create(**s_dict)


        ## iptables.
        print 'Received iptables dictionary:\n'
        iptables_rules = ipt_dict['rules']
        #print iptables_rules

        # TODO: If unique table names in DB are not in tables_rules --> set as inactive.

        for table_name, v in iptables_rules.iteritems():
            try:
                ipt_table = IPTable.objects.filter(
                    machine__id=self.machine_id, name=table_name).latest()
                ipt_table_id = ipt_table.id
            except IPTable.DoesNotExist:
                i_dict = {'machine': self.machine_obj,
                          'name': table_name}
                ipt_table = IPTable.objects.create(**i_dict)

                ipt_table_id = ipt_table.id


            for chain in v['chains']:
                try:
                    i_object = IPTableChain.objects.filter(
                        table__id=ipt_table_id, name=chain['name']).latest()

                    i_diff = False

                    # TODO: Check differences.

                    if i_diff:
                        i_dict = {}
                        IPTableChain.objects.create(**i_dict)
                except IPTableChain.DoesNotExist:
                    print 'inserting IP TABLE CHAIN'
                    #print chain
                    i_dict = {'table': ipt_table,
                              'name': chain['name'],
                              'policy': chain['policy'],
                              'packets': chain['packets'],
                              'bytes': chain['bytes']}
                    i_obj = IPTableChain.objects.create(**i_dict)

            for rule in v['rules']:
                try:
                    i_object = IPTableRule.objects.filter(
                        table__id=ipt_table_id, rule=rule).latest()

                    i_diff = False

                    # TODO: Check differences.

                    if i_diff:
                        i_dict = {}
                        IPTableRule.objects.create(**i_dict)

                except IPTableRule.DoesNotExist:
                    print 'inserting IP TABLE RULE'
                    #print rule
                    i_dict = {'table': ipt_table,
                              'rule': rule}
                    IPTableRule.objects.create(**i_dict)


        return True

