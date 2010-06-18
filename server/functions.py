#!/usr/bin/env python26

from __future__ import with_statement

import datetime
import os
import sys


def diff_list(l_old, l_new):
    """Creates a new dictionary representing a difference between two lists."""
    set_old, set_new = set(l_old), set(l_new)
    intersect = set_new.intersection(set_old)

    added = list(set_new - intersect)
    removed = list(set_old - intersect)

    return {'added': added, 'removed': removed}


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
#                                 SSHConfig, IPTable, IPTableChain, IPTableRules,
#                                 IPTableInfo, ApacheConfig


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

        #try:
        #    a = AuthKey.objects.filter(machine=self.machine)

        self.is_authenticated = True
        return True

    def machine(self, ip_dict, system_dict, services_dict, rpms_dict,
                sshconfig_dict, ipt_dict, acl_list):
        if not self.is_authenticated:
            return False

        # Get the machine IP address as the first ethernet interface.
        for interface in ip_dict.keys():
            if interface[0:3] == 'eth':
                self.machine_ip = ip_dict[interface]['i_ip']
                break

        ## Machine.
        try:
            m_objs = Machine.objects.filter(sys_ip=self.machine_ip).all()
            if m_objs.exists():
                m_obj = m_objs[0]
            else:
                # Find machine by hostname if it cannot be found by IP address.
                m_obj = Machine.objects.filter(
                    hostname=system_dict['hostname']).all()[0]

            m_obj.date_scanned = datetime.datetime.now()

            m_diff = False

            if m_obj.sys_ip != self.machine_ip:
                m_obj.sys_ip = self.machine_ip
                m_diff = True

            if m_obj.hostname != system_dict['hostname']:
                m_obj.hostname = system_dict['hostname']
                m_diff = True

            if m_diff:
                m_obj.date_modified = datetime.datetime.now()

                # To update `sys_ip` and `hostname`.
                with reversion.revision:
                    m_obj.save()
            else:
                # To update `date_scanned`.
                m_obj.save()

            self.machine_obj = m_obj
            self.machine_id = self.machine_obj.id

        except IndexError:
            # Add machine if not in table.
            m_new = Machine.objects.create(sys_ip=self.machine_ip,
                hostname=system_dict['hostname'],
                date_scanned=datetime.datetime.now())
            with reversion.revision:
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

                if i_object.i_ip != ip_dict[interface]['i_ip'] or \
                   i_object.i_mac != ip_dict[interface]['i_mac'] or \
                   i_object.i_mask != ip_dict[interface]['i_mask'] or \
                   not i_object.active:

                    i_object.machine = self.machine_obj
                    i_object.i_name = interface
                    i_object.i_ip = ip_dict[interface]['i_ip']
                    i_object.i_mac = ip_dict[interface]['i_mac']
                    i_object.i_mask = ip_dict[interface]['i_mask']
                    i_object.active = True
                    i_object.date_added = datetime.datetime.now()
                    with reversion.revision:
                        i_object.save()

            except Interface.DoesNotExist:
                i_new = Interface.objects.create(machine=self.machine_obj,
                    i_name=interface,
                    i_ip=ip_dict[interface]['i_ip'],
                    i_mac=ip_dict[interface]['i_mac'],
                    i_mask=ip_dict[interface]['i_mask'])
                with reversion.revision:
                    i_new.save()

        # Get latest interfaces (select by distinct interface name).
        distinct_interfaces = Interface.objects.filter(
            machine__id=self.machine_id, active=True).values_list(
            'i_name', flat=True).distinct()

        i_diff = diff_list(distinct_interfaces, ip_dict.keys())

        # Update each deactivated interface as inactive.
        for i in i_diff['removed']:
            try:
                i_latest = Interface.objects.filter(machine__id=self.machine_id,
                                                    i_name=i, active=True).latest()
            except Interface.DoesNotExist:
                continue

            i_latest.active = False
            with reversion.revision:
                i_latest.save()


        ## System.
        try:
            sys_object = System.objects.filter(
                machine__id=self.machine_id).latest()

            if sys_object.kernel_rel != system_dict['kernel_rel'] or \
               sys_object.rh_rel != system_dict['rh_rel'] or \
               sys_object.nfs != system_dict['nfs'] or \
               sys_object.ip_fwd != system_dict['ip_fwd'] or \
               sys_object.iptables != ipt_dict['status']:

                sys_object.machine = self.machine_obj
                sys_object.kernel_rel = system_dict['kernel_rel']
                sys_object.rh_rel = system_dict['rh_rel']
                sys_object.nfs = system_dict['nfs']
                sys_object.ip_fwd = system_dict['ip_fwd']
                sys_object.iptables = ipt_dict['status']
                sys_object.date_added = datetime.datetime.now()
                with reversion.revision:
                    sys_object.save()

        except System.DoesNotExist:
            sys_object = System.objects.create(machine=self.machine_obj,
                kernel_rel=system_dict['kernel_rel'],
                rh_rel=system_dict['rh_rel'],
                nfs=system_dict['nfs'],
                ip_fwd=system_dict['ip_fwd'],
                iptables=ipt_dict['status'])
            with reversion.revision:
                sys_object.save()


        ## Services.
        procs = services_dict.keys()
        csv_procs = ','.join(procs)
        ports = services_dict.values()
        csv_ports = ','.join(ports)

        try:
            s_object = Services.objects.filter(
                machine__id=self.machine_id).latest()

            if s_object.k_processes != csv_procs or \
               s_object.v_ports != csv_ports:

                s_object.machine = self.machine_obj
                s_object.k_processes = csv_procs
                s_object.v_ports = csv_ports
                s_object.date_added = datetime.datetime.now()
                with reversion.revision:
                    s_object.save()

                #s_dict = {'machine': self.machine_obj,
                #          'processes': csv_procs,
                #          'ports': csv_ports}
                #s_object = Services.objects.create(**s_dict)

        except Services.DoesNotExist:
            #s_dict = {'machine': self.machine_obj,
            #          'k_processes': csv_procs,
            #          'v_ports': csv_ports}
            #s_object = Services.objects.create(**s_dict)
            sys_object = Services.objects.create(machine=self.machine_obj,
                                                 k_processes=csv_procs,
                                                 v_ports=csv_ports)
            with reversion.revision:
                sys_object.save()


        ## RPMs.
        try:
            r_object = RPMs.objects.filter(machine__id=self.machine_id).latest()

            # TODO: Change rpms_dict.

            if r_object.v_rpms != rpms_dict['list']:
                r_object.machine = self.machine_obj
                r_object.v_rpms = rpms_dict['list']
                r_object.date_added = datetime.datetime.now()
                with reversion.revision:
                    r_object.save()

        except RPMs.DoesNotExist:
            r_object = RPMs.objects.create(machine=self.machine_obj,
                                           v_rpms=rpms_dict['list'])
            with reversion.revision:
                r_object.save()


        ## Apache configuration files.

        #
        # TODO: Mark deleted .conf files as `inactive`.
        # Add `active` field, a la Interfaces.
        #

        for ac in acl_list:
            try:
                a_object = ApacheConfig.objects.get(
                    machine__id=self.machine_id, filename=ac['filename'])

                if a_object.body != ac['body'] or \
                   a_object.directives != ac['directives'] or \
                   a_object.domains != ac['domains'] or \
                   a_object.included != ac['included']:

                    a_object.body = ac['body']
                    a_object.directives = ac['directives']
                    a_object.domains = ac['domains']
                    a_object.included = ac['included']
                    a_object.date_added = datetime.datetime.now()
                    with reversion.revision:
                        a_object.save()

            except ApacheConfig.DoesNotExist:
                a_object = ApacheConfig.objects.create(machine=self.machine_obj,
                    body=ac['body'], filename=ac['filename'],
                    directives=ac['directives'], domains=ac['domains'],
                    included=ac['included'])
                with reversion.revision:
                    a_object.save()


        ## SSH configuration file.
        params = sshconfig_dict.keys()
        csv_params = '\n'.join(params)
        values = sshconfig_dict.values()
        csv_values = '\n'.join(values)

        try:
            s_object = SSHConfig.objects.filter(
                machine__id=self.machine_id).latest()

            if s_object.k_parameters != csv_params or \
               s_object.v_values != csv_values:

                s_object.machine = self.machine_obj
                s_object.k_parameters = csv_params
                s_object.v_values = csv_values
                s_object.date_added = datetime.datetime.now()
                with reversion.revision:
                    s_object.save()

        except SSHConfig.DoesNotExist:
            s_object = SSHConfig.objects.create(machine=self.machine_obj,
                                                k_parameters=csv_params,
                                                v_values=csv_values)
            with reversion.revision:
                s_object.save()


        ## iptables.
        #print 'Received iptables dictionary:\n'
        iptables_rules = ipt_dict['rules']
        iptables_body = ipt_dict['rules']['body']
        iptables_status = ipt_dict['status']
        #print iptables_rules

        try:
            i_object = IPTableInfo.objects.filter(
                machine__id=self.machine_id).latest()

            if i_object.body != iptables_body or \
               i_object.active != iptables_status:
                i_object.machine = self.machine_obj
                i_object.body = iptables_body
                i_object.active = iptables_status
                i_object.date_added = datetime.datetime.now()
                with reversion.revision:
                    i_object.save()

        except IPTableInfo.DoesNotExist:
            i_object = IPTableInfo.objects.create(machine=self.machine_obj,
                                                  body=iptables_body,
                                                  active=iptables_status)
            with reversion.revision:
                i_object.save()


        '''
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
                    i_dict = {'table': ipt_table,
                              'rule': rule}
                    IPTableRule.objects.create(**i_dict)
        '''

        return True

