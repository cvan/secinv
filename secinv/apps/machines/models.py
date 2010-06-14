from django.db import models
from django.utils.translation import ugettext_lazy as _
#from ..fulltext.search import SearchManager
import reversion

import datetime
import re

from reversion.models import Version

# TODO: Move functions.


def get_version_diff(obj_item, delimiter=None):
    obj_version = Version.objects.get_for_object(obj_item).order_by('revision')
    versions = []
    for index, ver in enumerate(obj_version):
        old_v = {}
        try:
            old_v = obj_version[index - 1].field_dict
        except AssertionError:
            old_v = {}
            #for k in ver.field_dict.keys():
            #    old_v[k] = ''
        new_v = ver.field_dict
        patch = diff_dict2(old_v, new_v, delimiter)

        new_fields = ver.field_dict
        # If there are old fields, merge the dictionaries.
        if old_v:
            new_fields = dict(old_v, **ver.field_dict)

        versions.append({'fields': new_fields, 'diff': patch,
                         'timestamp': ver.field_dict['date_added']})
    versions.reverse()
    return versions


def diff_list2(l_old, l_new):
    """Creates a new dictionary representing a difference between two lists."""
    set_old, set_new = set(l_old), set(l_new)
    intersect = set_new.intersection(set_past)

    added = list(set_new - intersect)
    removed = list(set_old - intersect)

    return {'added': added, 'removed': removed}

def diff_dict2(a, b, delimiter=None):
    """Return differences from dictionaries a to b.

    Return a tuple of three dicts: (removed, added, changed).
    'removed' has all keys and values removed from a. 'added' has
    all keys and values that were added to b. 'changed' has all
    keys and their values in b that are different from the corresponding
    key in a.
    """

    removed = dict()
    added = dict()
    changed = dict()
    unchanged = dict()

    # If inactive object is now active, mark each field as 'added'.
    if 'active' in a and a['active'] == False and 'active' in b and b['active'] == True:
        for key, value in b.iteritems():
            added[key] = value
    # If object is inactive, mark each field as 'removed'.
    elif 'active' in b and b['active'] == False:
        for key, value in b.iteritems():
            removed[key] = value
    else:
        for key, value in a.iteritems():
            if key not in b:
                removed[key] = value
            elif b[key] != value:
                changed[key] = b[key]
            elif b[key] == value:
                unchanged[key] = b[key]
        for key, value in b.iteritems():
            if key not in a:
                added[key] = value

    diffs = {'removed': removed, 'added': added, 'changed': changed,
             'unchanged': unchanged}

    # To determine the differences of key/value pairs, the key and value fields
    # are split, merged as dictionaries, and subsequently compared.

    pair = {}
    if delimiter:
        key_name = None
        value_name = None
        for key, value in b.iteritems():
            if key[:2] == 'k_' and delimiter in value:
                key_name = key
                a_pair_k = re.split(delimiter, a[key]) if key in a else []
                b_pair_k = re.split(delimiter, value)
            if key[:2] == 'v_' and delimiter in value:
                value_name = value
                a_pair_v = re.split(delimiter, a[key]) if key in a else []
                b_pair_v = re.split(delimiter, value)


        if key_name and value_name:
            a_pair_dict = dict(zip(a_pair_k, a_pair_v))
            b_pair_dict = dict(zip(b_pair_k, b_pair_v))
            pair = diff_dict2(a_pair_dict, b_pair_dict)

            # Merge previous and current dictionaries.
            b = dict(a_pair_dict, **b_pair_dict)
        elif value_name:
            pair = diff_list2(a_pair_v, b_pair_v)

            # Similarly, merge lists.
            b = list(a_pair_v, **b_pair_v)

        if value_name:
            diffs['pair'] = {'merged': b, 'diff': pair}

    return diffs


def diff_dict(d_old, d_new):
    """
    Creates a new dict representing a diff between two dicts.
    """
    # Added and changed items.
    diff = {}
    for k, v in d_new.items():
        old_v = d_old.get(k, None)
        if v == old_v:
            continue
        diff.update({k: {'old': old_v, 'new': v}})

    # Deleted items.
    for k, v in d_old.items():
        if k not in d_new.keys():
            diff.update({k: {'deleted': v}})

    return diff

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
        processes = re.split(',', s.processes)
        return 'httpd' in processes

    def mysqld(self):
        s = Services.objects.filter(machine__id=self.id).order_by('-date_added').all()[0]
        processes = re.split(',', s.processes)
        return 'mysqld' in processes

    def openvpn(self):
        s = Services.objects.filter(machine__id=self.id).order_by('-date_added').all()[0]
        processes = re.split(',', s.processes)
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

    def diff(self):
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
                                            self.nfs, self.ip_fwd,
                                            self.iptables)

    def diff(self):
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
    date_added = models.DateTimeField(_('date added'), editable=False,
                                      default=datetime.datetime.now)

    def diff(self):
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


