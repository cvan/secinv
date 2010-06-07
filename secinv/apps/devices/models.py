from django.db import models
from django.utils.translation import ugettext_lazy as _
#from ..fulltext.search import SearchManager

import datetime
import re

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


class Device(models.Model):
    sys_ip = models.IPAddressField(_('IP address'))
    hostname = models.CharField(max_length=255)
    ext_ip = models.IPAddressField(_('external IP address'))
    diff = models.CharField(_('differences'), max_length=255)
    date_added = models.DateTimeField(_('date added'), editable=False,
                                      default=datetime.datetime.now)
    date_modified = models.DateTimeField(_('date modified'),
                                        default=datetime.datetime.now)
    date_scanned = models.DateTimeField(_('date scanned'))

    # Use a SearchManager for retrieving objects,
    # and tell it which fields to search.
    #objects = SearchManager(('sys_ip', 'hostname'))

    def __unicode__(self):
        return u'%s - %s' % (self.sys_ip, self.hostname)

    @property
    def slug(self):
        return re.sub('[^a-zA-Z-]', '-', self.hostname)

	#@models.permalink
    #def get_absolute_url(self):
    #	return "/%s/devices/%/" % (settings.BASE_URL, self.slug())


class Interface(models.Model):
    device = models.ForeignKey('Device')
    i_name = models.CharField(_('interface name'), max_length=50)
    i_ip = models.IPAddressField(_('IP address'))
    i_mac = models.CharField(_('MAC address'), max_length=17)
    i_mask = models.IPAddressField(_('netmask'))
    active = models.BooleanField(_('active'), default=1)
    date_added = models.DateTimeField(_('date added'), editable=False,
                                      default=datetime.datetime.now)

    def diff_split(self):
        return re.split(',', self.diff)

    def differences(self):
        """
        Create a dictionary of the differences between the latest
        interface of the same interface name.
        """
        i_older = Interface.objects.filter(device__id=self.device_id,
            i_name=self.i_name).exclude(id=self.id).filter(
            date_added__lt=self.date_added).order_by('-date_added').all()

        i_fields = ['i_ip', 'i_mac', 'i_mask']

        i_previous = {}
        if i_older.exists():
            i_values = [i_older[0].i_ip, i_older[0].i_mac, i_older[0].i_mask]

            if not i_older[0].active:
                i_values = ['', '', '']

            i_previous = dict(zip(i_fields, i_values))

        i_values = [self.i_ip, self.i_mac, self.i_mask]
        i_latest = dict(zip(i_fields, i_values))

        return diff_dict(i_previous, i_latest)

    def interfaces_dict(self):
        """
        Merge and return latest and previous dictionaries of interfaces.
        """
        i_older = Interface.objects.filter(device__id=self.device_id,
            i_name=self.i_name).exclude(id=self.id).filter(
            date_added__lt=self.date_added).order_by('-date_added').all()

        i_fields = ['i_ip', 'i_mac', 'i_mask']

        i_previous = {}
        if i_older.exists():
            i_values = [i_older[0].i_ip, i_older[0].i_mac, i_older[0].i_mask]
            i_previous = dict(zip(i_fields, i_values))

        i_values = [self.i_ip, self.i_mac, self.i_mask]
        i_latest = dict(zip(i_fields, i_values))

        return dict(i_latest, **i_previous)

    def __unicode__(self):
        return u'%s - %s - %s - %s' % (self.i_name, self.i_ip, self.i_mac,
                                       self.i_mask)
    class Meta:
        get_latest_by = 'date_added'


class System(models.Model):
    device = models.ForeignKey('Device')
    kernel_rel = models.CharField(_('kernel release'), max_length=255)
    rh_rel = models.CharField(_('RedHat release'), max_length=255)
    nfs = models.BooleanField(_('NFS?'), default=0)
    date_added = models.DateTimeField(_('date added'), editable=False,
                                        default=datetime.datetime.now)

    def nfs_mounted(self):
        return _('Yes') if self.nfs else _('No')

    def differences(self):
        """
        Create a dictionary of the differences between the latest
        and the previous system info.
        """
        s_older = System.objects.filter(device__id=self.device_id).exclude(
            id=self.id).filter(date_added__lt=self.date_added).order_by(
            '-date_added').all()

        s_fields = ['kernel_rel', 'rh_rel', 'nfs']

        s_previous = {}
        if s_older.exists():
            s_values = [s_older[0].kernel_rel, s_older[0].rh_rel, s_older[0].nfs]
            s_previous = dict(zip(s_fields, s_values))

        s_values = [self.kernel_rel, self.rh_rel, self.nfs]
        s_latest = dict(zip(s_fields, s_values))

        return diff_dict(s_previous, s_latest)

    def __unicode__(self):
        return u'%s - %s - %s' % (self.kernel_rel, self.rh_rel, self.nfs)

    class Meta:
        verbose_name_plural = _('System')
        get_latest_by = 'date_added'


class Services(models.Model):
    device = models.ForeignKey('Device')
    processes = models.CharField(max_length=255)
    ports = models.CommaSeparatedIntegerField(max_length=255)
    date_added = models.DateTimeField(_('date added'), editable=False,
                                      default=datetime.datetime.now)

    def differences(self):
        """
        Create a dictionary of the differences between the latest
        and the previous system info.
        """
        s_older = Services.objects.filter(
            device__id=self.device_id).exclude(id=self.id).filter(
            date_added__lt=self.date_added).order_by('-date_added').all()

        s_previous = {}
        if s_older.exists():
            s_procs = re.split(',', s_older[0].processes)
            s_ports = re.split(',', s_older[0].ports)
            s_previous = dict(zip(s_procs, s_ports))

        s_procs = re.split(',', self.processes)
        s_ports = re.split(',', self.ports)
        s_latest = dict(zip(s_procs, s_ports))

        return diff_dict(s_previous, s_latest)

    def processes_split(self):
        return re.split(',', self.processes)

    def ports_split(self):
        return re.split(',', self.ports)

    def processes_dict(self):
        """
        Merge and return latest and previous dictionaries of process/ports.
        """
        s_older = Services.objects.filter(
            device__id=self.device_id).exclude(id=self.id).filter(
            date_added__lt=self.date_added).order_by('-date_added').all()

        s_previous = {}
        if s_older.exists():
            s_procs = re.split(',', s_older[0].processes)
            s_ports = re.split(',', s_older[0].ports)
            s_previous = dict(zip(s_procs, s_ports))

        s_procs = re.split(',', self.processes)
        s_ports = re.split(',', self.ports)
        s_latest = dict(zip(s_procs, s_ports))

        return dict(s_latest, **s_previous)

    def __unicode__(self):
        return u'%s - %s' % (self.processes, self.ports)

    class Meta:
        verbose_name_plural = _('Services')
        get_latest_by = 'date_added'


class RPMs(models.Model):
    device = models.ForeignKey('Device')
    rpms = models.TextField(_('RPMs'))
    date_added = models.DateTimeField(_('date added'), editable=False,
                                      default=datetime.datetime.now)

    def differences(self):
        r_older = RPMs.objects.filter(
            device__id=self.device_id).exclude(id=self.id).filter(
        date_added__lt=self.date_added).order_by('-date_added').all()

        r_previous = []
        if r_older:
            r_previous = re.split('\n', r_older[0].rpms)

        r_latest = re.split('\n', self.rpms)

        return diff_list(r_previous, r_latest)


    def __unicode__(self):
        return u'%s' % (self.rpms[0:100])

    class Meta:
        verbose_name = _('RPMs')
        verbose_name_plural = _('RPMs')
        get_latest_by = 'date_added'
