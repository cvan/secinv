from django.db import models
from django.utils.translation import ugettext_lazy as _
#from ..fulltext.search import SearchManager
from ..fields import *
from .utils import diff_list, diff_dict, get_version_diff
from reversion.models import Version

import datetime
import re
import reversion


class Machine(models.Model):
    sys_ip = models.IPAddressField(_('IP address'))
    hostname = models.CharField(max_length=255)
    ext_ip = models.IPAddressField(_('external IP address'), blank=True, null=True)
    date_added = models.DateTimeField(_('date added'), editable=False,
                                      default=datetime.datetime.now)
    date_modified = models.DateTimeField(_('date modified'),
                                        default=datetime.datetime.now)
    date_scanned = models.DateTimeField(_('date scanned'))

    # TODO: DRY. Keep in one place.
    search_fields = ['sys_ip', 'hostname', 'ext_ip',
                     'system__kernel_rel', 'system__rh_rel', 'system__nfs',
                     'system__ip_fwd', 'system__iptables',
                     'services__k_processes', 'services__v_ports',
                     'rpms__v_rpms',
                     'interface__i_name', 'interface__i_ip',
                     'interface__i_mac', 'interface__i_mask']

    def __unicode__(self):
        return u'%s - %s' % (self.sys_ip, self.hostname)

    def httpd(self):
        s = Services.objects.filter(machine__id=self.id).order_by('-date_added').all()[0]
        processes = re.split(',', s.k_processes)
        return 'httpd' in processes

    def mysqld(self):
        s = Services.objects.filter(machine__id=self.id).order_by('-date_added').all()[0]
        processes = re.split(',', s.k_processes)
        return 'mysqld' in processes

    def openvpn(self):
        s = Services.objects.filter(machine__id=self.id).order_by('-date_added').all()[0]
        processes = re.split(',', s.k_processes)
        return 'openvpn' in processes

    def nfs(self):
        s = System.objects.filter(machine__id=self.id).order_by('-date_added').all()[0]
        return s.nfs

    def ip_fwd(self):
        s = System.objects.filter(machine__id=self.id).order_by('-date_added').all()[0]
        return s.ip_fwd

    def iptables(self):
        s = System.objects.filter(machine__id=self.id).order_by('-date_added').all()[0]
        return s.iptables

    def excerpt(self):
        excerpt = ''

        i = Interface.objects.filter(machine__id=self.id).order_by('-date_added').all()[0]
        sys = System.objects.filter(machine__id=self.id).order_by('-date_added').all()[0]
        serv = Services.objects.filter(machine__id=self.id).order_by('-date_added').all()[0]
        r = RPMs.objects.filter(machine__id=self.id).order_by('-date_added').all()[0]

        for sf in self.search_fields:
            if not re.search('__', sf):
                val = self.__getattribute__(sf)
            elif re.search('interface__', sf):
                val = i.__getattribute__(re.split('__', sf)[1])
            elif re.search('system__', sf):
                val = sys.__getattribute__(re.split('__', sf)[1])
            elif re.search('services__', sf):
                val = serv.__getattribute__(re.split('__', sf)[1])
            elif re.search('rpms__', sf):
                val = r.__getattribute__(re.split('__', sf)[1])

            excerpt += '%s ' % val

        return excerpt

    @property
    def slug(self):
        return re.sub('[^a-z0-9A-Z-]', '-', self.hostname)

if not reversion.is_registered(Machine):
    reversion.register(Machine, fields=['sys_ip', 'hostname', 'ext_ip'])
    #reversion.register(Machine)


class Interface(models.Model):
    machine = models.ForeignKey('Machine')
    i_name = models.CharField(_('interface name'), max_length=50)
    i_ip = models.IPAddressField(_('IP address'), blank=True, null=True)
    i_mac = models.CharField(_('MAC address'), max_length=17, blank=True, null=True)
    i_mask = models.IPAddressField(_('netmask'), blank=True, null=True)
    active = models.BooleanField(_('active'), default=1)
    date_added = models.DateTimeField(_('date added'),
                                      default=datetime.datetime.now)

    def __unicode__(self):
        return u'%s - %s - %s - %s' % (self.i_name, self.i_ip, self.i_mac,
                                       self.i_mask)

    def version_changes(self):
        """
        Create a dictionary of the differences between the current and previous
        interface of the same interface name.
        """
        i_diff = {}

        try:
            i_latest = Interface.objects.filter(machine__id=self.machine_id,
                i_name=self.i_name).latest()
            i_v = get_version_diff(i_latest)
            if i_v:
                i_diff = i_v[0]
        except Interface.DoesNotExist:
            pass

        return i_diff

    class Meta:
        get_latest_by = 'date_added'

