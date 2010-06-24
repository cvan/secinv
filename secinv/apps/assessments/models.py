from django.db import models


class Application(models.Model):
    VISIBILITY_CHOICES = (
        ('a', 'fully open'),
        ('b', 'application login required'),
        ('c', 'LDAP authentication required'),
        ('d', 'internal only'),
    )

    machine = models.ForeignKey('machines.Machine')
    name = models.CharField(_('application name'), blank=True, null=True)

    #overview = SerializedTextField(_('overview'), blank=True, null=True)
    overview = models.TextField(_('overview'), blank=True, null=True)

    contacts = models.TextField(_('contact points'), blank=True, null=True)
    url = models.CharField(_('URL'), max_length=255, blank=True, null=True)
    source_code_path = models.CharField(_('source code path'), max_length=255,
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

    file_uploads = models.BooleanFiled(_('allows file uploads'), default=0)
    arcsight = models.BooleanFiled(_('monitored via ArcSight'), default=0)

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



