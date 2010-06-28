from django.db import models
from django.utils.translation import ugettext_lazy as _
#from ..fulltext.search import SearchManager
from ..fields import *
from reversion.models import Version

import datetime
import re
import reversion

VISIBILITY_CHOICES = (
    ('a', 'fully open'),
    ('b', 'application login required'),
    ('c', 'LDAP authentication required'),
    ('d', 'internal only'),
)

CLASSIFICATION_CHOICES = (
    ('a', 'code review'),
    ('b', 'app penetration'),
    ('c', 'risk assessment'),
)


class Application(models.Model):
    machine = models.ForeignKey('machines.Machine')
    name = models.CharField(_('application name'), max_length=255, blank=True,
                            null=True)

    #overview = SerializedTextField(_('overview'), blank=True, null=True)
    overview = models.TextField(_('overview'), blank=True, null=True)

    contacts = models.TextField(_('contact points'), blank=True, null=True)
    url = models.URLField(_('URL'), verify_exists=False, blank=True, null=True)
    source_code_path = models.FilePathField(_('source code path'), max_length=255,
                                            blank=True, null=True)

    bugzilla_product = models.TextField(_('Bugzilla Product field'), blank=True,
                                        null=True)
    bugzilla_component = models.TextField(_('Bugzilla Component field'), blank=True,
                                          null=True)

    visibility = models.CharField(_('public facing?'), max_length=1, blank=True,
                                  null=True, choices=VISIBILITY_CHOICES)

    # Application info.
    cc = models.BooleanField(_('handles credit cards'), default=0)
    pii = models.BooleanField(_('accepts PII'), default=0)
    logins = models.BooleanField(_('allows logins'), default=0)

    user_roles = models.TextField(_('supported roles'), blank=True, null=True)

    file_uploads = models.BooleanField(_('allows file uploads'), default=0)
    arcsight = models.BooleanField(_('monitored via ArcSight'), default=0)

    # Date info.
    date_added = models.DateTimeField(_('date added'), editable=False,
                                      default=datetime.datetime.now)
    date_modified = models.DateTimeField(_('date modified'),
                                        default=datetime.datetime.now)

    # Add search fields.
    search_fields = ['sys_ip', 'hostname', 'ext_ip',
                     'system__kernel_rel', 'system__rh_rel', 'system__nfs',
                     'system__ip_fwd', 'system__iptables',
                     'services__k_processes', 'services__v_ports',
                     'rpms__v_rpms',
                     'interface__i_name', 'interface__i_ip',
                     'interface__i_mac', 'interface__i_mask']

    def __unicode__(self):
        return u'%s' % (self.name)

    class Meta:
        verbose_name = _('Application')
        verbose_name_plural = _('Applications')
        get_latest_by = 'date_added'


class Assessment(models.Model):
    application = models.ForeignKey('Application')

    # TODO: Possibly integrate with authentication system later.
    reviewer = models.CharField(_('reviewer'), max_length=255, blank=True,
                                null=True)

    notes = models.TextField(_('assessment notes'), blank=True, null=True)

    # TODO: Store bugzilla # here, or multiple links.
    bugs = models.TextField(_('Bugzilla links'), blank=True, null=True)

    classification = models.CharField(_('assessment type'), max_length=255,
                                      blank=True, null=True,
                                      choices=CLASSIFICATION_CHOICES)

    date_added = models.DateTimeField(_('date added'), editable=False,
                                      default=datetime.datetime.now)
    date_modified = models.DateTimeField(_('date modified'),
                                        default=datetime.datetime.now)

    def __unicode__(self):
        return u'%s by %s' % (self.application.name, self.reviewer)

    class Meta:
        verbose_name = _('Assessment')
        verbose_name_plural = _('Assessments')
        get_latest_by = 'date_added'

