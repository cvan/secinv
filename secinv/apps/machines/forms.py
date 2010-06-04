from ..fulltext.search import BaseSearchForm
from django.db.models import Q
from .models import Machine

class MachineSearchForm(BaseSearchForm):
    class Meta:
        base_qs = Machine.objects
        search_fields = ['sys_ip', 'hostname']

    """ 
    A custom addition - the absence of a clean_category method means
    the query will search for an exact match on this field.
    """
    '''
    category = forms.ModelChoiceField(
        queryset = Interface.live.all(),
        required = False
    )
    '''

    """ 
    This field creates a custom query addition via the clean_start_date
    method.
    """
    '''
    start_date = forms.DateField(
        required = False,
        input_formats = ('%Y-%m-%d',),
    )
    def clean_start_date(self):
        if self.cleaned_data['start_date']:
            return Q(creation_date__gte=self.cleaned_data['start_date'])
        else:
            return ""
    '''
