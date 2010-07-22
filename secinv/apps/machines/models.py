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
                     'interface__i_mac', 'interface__i_mask',
                     'sshconfig__k_parameters', 'sshconfig__v_values',
                     'apacheconfig__body', 'apacheconfig__filename',
                     'iptables__body',
                     'phpconfig__body', 'phpconfig__filename',
                     'mysqlconfig__body', 'mysqlconfig__filename']

    def __unicode__(self):
        return u'%s - %s' % (self.sys_ip, self.hostname)

    def httpd(self):
        try:
            s = Services.objects.filter(machine__id=self.id).order_by('-date_added').all()[0]
            processes = re.split(',', s.k_processes)
            return 'httpd' in processes
        except IndexError:
            return False

    def mysqld(self):
        try:
            s = Services.objects.filter(machine__id=self.id).order_by('-date_added').all()[0]
            processes = re.split(',', s.k_processes)
            return 'mysqld' in processes
        except IndexError:
            return False

    def openvpn(self):
        try:
            s = Services.objects.filter(machine__id=self.id).order_by('-date_added').all()[0]
            processes = re.split(',', s.k_processes)
            return 'openvpn' in processes
        except IndexError:
            return False

    def nfs(self):
        try:
            s = System.objects.filter(machine__id=self.id).order_by('-date_added').all()[0]
            return s.nfs
        except IndexError:
            return False

    def ip_fwd(self):
        try:
            s = System.objects.filter(machine__id=self.id).order_by('-date_added').all()[0]
            return s.ip_fwd
        except IndexError:
            return False

    def iptables(self):
        try:
            s = System.objects.filter(machine__id=self.id).order_by('-date_added').all()[0]
            return s.iptables
        except IndexError:
            return False

    def excerpt(self):
        excerpt = ''

        try:
            i = Interface.objects.filter(machine__id=self.id).order_by('-date_added').all()[0]
        except IndexError:
            i = None

        try:
            sys = System.objects.filter(machine__id=self.id).order_by('-date_added').all()[0]
        except IndexError:
            sys = None

        try:
            serv = Services.objects.filter(machine__id=self.id).order_by('-date_added').all()[0]
        except IndexError:
            serv = None

        try:
            r = RPMs.objects.filter(machine__id=self.id).order_by('-date_added').all()[0]
        except IndexError:
            r = None

        try:
            ipt = IPTables.objects.filter(machine__id=self.id).order_by('-date_added').all()[0]
        except IndexError:
            ipt = None

        try:
            sc = SSHConfig.objects.filter(machine__id=self.id).order_by('-date_added').all()[0]
        except IndexError:
            sc = None

        try:
            ac = ApacheConfig.objects.filter(machine__id=self.id).order_by('-date_added').all()
        except IndexError:
            ac = None

        try:
            pc = PHPConfig.objects.filter(machine__id=self.id).order_by('-date_added').all()[0]
        except IndexError:
            pc = None

        try:
            mc = MySQLConfig.objects.filter(machine__id=self.id).order_by('-date_added').all()[0]
        except IndexError:
            mc = None

        for sf in self.search_fields:
            val = ''

            if not '__' in sf:
                val = self.__getattribute__(sf)
            elif i and 'interface__' in sf:
                val = i.__getattribute__(re.split('__', sf)[1])
            elif sys and 'system__' in sf:
                val = sys.__getattribute__(re.split('__', sf)[1])
            elif serv and 'services__' in sf:
                val = serv.__getattribute__(re.split('__', sf)[1])
            elif r and 'rpms__' in sf:
                val = r.__getattribute__(re.split('__', sf)[1])
            elif ipt and 'iptables__' in sf:
                val = ipt.__getattribute__(re.split('__', sf)[1])
            elif sc and 'sshconfig__' in sf:
                val = sc.__getattribute__(re.split('__', sf)[1])
            elif ac and 'apacheconfig__' in sf:
                #if type(ac) is list:
                #    for o in ac:
                #        val += '%s ' % o.__getattribute__(re.split('__', sf)[1])
                #else:
                #    val = ac.__getattribute__(re.split('__', sf)[1])
                #val = ac[1].__getattribute__(re.split('__', sf)[1])
                val = ' '.join([o.__getattribute__(re.split('__', sf)[1]) for o in ac])
            elif pc and 'phpconfig__' in sf:
                val = pc.__getattribute__(re.split('__', sf)[1])
            elif mc and 'mysqlconfig__' in sf:
                val = mc.__getattribute__(re.split('__', sf)[1])

            excerpt += '%s ' % val

        return excerpt

    @property
    def slug(self):
        return re.sub('[^a-z0-9A-Z-]', '-', self.hostname)

if not reversion.is_registered(Machine):
    reversion.register(Machine, fields=['sys_ip', 'hostname', 'ext_ip'])
    #reversion.register(Machine)


class AuthToken(models.Model):
    token = models.CharField(_('authorization token'), blank=True,
                             null=True, max_length=255)
    active = models.BooleanField(_('active'), default=1)
    date_added = models.DateTimeField(_('date added'),
                                      default=datetime.datetime.now)

    def __unicode__(self):
        return u'%s' % (self.token)

    class Meta:
        verbose_name = _('Authorization Token')
        verbose_name_plural = _('Authorization Tokens')
        get_latest_by = 'date_added'


