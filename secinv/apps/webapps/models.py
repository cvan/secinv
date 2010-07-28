from django.db import models
from django.utils.translation import ugettext_lazy as _
#from ..fulltext.search import SearchManager
from ..fields import *
from reversion.models import Version

import datetime
import re
import reversion

VISIBILITY_CHOICES = (
    ('a', _('fully open')),
    ('b', _('application login required')),
    ('c', _('LDAP authentication required')),
    ('d', _('internal only')),
)

CLASSIFICATION_CHOICES = (
    ('a', _('code review')),
    ('b', _('app penetration')),
    ('c', _('risk assessment')),
)

VISIBILITY_DICT = {}
for c in VISIBILITY_CHOICES:
    VISIBILITY_DICT[c[0]] = c[1]

CLASSIFICATION_DICT = {}
for c in CLASSIFICATION_CHOICES:
    CLASSIFICATION_DICT[c[0]] = c[1]


class Application(models.Model):
    machine = models.ManyToManyField('machines.Machine')
    name = models.CharField(_('application name'), max_length=255, blank=True,
                            null=True)

    #overview = SerializedTextField(_('overview'), blank=True, null=True)
    overview = models.TextField(_('overview'), blank=True, null=True)

    contacts = models.TextField(_('contact points'), blank=True, null=True)
    url = models.URLField(_('URL'), verify_exists=False, blank=True, null=True)
    source_code_url = models.URLField(_('source code URL'), verify_exists=False,
                                      blank=True, null=True)

    source_code_path = models.CharField(_('source code local path'), max_length=255,
                                        blank=True, null=True)

    bugzilla_product = models.CharField(_('Bugzilla Product field'), max_length=255,
                                        blank=True, null=True)
    bugzilla_component = models.CharField(_('Bugzilla Component field'), max_length=255,
                                          blank=True, null=True)

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
    #search_fields = []

    def __unicode__(self):
        return u'%s' % (self.name)

    def assessments(self):
        try:
            a = Assessment.objects.filter(application__id=self.id).order_by('-date_added').all()
        except Assessment.DoesNotExist:
            a = None
        return a

    def visibility_value(self):
        try:
            return VISIBILITY_DICT[self.visibility]
        except KeyError:
            return ''

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

    # TODO: Multiple Checkbox Field.
    #classification = models.CharField(_('assessment type (code review, app penetration, risk assessment)'),
                                      #max_length=255,
    classification = models.CharField(_('assessment type'),
                                      max_length=255,
                                      blank=True, null=True,
                                      choices=CLASSIFICATION_CHOICES)

    date_added = models.DateTimeField(_('date added'), editable=False,
                                      default=datetime.datetime.now)
    date_modified = models.DateTimeField(_('date modified'),
                                        default=datetime.datetime.now)

    # Add search fields.
    #search_fields = []

    def __unicode__(self):
        return u'%s by %s' % (self.application.name, self.reviewer)

    def classification_value(self):
        try:
            return CLASSIFICATION_DICT[self.classification]
        except KeyError:
            return self.classification

    class Meta:
        verbose_name = _('Assessment')
        verbose_name_plural = _('Assessments')
        get_latest_by = 'date_added'