class RPMs(models.Model):
    machine = models.ForeignKey('Machine')
    v_rpms = models.TextField(_('RPMs'), blank=True, null=True)
    date_added = models.DateTimeField(_('date added'), editable=False,
                                      default=datetime.datetime.now)

    def differences(self):
        r_older = RPMs.objects.filter(
            machine__id=self.machine_id).exclude(id=self.id).filter(
            date_added__lt=self.date_added).order_by('-date_added').all()

        r_previous = []
        if r_older:
            r_previous = re.split('\n', r_older[0].v_rpms)

        r_latest = re.split('\n', self.v_rpms)

        return diff_list(r_previous, r_latest)

    def __unicode__(self):
        return u'%s' % (self.v_rpms[0:100])

    class Meta:
        verbose_name = _('RPMs')
        verbose_name_plural = _('RPMs')
        get_latest_by = 'date_added'

if not reversion.is_registered(RPMs):
    reversion.register(RPMs)


class SSHConfig(models.Model):
    machine = models.ForeignKey('Machine')
    k_parameters = models.TextField(_('parameters'), blank=True, null=True)
    v_values = models.TextField(_('values'), blank=True, null=True)
    date_added = models.DateTimeField(_('date added'), editable=False,
                                      default=datetime.datetime.now)

    def differences(self):
        """
        Create a dictionary of the differences between the latest
        and the previous SSH configuration files.
        """
        s_older = SSHConfig.objects.filter(
            machine__id=self.machine_id).exclude(id=self.id).filter(
            date_added__lt=self.date_added).order_by('-date_added').all()

        s_previous = {}
        if s_older.exists():
            # TODO: remove carriage returns?
            s_params = re.split('\n', s_older[0].k_parameters.replace('\r', ''))
            s_values = re.split('\n', s_older[0].v_values.replace('\r', ''))
            s_previous = dict(zip(s_params, s_values))

        s_params = re.split('\n', self.k_parameters.replace('\r', ''))
        s_values = re.split('\n', self.v_values.replace('\r', ''))
        s_latest = dict(zip(s_params, s_values))

        return diff_dict(s_previous, s_latest)

    def parameters_split(self):
        return re.split('\n', self.k_parameters.replace('\r', ''))

    def values_split(self):
        return re.split('\n', self.v_values.replace('\r', ''))

    def parameters_dict(self):
        """
        Merge and return latest and previous dictionaries of parameters/values.
        """
        # TODO: merge_diff(s_older, self, fields=['parameters', 'values'], delimeter='')

        s_older = SSHConfig.objects.filter(
            machine__id=self.machine_id).exclude(id=self.id).filter(
            date_added__lt=self.date_added).order_by('-date_added').all()

        s_previous = {}
        if s_older.exists():
            s_params = re.split('\n', s_older[0].k_parameters.replace('\r', ''))
            s_values = re.split('\n', s_older[0].v_values.replace('\r', ''))
            s_previous = dict(zip(s_params, s_values))

        s_params = re.split('\n', self.k_parameters.replace('\r', ''))
        s_values = re.split('\n', self.v_values.replace('\r', ''))
        s_latest = dict(zip(s_params, s_values))

        return dict(s_latest, **s_previous)

    def __unicode__(self):
        return u'%s - %s' % (self.k_parameters, self.v_values)

    class Meta:
        verbose_name = _('SSHConfig')
        verbose_name_plural = _('SSHConfig')
        get_latest_by = 'date_added'

#if not reversion.is_registered(SSHConfig):
#    reversion.register(SSHConfig)

'''
class ApacheConfig(models.Model):
    machine = models.ForeignKey('Machine')
    parameters = models.TextField(blank=True, null=True)
    values = models.TextField(blank=True, null=True)
    date_added = models.DateTimeField(_('date added'), editable=False,
                                      default=datetime.datetime.now)
'''


class IPTable(models.Model):
    machine = models.ForeignKey('Machine')
    name = models.TextField(_('name'), max_length=255)
    #active = models.BooleanField(_('active'), default=1)
    date_added = models.DateTimeField(_('date added'), editable=False,
                                      default=datetime.datetime.now)

    def __unicode__(self):
        return u'%s' % (self.name)

    class Meta:
        verbose_name = _('IPTable')
        verbose_name_plural = _('IPTables')
        get_latest_by = 'date_added'

#if not reversion.is_registered(IPTable):
#    reversion.register(IPTable)


class IPTableChain(models.Model):
    table = models.ForeignKey('IPTable')
    name = models.CharField(_('chain name'), max_length=255)
    policy = models.TextField(_('chain policy'), max_length=255, blank=True, null=True)
    packets = models.BigIntegerField(_('packets counter'))
    bytes = models.BigIntegerField(_('bytes counter'))
    date_added = models.DateTimeField(_('date added'), editable=False,
                                      default=datetime.datetime.now)

    class Meta:
        verbose_name = _('IPTableChain')
        verbose_name_plural = _('IPTableChains')
        get_latest_by = 'date_added'

#if not reversion.is_registered(IPTableChain):
#    reversion.register(IPTableChain)


class IPTableRule(models.Model):
    table = models.ForeignKey('IPTable')
    rule = models.CharField(_('rule'), max_length=255)
    date_added = models.DateTimeField(_('date added'), editable=False,
                                      default=datetime.datetime.now)

    class Meta:
        verbose_name = _('IPTableRules')
        verbose_name_plural = _('IPTableRules')
        get_latest_by = 'date_added'

#if not reversion.is_registered(IPTableRule):
#    reversion.register(IPTableRule)

