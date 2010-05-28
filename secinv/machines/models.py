from django.db import models
from django.utils.translation import ugettext_lazy as _

import datetime
import re

class Machine(models.Model):
    sys_ip = models.IPAddressField(_('IP address'))
    hostname = models.CharField(max_length=255)
    ext_ip = models.IPAddressField(_('external IP address'))
    diff = models.CharField(_('differences'), max_length=255)
    date_added = models.DateTimeField(_('date added'), editable=False,
                                      default=datetime.datetime.now)
    date_modified = models.DateTimeField(_('date modified'),
                                        default=datetime.datetime.now)
    date_scanned = models.DateTimeField(_('date scanned'))

    def __unicode__(self):
        return u'%s - %s' % (self.sys_ip, self.hostname)

    @property
    def slug(self):
        return re.sub('[^a-zA-Z-]', '-', self.hostname)

    '''
    def was_published_today(self):
        return self.pub_date.date() == datetime.date.today()
    was_published_today.short_description = 'Published Today?'
    '''

'''
class Choice(models.Model):
    machine = models.ForeignKey(Machine)
    choice = models.CharField(max_length=200)
    votes = models.IntegerField()

    def __unicode__(self):
        return self.choice
'''

class Interface(models.Model):
    machine = models.ForeignKey('Machine')
    i_name = models.CharField(_('interface name'), max_length=50)
    i_ip = models.IPAddressField(_('IP address'))
    i_mac = models.CharField(_('MAC address'), max_length=17)
    i_mask = models.IPAddressField(_('netmask'))
    diff = models.CharField(_('differences'), max_length=255)
    date_added = models.DateTimeField(_('date added'), editable=False,
                                      default=datetime.datetime.now)

    def diff_split(self):
        return re.split(',', self.diff)

    def __unicode__(self):
        return u'%s - %s - %s - %s' % (self.i_name, self.i_ip, self.i_mac,
                                       self.i_mask)
    class Meta:
        get_latest_by = 'date_added'


class System(models.Model):
    machine = models.ForeignKey('Machine')
    kernel_rel = models.CharField(_('kernel release'), max_length=255)
    rh_rel = models.CharField(_('RedHat release'), max_length=255)
    nfs = models.BooleanField(_('NFS?'), default=0)
    diff = models.CharField(_('differences'), max_length=255)
    date_added = models.DateTimeField(_('date added'), editable=False,
                                        default=datetime.datetime.now)

    def diff_split(self):
        return re.split(',', self.diff)
    diff_split.short_description = 'differences split'


    def __unicode__(self):
        return u'%s - %s - %s' % (self.kernel_rel, self.rh_rel, self.nfs)

    class Meta:
        verbose_name_plural = _('System')
        get_latest_by = 'date_added'


class Services(models.Model):
    machine = models.ForeignKey('Machine')
    processes = models.CharField(max_length=255)
    ports = models.CommaSeparatedIntegerField(max_length=255)
    diff = models.CharField(_('differences'), max_length=255)
    diff_ins_processes = models.CharField(_('new processes'),
                                         max_length=255)
    diff_del_processes = models.CharField(_('removed processes'),
                                          max_length=255)
    diff_ins_ports = models.CharField(_('new ports'), max_length=255)
    diff_del_ports = models.CharField(_('removed ports'), max_length=255)
    date_added = models.DateTimeField(_('date added'), editable=False,
                                      default=datetime.datetime.now)

    def diff_split(self):
        return re.split(',', self.diff)

    def diff_ins_processes_split(self):
        return re.split(',', self.diff_ins_processes)

    def diff_del_processes_split(self):
        return re.split(',', self.diff_del_processes)

    def diff_ins_ports_split(self):
        return re.split(',', self.diff_ins_ports)

    def diff_del_ports_split(self):
        return re.split(',', self.diff_del_ports)

    def processes_split(self):
        return re.split(',', self.processes)

    def ports_split(self):
        return re.split(',', self.ports)

    def __unicode__(self):
        return u'%s - %s' % (self.processes, self.ports)

    class Meta:
        verbose_name_plural = _('Services')
        get_latest_by = 'date_added'


class RPMs(models.Model):
    machine = models.ForeignKey('Machine')
    rpms = models.TextField(_('RPMs'))
    diff = models.CharField(_('differences'), max_length=255)
    diff_ins_rpms = models.CharField(_('RPM differences'), max_length=255)
    diff_del_rpms = models.CharField(_('RPM differences'), max_length=255)
    date_added = models.DateTimeField(_('date added'), editable=False,
                                      default=datetime.datetime.now)

    def diff_split(self):
        return re.split(',', self.diff)

    def __unicode__(self):
        return u'%s' % (self.rpms)

    class Meta:
        verbose_name = _('RPMs')
        verbose_name_plural = _('RPMs')
        get_latest_by = 'date_added'

