import datetime
from django.db import models
from django.utils.translation import ugettext_lazy as _

class Machine(models.Model):
    sys_ip = models.IPAddressField(_('IP address'))
    hostname = models.CharField(max_length=255)
    ext_ip = models.IPAddressField(_('external IP address'))

    date_added = models.DateTimeField(_('date added'), editable=False,
                                      default=datetime.datetime.now)
    date_updated = models.DateTimeField(_('date updated'),
                                        default=datetime.datetime.now)
    date_scanned = models.DateTimeField(_('date scanned'))

    question = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')

    def __unicode__(self):
        return u'%s - %s' % (self.question, self.sys_ip)

    @property
    def slug(self):
        return re.sub('[^a-zA-Z-]', '-', self.hostname)

    def was_published_today(self):
        return self.pub_date.date() == datetime.date.today()
    was_published_today.short_description = 'Published Today?'


class Choice(models.Model):
    machine = models.ForeignKey(Machine)
    choice = models.CharField(max_length=200)
    votes = models.IntegerField()

    def __unicode__(self):
        return self.choice


class Interface(models.Model):
    machine = models.ForeignKey('Machine')
    i_name = models.CharField(_('interface name'), max_length=50)
    i_ip = models.IPAddressField(_('IP address'))
    i_mac = models.CharField(_('MAC address'), max_length=17)
    i_mask = models.IPAddressField(_('netmask'))
    date_added = models.DateTimeField(_('date added'), editable=False,
                                      default=datetime.datetime.now)
    date_updated = models.DateTimeField(_('date updated'),
                                        default=datetime.datetime.now)

    def __unicode__(self):
        return u'%s - %s - %s - %s' % (self.i_name, self.i_ip, self.i_mac,
                                       self.i_mask)


class System(models.Model):
    machine = models.OneToOneField('Machine')
    kernel_rel = models.CharField(_('kernel release'), max_length=255)
    rh_rel = models.CharField(_('RedHat release'), max_length=255)
    nfs = models.BooleanField(_('NFS?'), default=0)
    date_updated = models.DateTimeField(_('date updated'),
                                        default=datetime.datetime.now)

    def __unicode__(self):
        return u'%s - %s - %s' % (self.kernel_rel, self.rh_rel, self.nfs)

    class Meta:
        verbose_name_plural = _('System')


class Services(models.Model):
    machine = models.OneToOneField('Machine')
    processes = models.CharField(max_length=255)
    ports = models.CommaSeparatedIntegerField(max_length=255)
    #date_added = models.DateTimeField(_('date added'), editable=False,
    #                                  default=datetime.datetime.now)
    date_updated = models.DateTimeField(_('date updated'),
                                        default=datetime.datetime.now)
    def __unicode__(self):
        return u'%s - %s' % (self.processes, self.ports)

    class Meta:
        verbose_name_plural = _('Services')


class RPMs(models.Model):
    machine = models.OneToOneField('Machine')
    rpms = models.TextField(_('RPMs'))
    date_added = models.DateTimeField(_('date added'), editable=False,
                                      default=datetime.datetime.now)
    date_updated = models.DateTimeField(_('date updated'))

    def __unicode__(self):
        return u'%s' % (self.rpms)

    class Meta:
        verbose_name = _('RPMs')
        verbose_name_plural = _('RPMs')


