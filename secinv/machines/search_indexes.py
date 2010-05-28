import datetime
from haystack.indexes import *
from haystack import site
from secinv.machines.models import Machine


class MachineIndex(RealTimeSearchIndex):
    text = CharField(document=True, use_template=True)
    sys_ip = CharField(model_attr='sys_ip')
    hostname = CharField(model_attr='hostname')
    ext_ip = CharField(model_attr='ext_ip')
    date_added = DateTimeField(model_attr='date_added')
    date_updated = DateTimeField(model_attr='date_updated')
    date_scanned = DateTimeField(model_attr='date_scanned')

    def get_queryset(self):
        """Used when the entire index for model is updated."""
        return Machine.objects.filter()


site.register(Machine, MachineIndex)