if not reversion.is_registered(Interface):
    reversion.register(Interface)


class System(models.Model):
    machine = models.ForeignKey('Machine')
    kernel_rel = models.CharField(_('kernel release'), max_length=255,
                                  blank=True, null=True)
    rh_rel = models.CharField(_('RedHat release'), max_length=255,
                              blank=True, null=True)
    nfs = models.BooleanField(_('NFS?'), default=0)
    ip_fwd = models.BooleanField(_('IP forwarding'), default=0)
    iptables = models.BooleanField(_('iptables'), default=0)
    date_added = models.DateTimeField(_('date added'),
                                      default=datetime.datetime.now)

    def __unicode__(self):
        return u'%s - %s - %s - %s - %s' % (self.kernel_rel, self.rh_rel,
                                            self.nfs, self.ip_fwd, self.iptables)

    def version_changes(self):
        """
        Create a dictionary of the differences between the current and previous
        entry of the system info.
        """
        i_diff = {}

        try:
            s_latest = System.objects.filter(
                machine__id=self.machine_id).latest()
            s_v = get_version_diff(s_latest)
            if s_v:
                s_diff = s_v[0]
        except System.DoesNotExist:
            pass

        return s_diff

    class Meta:
        verbose_name_plural = _('System')
        get_latest_by = 'date_added'

if not reversion.is_registered(System):
    reversion.register(System)


class Services(models.Model):
    machine = models.ForeignKey('Machine')
    # TODO: Use TextFields.
    k_processes = models.CharField(_('processes'), max_length=255, blank=True,
                                   null=True)
    v_ports = models.CommaSeparatedIntegerField(_('ports'), max_length=255,
                                                blank=True, null=True)
    date_added = models.DateTimeField(_('date added'),
                                      default=datetime.datetime.now)

    def version_changes(self):
        """
        Create a dictionary of the differences between the current and previous
        services entries.
        """
        s_diff = {}

        try:
            s_latest = Services.objects.get(machine__id=self.machine_id)
            s_v = get_version_diff(s_latest, ',')
            if s_v:
                s_diff = s_v[0]
        except Services.DoesNotExist:
            pass

        return s_diff

    def __unicode__(self):
        return u'%s - %s' % (self.k_processes, self.v_ports)

    class Meta:
        verbose_name_plural = _('Services')
        get_latest_by = 'date_added'

if not reversion.is_registered(Services):
    reversion.register(Services)


class SSHConfig(models.Model):
    machine = models.ForeignKey('Machine')
    k_parameters = models.TextField(_('parameters'), blank=True, null=True)
    v_values = models.TextField(_('values'), blank=True, null=True)
    date_added = models.DateTimeField(_('date added'),
                                      default=datetime.datetime.now)

    def version_changes(self):
        """
        Create a dictionary of the differences between the current and previous
        SSH configuration entries.
        """
        s_diff = {}

        try:
            s_latest = SSHConfig.objects.get(machine__id=self.machine_id)
            s_v = get_version_diff(s_latest, '\n')
            if s_v:
                s_diff = s_v[0]
            else:
                s_diff = {'empty': 'itis'}
        except SSHConfig.DoesNotExist:
            pass

        return s_diff

    def __unicode__(self):
        return u'%s - %s' % (self.k_parameters, self.v_values)

    class Meta:
        verbose_name = _('SSHConfig')
        verbose_name_plural = _('SSHConfig')
        get_latest_by = 'date_added'

if not reversion.is_registered(SSHConfig):
    reversion.register(SSHConfig)


class ApacheConfig(models.Model):
    machine = models.ForeignKey('Machine')

    # TODO: Store as SerializedDataField.
    body = CompressedTextField(_('contents'), blank=True, null=True)
#    body = SerializedDataField(_('contents'), blank=True, null=True)

    filename = models.CharField(_('filename'), max_length=255, blank=True,
                                null=True)

    directives = SerializedDataField()
    domains = SerializedDataField()

    # Do not use a ManyToManyField or ForeignKey field, since we may not have
    # objects for the included Apache config files (since the files themselves
    # may be unreadable).
    included = SerializedDataField()