class Interface(models.Model):
    machine = models.ForeignKey('Machine')
    i_name = models.CharField(_('interface name'), max_length=50)
    i_ip = models.IPAddressField(_('IP address'), blank=True, null=True)
    #i_mac = models.CharField(_('MAC address'), max_length=17, blank=True, null=True)
    i_mac = models.CharField(_('MAC address'), max_length=255, blank=True, null=True)
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
            i_diff = {'diff': ''}

        return i_diff

    class Meta:
        verbose_name = _('Interface')
        verbose_name_plural = _('Interfaces')
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
            s_diff = {'fields': ['kernel_rel'],
                      'diff': {'kernel_rel': ''},
                      'timestamp': '',
                      'version': ''}


        return s_diff

    class Meta:
        verbose_name = _('System')
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
        verbose_name = _('Services')
        verbose_name_plural = _('Services')
        get_latest_by = 'date_added'

if not reversion.is_registered(Services):
    reversion.register(Services)


class SSHConfig(models.Model):
    machine = models.ForeignKey('Machine')
    body = CompressedTextField(_('contents'), blank=True, null=True)
    filename = models.CharField(_('filename'), max_length=255, blank=True,
                                null=True)
    items = SerializedTextField(_('items'), blank=True, null=True)
    active = models.BooleanField(_('status'), default=1)
    date_added = models.DateTimeField(_('date added'),
                                      default=datetime.datetime.now)
    '''
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
        except SSHConfig.DoesNotExist:
            pass

        return s_diff
    '''

    def __unicode__(self):
        return u'%s - %s' % (self.machine.hostname, self.filename)

    #def __unicode__(self):
    #    return u'%s - %s' % (self.k_parameters, self.v_values)

    class Meta:
        verbose_name = _('SSH Configuration')
        verbose_name_plural = _('SSH Configuration')
        get_latest_by = 'date_added'

if not reversion.is_registered(SSHConfig):
    reversion.register(SSHConfig)


class ApacheConfig(models.Model):
    machine = models.ForeignKey('Machine')

    # TODO: Store as SerializedTextField.
    body = CompressedTextField(_('contents'), blank=True, null=True)
    #body = SerializedTextField(_('contents'), blank=True, null=True)
    #body = SerializedTextField()
#    body = SerializedTextField(blank=True, null=True)

    filename = models.CharField(_('filename'), max_length=255, blank=True,
                                null=True)

    directives = SerializedTextField()
    domains = SerializedTextField()

    # Do not use a ManyToManyField or ForeignKey field, since we may not have
    # objects for the included Apache config files (since the files themselves
    # may be unreadable).
    included = SerializedTextField()

#    included = models.ManyToManyField('ApacheConfig')

    active = models.BooleanField(_('status'), default=1)

    date_added = models.DateTimeField(_('date added'),
                                      default=datetime.datetime.now)

#    def __unicode__(self):
#        return u'%s' % self.body[0:100]

    def __unicode__(self):
        fn = self.filename
        if re.search('/', self.filename):
            fn = re.split('/', self.filename)[-1]
        return u'%s' % fn

    @models.permalink
    def get_absolute_url(self):
        return ('apacheconfig', (), {'machine_slug': self.machine.hostname,
                                     'ac_id': str(self.id)})

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
        verbose_name = _('Apache Configuration')
        verbose_name_plural = _('Apache Configuration')
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


class IPTables(models.Model):
    machine = models.ForeignKey('Machine')
    body = models.TextField(_('iptables policies and rules'), blank=True,
                            null=True)
    active = models.BooleanField(_('iptables status'), default=0)
    date_added = models.DateTimeField(_('date added'),
                                      default=datetime.datetime.now)

    def __unicode__(self):
        return u'%s' % self.body[0:100]

    class Meta:
        verbose_name = _('iptables')
        verbose_name_plural = _('iptables')
        get_latest_by = 'date_added'

if not reversion.is_registered(IPTables):
    reversion.register(IPTables)


class PHPConfig(models.Model):
    machine = models.ForeignKey('Machine')
    body = CompressedTextField(_('contents'), blank=True, null=True)
    filename = models.CharField(_('filename'), max_length=255, blank=True,
                                null=True)
    items = SerializedTextField(_('items'), blank=True, null=True)
    active = models.BooleanField(_('status'), default=1)

    date_added = models.DateTimeField(_('date added'),
                                      default=datetime.datetime.now)

    def __unicode__(self):
        return u'%s - %s' % (self.filename, self.body[0:50])

    @models.permalink
    def get_absolute_url(self):
        return ('phpconfig', (), {'machine_slug': self.machine.hostname,
                                  'phpconfig_id': str(self.id)})

    class Meta:
        verbose_name = _('PHP Configuration')
        verbose_name_plural = _('PHP Configuration')
        get_latest_by = 'date_added'

if not reversion.is_registered(PHPConfig):
    reversion.register(PHPConfig)


class MySQLConfig(models.Model):
    machine = models.ForeignKey('Machine')
    body = CompressedTextField(_('contents'), blank=True, null=True)
    filename = models.CharField(_('filename'), max_length=255, blank=True,
                                null=True)
    items = SerializedTextField(_('items'), blank=True, null=True)
    active = models.BooleanField(_('status'), default=1)

    date_added = models.DateTimeField(_('date added'),
                                      default=datetime.datetime.now)

    def __unicode__(self):
        return u'%s - %s' % (self.filename, self.body[0:50])

    @models.permalink
    def get_absolute_url(self):
        return ('mysqlconfig', (), {'machine_slug': self.machine.hostname,
                                    'mysql_id': str(self.id)})

    class Meta:
        verbose_name = _('MySQL Configuration')
        verbose_name_plural = _('MySQL Configuration')
        get_latest_by = 'date_added'

if not reversion.is_registered(MySQLConfig):
    reversion.register(MySQLConfig)

