from django import forms
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

from search.search import BaseSearchForm
from .models import Machine


HISTORY_CHOICES = (
    ('h', _('History')),
    ('c', _('Current')),
)


# TODO: Get verbose_name for each model.

SEARCHABLE_MODELS = (
    ('System', _('System Info')),
    ('Interface', _('Interfaces')),
    ('Services', _('Services Listening')),
    ('RPMs', _('RPMs')),
    ('IPTables', _('iptables')),
    ('SSHConfig', _('SSH Config')),
    ('ApacheConfig', _('Apache Config')),
    ('PHPConfig', _('PHP Config')),
    ('MySQLConfig', _('MySQL Config')),
)


class MachineSearchForm(BaseSearchForm):
    class Meta:
        base_qs = Machine.objects
        search_fields = ['sys_ip', 'hostname', 'ext_ip',
                         'system__kernel_rel', 'system__rh_rel', 'system__nfs',
                         'system__ip_fwd', 'system__iptables',
                         'services__k_processes', 'services__v_ports',
                         'rpms__v_rpms',
                         'interface__i_name', 'interface__i_ip',
                         'interface__i_mac', 'interface__i_mask',
                         'sshconfig__body', 'sshconfig__filename',
                         'apacheconfig__body', 'apacheconfig__filename',
                         'iptables__body',
                         'phpconfig__body', 'phpconfig__filename',
                         'mysqlconfig__body', 'mysqlconfig__filename']

    """
    A custom addition - the absence of a clean_category method means
    the query will search for an exact match on this field.
    """
    category = forms.ModelChoiceField(queryset=Machine.objects.all(),
                                      required=False)

    sections = forms.MultipleChoiceField(choices=SEARCHABLE_MODELS,
                                         widget=forms.CheckboxSelectMultiple(),
                                         required=False)

    history = forms.MultipleChoiceField(choices=HISTORY_CHOICES,
                                        widget=forms.CheckboxSelectMultiple(),
                                        required=False)


    """
    This field creates a custom query addition via the clean_start_date
    method.
    """
    '''
    start_date = forms.DateField(required=False, input_formats=('%Y-%m-%d',),)
    def clean_start_date(self):
        if self.cleaned_data['start_date']:
            return Q(creation_date__gte=self.cleaned_data['start_date'])
        else:
            return ""
    '''