#    included = models.ManyToManyField('ApacheConfig')

    date_added = models.DateTimeField(_('date added'),
                                      default=datetime.datetime.now)

#    def __unicode__(self):
#        return u'%s' % self.body[0:100]

    def __unicode__(self):
        if re.search('/', self.filename):
            fn = re.split('/', self.filename)[-1]
        return u'%s' % fn

    @models.permalink
    def get_absolute_url(self):
        return ('httpd-conf', (), {'machine_slug': self.machine.hostname,
                                   'ac_id': str(self.id)})

    '''
    def get_domains(self):
        domains = {}
        for fn in self.included:
            try:
                a = ApacheConfig.objects.get(machine__id=self.machine_id,
                                             filename=fn)
                if a.domains:
                    domains = dict(domains, **a.domains)
            except ApacheConfig.DoesNotExist:
                pass
        return domains
    '''

    def get_domains(self):
        domains = []

        # Append domains defined in this config file.
        for k, v in self.domains.iteritems():
            domains.append([k, v, self])

        # Append domains defined in included config files.
        for fn in self.included:
            try:
                a = ApacheConfig.objects.get(machine__id=self.machine_id,
                                             filename=fn)
                if a.domains:
                    #domains.append( a.domains )
                    for k, v in a.domains.iteritems():
                        domains.append([k, v, a])
            except ApacheConfig.DoesNotExist:
                pass
        return domains

    class Meta:
        verbose_name = _('ApacheConfig')
        verbose_name_plural = _('ApacheConfig')
        get_latest_by = 'date_added'

if not reversion.is_registered(ApacheConfig):
    reversion.register(ApacheConfig)


class RPMs(models.Model):
    machine = models.ForeignKey('Machine')
    v_rpms = models.TextField(_('RPMs'), blank=True, null=True)
    date_added = models.DateTimeField(_('date added'),
                                      default=datetime.datetime.now)

    def version_changes(self):
        """
        Create a dictionary of the differences between the current and previous
        RPMs installed.
        """
        r_diff = {}

        try:
            r_latest = RPMs.objects.get(machine__id=self.machine_id)
            r_v = get_version_diff(s_latest, '\n')
            if r_v:
                r_diff = r_v[0]
        except RPMs.DoesNotExist:
            pass

        return r_diff

    def __unicode__(self):
        return u'%s' % self.v_rpms[0:100]

    class Meta:
        verbose_name = _('RPMs')
        verbose_name_plural = _('RPMs')
        get_latest_by = 'date_added'

if not reversion.is_registered(RPMs):
    reversion.register(RPMs)


class IPTableInfo(models.Model):
    machine = models.ForeignKey('Machine')
    body = models.TextField(_('iptables policies and rules'), blank=True,
                            null=True)
    active = models.BooleanField(_('iptables status'), default=0)
    date_added = models.DateTimeField(_('date added'),
                                      default=datetime.datetime.now)

    def __unicode__(self):
        return u'%s' % self.body[0:100]

    class Meta:
        verbose_name = _('IPTableInfo')
        verbose_name_plural = _('IPTableInfo')
        get_latest_by = 'date_added'

if not reversion.is_registered(IPTableInfo):
    reversion.register(IPTableInfo)


class IPTable(models.Model):
    machine = models.ForeignKey('Machine')
    name = models.CharField(_('name'), max_length=255)

    # TODO: `active` field.
    #active = models.BooleanField(_('active'), default=1)

    date_added = models.DateTimeField(_('date added'),
                                      default=datetime.datetime.now)

    def __unicode__(self):
        return u'%s' % (self.name)

    class Meta:
        verbose_name = _('IPTable')
        verbose_name_plural = _('IPTables')
        get_latest_by = 'date_added'

#if not reversion.is_registered(IPTable):
#    reversion.register(IPTable)


class AuthKey(models.Model):
    machine = models.ForeignKey('Machine')
    key = models.CharField(_('authorization key'), max_length=255)
    date_added = models.DateTimeField(_('date added'),
                                      default=datetime.datetime.now)

    class Meta:
        verbose_name = _('AuthKey')
        verbose_name_plural = _('AuthKeys')
        get_latest_by = 'date_added'
