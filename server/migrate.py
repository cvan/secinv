#!/usr/bin/env python

from __future__ import with_statement

import datetime
import os
import sys


# BASE_PATH is the absolute path of '..' relative to this script location.
BASE_PATH = reduce(lambda l, r: l + os.path.sep + r,
    os.path.dirname(os.path.realpath(__file__)).split(os.path.sep)[:-1])

# Append settings directory.
sys.path.append(os.path.join(BASE_PATH, 'secinv'))

import manage

from apps.machines.models import (Machine, Services, System, RPMs, Interface,
                                  SSHConfig, IPTables, ApacheConfig,
                                  PHPConfig, MySQLConfig, AuthToken)
from apps.fields import dbsafe_decode

from reversion.models import Version

import reversion


# Convert SSHConfig SerializedTextField to JSONField.

sshconfigs = SSHConfig.objects.filter(active=True).all()
phpconfigs = PHPConfig.objects.filter(active=True).all()
mysqlconfigs = MySQLConfig.objects.filter(active=True).all()
apacheconfigs = ApacheConfig.objects.filter(active=True).all()

from apps.json_field import JSONField

from django.utils import simplejson as json

'''
for s in sshconfigs:
    s.items = json.dumps(dbsafe_decode(s.items))
    #print s.items
    s.save()
    print "Updated SSHConfig #%s ..." % s.id

for s in phpconfigs:
    s.items = json.dumps(dbsafe_decode(s.items))
    #print s.items
    s.save()
    print "Updated PHPConfig #%s ..." % s.id

for s in mysqlconfigs:
    s.items = json.dumps(dbsafe_decode(s.items))
    #print json.dumps(dbsafe_decode(s.items))
    s.save()
    print "Updated MySQLConfig #%s ..." % s.id

for s in apacheconfigs:
    s.directives = json.dumps(dbsafe_decode(s.directives))
    s.domains = json.dumps(dbsafe_decode(s.domains))
    s.included = json.dumps(dbsafe_decode(s.included))
    s.save()
    print "Updated ApacheConfig #%s ..." % s.id

'''
