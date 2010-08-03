#!/usr/bin/env python26

from __future__ import with_statement

import datetime
import os
import sys

def all_zeros(txt):
    return txt and not int(float.fromhex(
        str(txt).strip().replace(':', '').replace('-', ''))) or False


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

# To suppress MySQLdb warnings.
import warnings
warnings.filterwarnings('ignore')

from django.core.management import setup_environ
setup_environ(settings)

import reversion

from apps.machines.models import (Machine, Services, System, RPMs, Interface,
                                  SSHConfig, IPTables, ApacheConfig,
                                  PHPConfig, MySQLConfig, AuthToken)


class ServerFunctions:
    def __init__(self):
        self.machine_ip = '0.0.0.0'
        self.machine_id = 0
        self.is_authenticated = False

        # Create logger.
        #self.logger = logging.getLogger('secinv')

    def authenticate(self, auth_token):
        """
        Check if client's authorization token is valid.
        """
        try:
            s = AuthToken.objects.get(token=auth_token, active=True)
            if s:
                self.is_authenticated = True
        except AuthToken.DoesNotExist:
            pass

        return self.is_authenticated

    def machine(self, ip_dict, system_dict, services_dict, rpms_dict,
                sshconfig_dict, ipt_dict, acl_list, phpini_dict, mycnf_dict):
        if not self.is_authenticated:
            return False
        # Get the machine IP address as the first ethernet interface.
        '''
        for interface in ip_dict.keys():
            if interface[0:3] == 'eth':
                self.machine_ip = i_dict['i_ip']
                break
        '''
        self.machine_ip = system_dict['sys_ip']

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
        for interface, i_dict in ip_dict.iteritems():
            # Clean up a null MAC address.
            if all_zeros(i_dict['i_mac']):
                i_dict['i_mac'] = ''

            # If all fields are empty, then device is inactive -- so do not
            # insert a row.
            if not i_dict['i_ip'] and not i_dict['i_mac'] and \
               not i_dict['i_mask']:
                continue

            # If interface already exists in table, update accordingly.
            try:
                i_object = Interface.objects.filter(
                    machine__id=self.machine_id, i_name=interface).latest()

                if i_object.i_ip != i_dict['i_ip'] or \
                   i_object.i_mac != i_dict['i_mac'] or \
                   i_object.i_mask != i_dict['i_mask'] or \
                   not i_object.active:

                    i_object.machine = self.machine_obj
                    i_object.i_name = interface
                    i_object.i_ip = i_dict['i_ip']
                    i_object.i_mac = i_dict['i_mac']
                    i_object.i_mask = i_dict['i_mask']
                    i_object.active = True
                    i_object.date_added = datetime.datetime.now()
                    with reversion.revision:
                        i_object.save()

            except Interface.DoesNotExist:
                i_object = Interface.objects.create(machine=self.machine_obj,
                                                    i_name=interface,
                                                    i_ip=i_dict['i_ip'],
                                                    i_mac=i_dict['i_mac'],
                                                    i_mask=i_dict['i_mask'])
                with reversion.revision:
                    i_object.save()

        # Get latest interfaces (select by distinct interface name).
        distinct_interfaces = Interface.objects.filter(
            machine__id=self.machine_id, active=True).values_list(
            'i_name', flat=True).distinct()

        i_diff = diff_list(distinct_interfaces, ip_dict.keys())

        # Update each deactivated interface as inactive.
        for i in i_diff['removed']:
            try:
                i_latest = Interface.objects.filter(
                    machine__id=self.machine_id,
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
 
        except Services.DoesNotExist:
            sys_object = Services.objects.create(machine=self.machine_obj,
                                                 k_processes=csv_procs,
                                                 v_ports=csv_ports)
            with reversion.revision:
                sys_object.save()


        ## RPMs.
        try:
            r_object = RPMs.objects.filter(
                machine__id=self.machine_id).latest()

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


        ## SSH Configuration file.
        try:
            s_object = SSHConfig.objects.get(machine__id=self.machine_id)
            #print 'SSH Config exists ...'
            if s_object.body != sshconfig_dict['body'] or \
               s_object.items != sshconfig_dict['items'] or \
               s_object.filename != sshconfig_dict['filename']:

                s_object.body = sshconfig_dict['body']
                s_object.items = sshconfig_dict['items']
                s_object.filename = sshconfig_dict['filename']
                with reversion.revision:
                    s_object.save()

                #print 'Updating SSH Config ...'
        except SSHConfig.DoesNotExist:
            s_object = SSHConfig.objects.create(machine=self.machine_obj,
                body=sshconfig_dict['body'], items=sshconfig_dict['items'],
                filename=sshconfig_dict['filename'])
            with reversion.revision:
                s_object.save()
            #print 'Adding SSH Config ...'


        ## iptables.
        iptables_rules = ipt_dict['rules']
        iptables_body = ipt_dict['rules']['body']
        iptables_status = ipt_dict['status']

        try:
            i_object = IPTables.objects.filter(
                machine__id=self.machine_id).latest()

            if i_object.body != iptables_body or \
               i_object.active != iptables_status:
                i_object.machine = self.machine_obj
                i_object.body = iptables_body
                i_object.active = iptables_status
                i_object.date_added = datetime.datetime.now()
                with reversion.revision:
                    i_object.save()

        except IPTables.DoesNotExist:
            i_object = IPTables.objects.create(machine=self.machine_obj,
                                               body=iptables_body,
                                               active=iptables_status)
            with reversion.revision:
                i_object.save()


        ## Apache Configuration files.
        acl_filenames = []

        for ac in acl_list:
            try:
                a_object = ApacheConfig.objects.get(
                    machine__id=self.machine_id, filename=ac['filename'])
                #print 'AC %s Exists ...' % ac['filename']
                if a_object.body != ac['body'] or \
                   a_object.directives != ac['directives'] or \
                   a_object.domains != ac['domains'] or \
                   a_object.included != ac['included']:

                    a_object.body = ac['body']
                    a_object.directives = ac['directives']
                    a_object.domains = ac['domains']
                    a_object.included = ac['included']
                    a_object.active = True
                    a_object.date_added = datetime.datetime.now()
                    with reversion.revision:
                        a_object.save()
                    #print 'Updating AC %s ...' % ac['filename']
                elif not a_object.active:
                    a_object.active = True
                    with reversion.revision:
                        a_object.save()
                    #print 'Activating AC %s ...' % ac['filename']

            except ApacheConfig.DoesNotExist:
                a_object = ApacheConfig.objects.create(
                    machine=self.machine_obj,
                    body=ac['body'], filename=ac['filename'],
                    directives=ac['directives'], domains=ac['domains'],
                    included=ac['included'])
                with reversion.revision:
                    a_object.save()
                #print 'Adding AC % ...' % ac['filename']

            acl_filenames.append(ac['filename'])

        # Get latest Apache Config files (select by distinct filename).
        distinct_acs = ApacheConfig.objects.filter(
            machine__id=self.machine_id, active=True).values_list(
            'filename', flat=True).distinct()

        a_diff = diff_list(distinct_acs, acl_filenames)

        # Update each deactivated Apache Config as inactive.
        for a in a_diff['removed']:
            try:
                a_latest = ApacheConfig.objects.filter(
                    machine__id=self.machine_id,
                    filename=a, active=True).latest()
            except ApacheConfig.DoesNotExist:
                continue

            a_latest.active = False
            with reversion.revision:
                a_latest.save()


        ## PHP Configuration files.
        if phpini_dict['filename']:
            try:
                p_object = PHPConfig.objects.get(machine__id=self.machine_id)
                #print 'PHP Config exists ...'
                if p_object.body != phpini_dict['body'] or \
                   p_object.items != phpini_dict['items'] or \
                   p_object.filename != phpini_dict['filename']:
    
                    p_object.body = phpini_dict['body']
                    p_object.items = phpini_dict['items']
                    p_object.filename = phpini_dict['filename']
                    p_object.date_added = datetime.datetime.now()
                    with reversion.revision:
                        p_object.save()
    
                    #print 'Updating PHP Config ...'
            except PHPConfig.DoesNotExist:
                p_object = PHPConfig.objects.create(machine=self.machine_obj,
                    body=phpini_dict['body'], items=phpini_dict['items'],
                    filename=phpini_dict['filename'])
                with reversion.revision:
                    p_object.save()
                #print 'Adding PHP Config ...'


        ## MySQL Configuration files.
        try:
            m_object = MySQLConfig.objects.get(machine__id=self.machine_id)
            #print 'MySQL Config exists ...'
            if m_object.body != mycnf_dict['body'] or \
               m_object.items != mycnf_dict['items'] or \
               m_object.filename != mycnf_dict['filename']:

                m_object.body = mycnf_dict['body']
                m_object.items = mycnf_dict['items']
                m_object.filename = mycnf_dict['filename']
                with reversion.revision:
                    m_object.save()

                #print 'Updating MySQL Config ...'
        except MySQLConfig.DoesNotExist:
            m_object = MySQLConfig.objects.create(machine=self.machine_obj,
                body=mycnf_dict['body'], items=mycnf_dict['items'],
                filename=mycnf_dict['filename'])
            with reversion.revision:
                m_object.save()
            #print 'Adding MySQL Config ...'

        return True
