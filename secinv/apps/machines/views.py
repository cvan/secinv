from django.db.models import Q
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from .models import Machine, Services, System, RPMs, Interface, SSHConfig
from .forms import MachineSearchForm

from reversion.models import Version
#from reversion.helpers import generate_patch

import re

'''
def diff_dict(d_old, d_new):
    """
    Creates a new dict representing a diff between two dicts.
    """
    # Added and changed items.
    diff = {}
    for k, v in d_new.items():
        old_v = d_old.get(k, None)
        if v == old_v:
            continue
        diff.update({k: {'old': old_v, 'new': v}})

    # Deleted items.
    for k, v in d_old.items():
        if k not in d_new.keys():
            diff.update({k: {'deleted': v}})

    return diff
'''

def diff_dict(a, b):
    """Return differences from dictionaries a to b.

    Return a tuple of three dicts: (removed, added, changed).
    'removed' has all keys and values removed from a. 'added' has
    all keys and values that were added to b. 'changed' has all
    keys and their values in b that are different from the corresponding
    key in a.
    """

    removed = dict()
    added = dict()
    changed = dict()
    unchanged = dict()

    for key, value in a.iteritems():
        if key not in b:
            removed[key] = value
        elif b[key] != value:
            changed[key] = b[key]
        elif b[key] == value:
            unchanged[key] = b[key]
    for key, value in b.iteritems():
        if key not in a:
            added[key] = value

    return {'removed': removed, 'added': added, 'changed': changed, 'unchanged': unchanged}

def get_version_diff(obj_item):
    obj_version = Version.objects.get_for_object(obj_item)
    versions = []
    for index, ver in enumerate(obj_version):
        try:
            old_v = obj_version[index - 1].field_dict
        except AssertionError, IndexError:
            old_v = {}
        new_v = ver.field_dict
        patch = diff_dict(old_v, new_v)

        '''
        field_diffs = {}
        for status, field in patch:
            field_diffs[field] = status
        '''
        versions.append({'fields': ver.field_dict, 'diff': patch})
    return versions


def index(request):
    machine_list = Machine.objects.all()
    query = request.GET.get('q', '')
    return render_to_response('machines/index.html',
        {'machine_list': machine_list, 'query': query},
        context_instance=RequestContext(request))


# View that that returns the JSON result.
def history(request, machine_slug):
    # TODO: prevent calls
    #if not request.is_ajax():
    #    return HttpResponse(status=400)

    p = get_object_or_404(Machine, hostname=machine_slug)

    # Retrieve all the system history.
    system_history = System.objects.filter(machine__id=p.id).order_by(
        '-date_added').all()

    # Serialize the result of the database retrieval to JSON and send an
    # application/json response.
    return HttpResponse(serializers.serialize('json', system_history),
                        mimetype='application/json')


def detail(request, machine_slug):
    p = get_object_or_404(Machine, hostname=machine_slug)
    query = request.GET.get('q', '')

    system_latest = []
    system_history = System.objects.filter(machine__id=p.id).order_by(
        '-date_added').all()

    system_versions = get_version_diff(system_history[0])

    """
    system_versioning = []
    for index, ver in enumerate(system_version):
        try:
            old_v = system_version[index - 1].field_dict
        except AssertionError, IndexError:
            old_v = {}
        new_v = ver.field_dict
        patch = diff_dict(old_v, new_v)

        '''
        field_diffs = {}
        for status, field in patch:
            field_diffs[field] = status
        '''
        system_versioning.append({'fields': ver.field_dict, 'diff': patch})
    """

    if system_history.exists():
        system_latest = System.objects.filter(machine__id=p.id).latest()



    services_latest = []
    services_history = Services.objects.filter(machine__id=p.id).order_by(
        '-date_added').all()

    if services_history.exists():
        services_latest = Services.objects.filter(machine__id=p.id).latest()


    rpms_list = []
    rpms_date_added = None
    rpms_history = RPMs.objects.filter(machine__id=p.id).order_by(
        '-date_added').all()

    if rpms_history.exists():
        rpms_obj = RPMs.objects.filter(machine__id=p.id).latest()

        rpms_list = re.split('\n', rpms_obj.rpms)

        rpms_date_added = rpms_obj.date_added

    rpms_latest = {'installed': rpms_list, 'date_added': rpms_date_added}


    # Get latest interfaces (select by distinct interface name).
    distinct_interfaces = Interface.objects.filter(
        machine__id=p.id).values_list('i_name', flat=True).distinct()

    interfaces_latest = []
    interfaces_added_ids = []
    for i in distinct_interfaces:
        i_latest = Interface.objects.filter(machine__id=p.id,
                                            i_name=i).latest()
        interfaces_latest.append(i_latest)

        i_oldest = Interface.objects.filter(machine__id=p.id,
            i_name=i).order_by('date_added').all()
        if i_oldest.exists():
            interfaces_added_ids.append(i_oldest[0].id)

        i_previous = Interface.objects.filter(machine__id=p.id,
            i_name=i, active=False).exclude(id=i_latest.id).order_by(
            '-date_added').all()
        if i_previous.exists():
            # If second most recent interface was inactive but the latest
            # interface is now active, then mark it as "added."
            interfaces_added_ids.append(i_latest.id)

    interfaces_history = Interface.objects.filter(machine__id=p.id).order_by(
        '-date_added').all()


    sshconfig_latest = []
    sshconfig_history = SSHConfig.objects.filter(machine__id=p.id).order_by(
        '-date_added').all()

    if sshconfig_history.exists():
        sshconfig_latest = SSHConfig.objects.filter(machine__id=p.id).latest()


    template_context = {'query': query,
                        'machine': p,
                        'system': system_latest,
                        'system_history': system_history,
                        'system_versions': system_versions,
                        'services': services_latest,
                        'services_history': services_history,
                        'rpms': rpms_latest,
                        'rpms_history': rpms_history,
                        'interfaces': interfaces_latest,
                        'interfaces_history': interfaces_history,
                        'interfaces_added': interfaces_added_ids,
                        'sshconfig': sshconfig_latest,
                        'sshconfig_history': sshconfig_history}
    return render_to_response('machines/detail.html', template_context,
        context_instance=RequestContext(request))


def results(request, machine_slug):
    p = get_object_or_404(Machine, hostname=machine_slug)
    return render_to_response('machines/results.html', {'machine': p},
        context_instance=RequestContext(request))


def vote(request, machine_slug):
    '''
    p = get_object_or_404(Machine, hostname=machine_slug)
    try:
        selected_choice = p.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the machine voting form.
        return render_to_response('machines/detail.html', {
            'machine': p,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('secinv.machines.views.results',
            args=(p.id,)))
    '''
    pass


def search(request):
    query = request.GET.get('q', '')
    terms = query.split()
    results = []
    excerpts = {}

    if query:
        form = MachineSearchForm(request.GET)
        if form.is_valid():
            results = form.get_result_queryset()
    else:
        form = MachineSearchForm()

    template_context = {'form': form,
                        'results': results,
                        'query': query,
                        'terms': terms}
    return render_to_response('machines/search.html', template_context,
        context_instance=RequestContext(request))
