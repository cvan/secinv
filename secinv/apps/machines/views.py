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

def diff_list(l_old, l_new):
    """Creates a new dictionary representing a difference between two lists."""
    set_old, set_new = set(l_old), set(l_new)
    intersect = set_new.intersection(set_past)

    added = list(set_new - intersect)
    removed = list(set_old - intersect)

    return {'added': added, 'removed': removed}

def diff_dict(a, b, delimiter=None):
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

    # If inactive object is now active, mark each field as 'added'.
    if 'active' in a and a['active'] == False and 'active' in b and b['active'] == True:
        for key, value in b.iteritems():
            added[key] = value
    # If object is inactive, mark each field as 'removed'.
    elif 'active' in b and b['active'] == False:
        for key, value in b.iteritems():
            removed[key] = value
    else:
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

    diffs = {'removed': removed, 'added': added, 'changed': changed,
             'unchanged': unchanged}

    # To determine the differences of key/value pairs, the key and value fields
    # are split, merged as dictionaries, and subsequently compared.

    pair = {}
    if delimiter:
        key_name = None
        value_name = None
        for key, value in b.iteritems():
            if key[:2] == 'k_' and delimiter in value:
                key_name = key
                a_pair_k = re.split(delimiter, a[key]) if key in a else []
                b_pair_k = re.split(delimiter, value)
            if key[:2] == 'v_' and delimiter in value:
                value_name = value
                a_pair_v = re.split(delimiter, a[key]) if key in a else []
                b_pair_v = re.split(delimiter, value)


        if key_name and value_name:
            a_pair_dict = dict(zip(a_pair_k, a_pair_v))
            b_pair_dict = dict(zip(b_pair_k, b_pair_v))
            pair = diff_dict(a_pair_dict, b_pair_dict)

            # Merge previous and current dictionaries.
            b = dict(a_pair_dict, **b_pair_dict)
        elif value_name:
            pair = diff_list(a_pair_v, b_pair_v)

            # Similarly, merge lists.
            b = list(a_pair_v, **b_pair_v)

        if value_name:
            diffs['pair'] = {'merged': b, 'diff': pair}

    return diffs


def get_version_diff(obj_item, delimiter=None):
    obj_version = Version.objects.get_for_object(obj_item).order_by('revision')
    versions = []
    for index, ver in enumerate(obj_version):
        '''
        try:
            old_v = obj_version[index + 1].field_dict
        #except AssertionError:
        except IndexError:
            old_v = {}
        new_v = ver.field_dict
        patch = diff_dict(old_v, new_v)
        '''
        try:
            old_v = obj_version[index - 1].field_dict
        except AssertionError:
        #except IndexError:
            old_v = {}
        new_v = ver.field_dict
        patch = diff_dict(old_v, new_v, delimiter)

        new_fields = ver.field_dict
        # If there are old fields, merge the dictionaries.
        if old_v:
            new_fields = dict(old_v, **ver.field_dict)

        versions.append({'fields': new_fields, 'diff': patch,
                         'timestamp': ver.field_dict['date_added']})
    versions.reverse()
    return versions


def index(request):
    machines = Machine.objects.all()
    query = request.GET.get('q', '')
    return render_to_response('machines/index.html',
        {'machines': machines, 'query': query},
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

    # Get historical versions of System objects.
    system_versions = get_version_diff(system_history[0])

    if system_history.exists():
        system_latest = System.objects.filter(machine__id=p.id).latest()
        #system_latest = system_versions[0]


    services_latest = []
    services_history = Services.objects.filter(machine__id=p.id).order_by(
        '-date_added').all()

    # Get historical versions of Services objects.
    services_versions = get_version_diff(services_history[0], ',')

    if services_history.exists():
        services_latest = Services.objects.filter(machine__id=p.id).latest()


    rpms_list = []
    rpms_date_added = None
    rpms_history = RPMs.objects.filter(machine__id=p.id).order_by(
        '-date_added').all()

    if rpms_history.exists():
        rpms_obj = RPMs.objects.filter(machine__id=p.id).latest()

        rpms_list = re.split('\n', rpms_obj.v_rpms)

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

        # *** add to dict_diff: Mark oldest of each interface as 'added'. ***
        i_oldest = Interface.objects.filter(machine__id=p.id,
            i_name=i).order_by('date_added').all()
        if i_oldest.exists():
            interfaces_added_ids.append(i_oldest[0].id)

        v_previous = Version.objects.get_for_object(i_latest).order_by('-revision')

        #i_previous = Interface.objects.filter(machine__id=p.id,
        #    i_name=i, active=False).exclude(id=i_latest.id).order_by(
        #    '-date_added').all()
        if v_previous:
            # If second most recent interface was inactive but the latest
            # interface is now active, then mark it as "added."
            #interfaces_added_ids.append(v_previous.object_id)
            pass

    interfaces_history = Interface.objects.filter(machine__id=p.id).order_by(
        '-date_added').all()


    #interfaces_versions = get_version_diff(interfaces_history[0])

    # Get all unique interfaces.
    interfaces_versions = []
    for i in interfaces_latest:
        i_v = get_version_diff(i)
        interfaces_versions += i_v

    #interfaces_newest = interfaces_versions[0]

    interfaces_versions = sorted(interfaces_versions,
                                 key=lambda k: k['timestamp'], reverse=True)

    #for i in interfaces_versions:
    #    i['fields']['date_added']

    #interfaces_versions = [get_version_diff(i) for i in interfaces_latest]

    #interfaces_versions = Version.objects.get_deleted(Interface)


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
                        'services_versions': services_versions,
                        'rpms': rpms_latest,
                        'rpms_history': rpms_history,
                        'interfaces': interfaces_latest,
                        'interfaces_history': interfaces_history,
                        'interfaces_versions': interfaces_versions,
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
