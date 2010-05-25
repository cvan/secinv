import datetime
from django.db import models
from django.utils.translation import ugettext_lazy as _
#from fields import IncrementingField, AutoNowField

# Create your models here.

class Machine(models.Model):
    sys_ip = models.CharField(max_length=15)
    date_added = models.DateTimeField(_('date added'), editable=False,
                                      default=datetime.datetime.now())
    date_edited = models.DateTimeField(_('date edited'))


    question = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')

    def __unicode__(self):
        return self.question

    def was_published_today(self):
        return self.pub_date.date() == datetime.date.today()
    was_published_today.short_description = 'Published Today?'


class Choice(models.Model):
    machine = models.ForeignKey(Machine)
    choice = models.CharField(max_length=200)
    votes = models.IntegerField()

    def __unicode__(self):
        return self.choice


class Asset(models.Model):
    machine = models.ForeignKey('Machine')
    hostname = models.CharField(max_length=255)
    sys_ip = models.IPAddressField()
    ext_ip = models.IPAddressField()
    httpd = models.BooleanField(default=0)
    mysqld = models.BooleanField(default=0)
    openvpn = models.BooleanField(default=0)
    nfs = models.BooleanField(default=0)
    kernel_rel = models.CharField(max_length=255)
    rh_rel = models.CharField(max_length=255)
    #interfaces = models.ForeignKey('Interface')
    date_added = models.DateTimeField(_('date added'), editable=False,
                                      default=datetime.datetime.now())
    def __unicode__(self):
        return self.sys_ip

class Interface(models.Model):
    machine = models.ForeignKey('Machine')
    i_name = models.CharField(max_length=50)
    i_ip = models.IPAddressField()
    i_mac = models.CharField(max_length=17)
    i_mask = models.IPAddressField()

class Ports(models.Model):
    machine = models.ForeignKey('Machine')
    processes = models.CharField(max_length=255)
    ports = models.CharField(max_length=255)
    date_added = models.DateTimeField(_('date added'), editable=False,
                                      default=datetime.datetime.now())
    date_updated = models.DateTimeField(_('date updated'))

class RPMs(models.Model):
    machine = models.ForeignKey('Machine')
    rpms = models.TextField()
    date_added = models.DateTimeField(_('date added'), editable=False,
                                      default=datetime.datetime.now())
    date_updated = models.DateTimeField(_('date updated'))

class History(models.Model):
    machine = models.ForeignKey('Machine')
    date_scanned = models.DateTimeField(_('date scanned'),
                                        default=datetime.datetime.now())

