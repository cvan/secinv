from django.db.models import Q
from django.core import serializers
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils import simplejson

from .models import Machine, Services, System, RPMs, Interface, SSHConfig, \
                    IPTables, ApacheConfig
from .forms import MachineSearchForm
from .utils import diff_list, diff_dict, get_version_diff, get_version_diff_field

from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter
from pygments.lexers import ApacheConfLexer

from reversion.models import Version

import re
import json

DIFF_SECTION_SLUGS = ('iptables', 'httpd-conf')

def get_all_domains():
    all_domains = []

    m_all = Machine.objects.all()
    for m in m_all:
        a_m = ApacheConfig.objects.filter(machine__id=m.id).all()
        for a in a_m:
            for fn in a.included:
                try:
                    i_a = ApacheConfig.objects.get(machine__id=m.id,
                                                   filename=fn)
                    if i_a.domains:
                        # TODO: Want port number (value)?
                        for k in i_a.domains.keys():
                            if not [m.hostname, k, i_a.id] in all_domains:
                                all_domains.append([m.hostname, k, i_a.id])
                except ApacheConfig.DoesNotExist:
                    pass

    all_domains.sort()
    return all_domains

def get_all_machines(order_by='id'):
    return Machine.objects.all().order_by(order_by)

#
# TODO: Save in a table.
#
# TODO: Update after each scan.
#

#
# TODO: Apache Parser -- Force directives to be uppercased.
#
def get_all_directives():
    all_directives_dict = {}

    a_all = ApacheConfig.objects.all()
    for a in a_all:
        if a.directives:
            for k, v in a.directives.iteritems():
                if k in all_directives_dict:
                    all_directives_dict[k] += v
                else:
                    all_directives_dict[k] = v

    all_directives = []

    for key, values in all_directives_dict.iteritems():
        all_directives.append([key, list(set(values))])

    all_directives.sort()
    return all_directives


'''
def get_all_directives():
    all_directives_dict = {}

    m_all = Machine.objects.all()
    for m in m_all:
        a_m = ApacheConfig.objects.filter(machine__id=m.id).all()
        for a in a_m:
            if a.directives:
                for k, v in a.directives.iteritems():
                    if k in all_directives_dict:
                        all_directives_dict[k] += v
                    else:
                        all_directives_dict[k] = v

            for fn in a.included:
                try:
                    i_a = ApacheConfig.objects.get(machine__id=m.id,
                                                   filename=fn)
                    if i_a.directives:
                        for k, v in i_a.directives.iteritems():
                            if k in all_directives_dict:
                                all_directives_dict[k] += v
                            else:
                                all_directives_dict[k] = v
                except ApacheConfig.DoesNotExist:
                    pass

    all_directives = []

    for key, values in all_directives_dict.iteritems():
        all_directives.append([key, list(set(values))])

    all_directives.sort()
    return all_directives
'''

def index(request):
    """Machines index page."""
    machines = Machine.objects.all()
    query = request.GET.get('q', '')

    template_context = {'machines': machines,
                        'query': query,
                        'all_machines_hn': get_all_machines('-hostname'),
                        'all_machines_ip': get_all_machines('-sys_ip'),
                        'all_domains': get_all_domains(),
                        'all_directives': get_all_directives()}
    return render_to_response('machines/index.html', template_context,
                              context_instance=RequestContext(request))


# View that that returns the JSON result.
def history(request, machine_slug):
    # TODO: prevent calls
    #if not request.is_ajax():
    #    return HttpResponse(status=400)

    m = get_object_or_404(Machine, hostname=machine_slug)

    # Retrieve all the system history.
    system_history = System.objects.filter(machine__id=m.id).order_by(
        '-date_added').all()

    # Serialize the result of the database retrieval to JSON and send an
    # application/json response.
    return HttpResponse(serializers.serialize('json', system_history),
                        mimetype='application/json')


def recurse_ac_includes(ac, field_name='filename'):
    ac_includes = []
    for fn in ac.included:
        try:
            i_ac = ApacheConfig.objects.get(machine__id=ac.machine_id, filename=fn)

            l = i_ac.__getattribute__(field_name)

            if i_ac.included:
                l = [i_ac.__getattribute__(field_name), recurse_ac_includes(i_ac)]

            ac_includes.append(l)

        except ApacheConfig.DoesNotExist:
            pass

    return ac_includes


def detail(request, machine_slug):
    m = get_object_or_404(Machine, hostname=machine_slug)
    query = request.GET.get('q', '')

    ## System.
    system_latest = []
    system_history = System.objects.filter(machine__id=m.id).order_by(
        '-date_added').all()

    # Get historical versions of System objects.
    system_versions = get_version_diff(system_history[0])

    if system_history.exists():
        system_latest = system_history[0]


    ## Services.
    services_latest = []
    services_history = Services.objects.filter(machine__id=m.id).order_by(
        '-date_added').all()

    # Get historical versions of Services objects.
    services_versions = get_version_diff(services_history[0], ',')

    if services_history.exists():
        services_latest = services_history[0]


    ## Interfaces.

    # Get latest interfaces (select by distinct interface name).
    distinct_interfaces = Interface.objects.filter(
        machine__id=m.id).values_list('i_name', flat=True).distinct()

    interfaces_latest = []
    interfaces_versions = []
    for i in distinct_interfaces:
        i_latest = Interface.objects.filter(machine__id=m.id,
                                            i_name=i).latest()
        interfaces_latest.append(i_latest)

        # Append each unique interface's history.
        i_v = get_version_diff(i_latest)
        interfaces_versions += i_v

    if interfaces_versions:
        interfaces_versions = sorted(interfaces_versions,
                                     key=lambda k: k['timestamp'],
                                     reverse=True)


    ## SSHConfig.
    sshconfig_latest = []
    sshconfig_history = SSHConfig.objects.filter(machine__id=m.id).order_by(
        '-date_added').all()

    # Get historical versions of SSHConfig objects.
    sshconfig_versions = get_version_diff(sshconfig_history[0], '\n')

    if sshconfig_history.exists():
        sshconfig_latest = sshconfig_history[0]


    # RPMs.
    rpms_list = []
    rpms_date_added = None
    rpms_history = RPMs.objects.filter(machine__id=m.id).order_by(
        '-date_added').all()

    # Get historical versions of RPMs objects.
    rpms_versions = get_version_diff(rpms_history[0], '\n')

    if rpms_history.exists():
        rpms_list = re.split('\n', rpms_history[0].v_rpms)
        rpms_date_added = rpms_history[0].date_added

    rpms_latest = {'installed': rpms_list, 'date_added': rpms_date_added}


    ## iptables.
    iptables_latest = []
    iptables_history = IPTables.objects.filter(machine__id=m.id).order_by(
        '-date_added').all()

    # Get historical versions of IPTables objects.
    iptables_versions = get_version_diff_field(iptables_history[0], 'body')

    if iptables_history.exists():
        iptables_latest = iptables_history[0]


    ## Apache configuration files.
    apacheconfig_latest = []
    apacheconfig_includes = []
    apacheconfig_history = ApacheConfig.objects.filter(machine__id=m.id).order_by(
        '-date_added').all()



    # Get historical versions of ApacheConfig objects.
    apacheconfig_versions = []
    for a_h in apacheconfig_history:
        a_v = get_version_diff_field(a_h, 'body')
        apacheconfig_versions += a_v

    if apacheconfig_versions:
        apacheconfig_versions = sorted(apacheconfig_versions,
                                       key=lambda k: k['timestamp'],
                                       reverse=True)

    if apacheconfig_history.exists():
        # TODO: get main `httpd.conf` file.
        apacheconfig_latest = ApacheConfig.objects.get(machine__id=m.id,
            filename__endswith='/httpd.conf')

        apacheconfig_latest_body = highlight(apacheconfig_latest.body,
                                             ApacheConfLexer(),
                                             HtmlFormatter())

        body = ''
        lines = re.split('\n', apacheconfig_latest_body)
        for line in lines:
            ls = re.split(' ', line.replace('<span class="nb">', '').replace('</span>', ''))
            if len(ls) == 2 and ls[0].lower() == 'include':
                # TODO: in Apache Config Parser, handle ``quoted`` Include filenames.

                try:
                    a = ApacheConfig.objects.get(machine__id=m.id,
                                                 filename__endswith=ls[1])
                    i_fn = '<a href="%s">%s</a>' % (a.get_absolute_url(), ls[1])
                except (ApacheConfig.DoesNotExist,
                        ApacheConfig.MultipleObjectsReturned):
                    i_fn = '%s' % ls[1]

                line = '<span class="nb">%s</span> %s' % (ls[0], i_fn)
            body += '%s\n' % line
        apacheconfig_latest_body = body


        for fn in apacheconfig_latest.included:
            try:
                i_ac = ApacheConfig.objects.get(machine__id=m.id, filename=fn)

                apacheconfig_includes.append(i_ac)
            except ApacheConfig.DoesNotExist:
                pass

    # Recurse includes.
    ac_includes = recurse_ac_includes(apacheconfig_latest)

    template_context = {'query': query,
                        'machine': m,
                        'system': system_latest,
                        'system_versions': system_versions,
                        'services': services_latest,
                        'services_versions': services_versions,
                        'rpms': rpms_latest,
                        'rpms_versions': rpms_versions,
                        'interfaces': interfaces_latest,
                        'interfaces_versions': interfaces_versions,
                        'sshconfig': sshconfig_latest,
                        'sshconfig_versions': sshconfig_versions,
                        'iptables': iptables_latest,
                        'iptables_versions': iptables_versions,
                        'apacheconfig': apacheconfig_latest,
                        'apacheconfig_versions': apacheconfig_versions,
                        'apacheconfig_latest_body': apacheconfig_latest_body,
                        'apacheconfig_includes': apacheconfig_includes,
                        'ac_includes': ac_includes,
                        'all_machines_hn': get_all_machines('-hostname'),
                        'all_machines_ip': get_all_machines('-sys_ip'),
                        'all_domains': get_all_domains(),
                        'all_directives': get_all_directives()}
    return render_to_response('machines/detail.html', template_context,
                              context_instance=RequestContext(request))


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
                        'terms': terms,
                        'all_machines_hn': get_all_machines('-hostname'),
                        'all_machines_ip': get_all_machines('-sys_ip'),
                        'all_domains': get_all_domains(),
                        'all_directives': get_all_directives()}
    return render_to_response('machines/search.html', template_context,
        context_instance=RequestContext(request))


def httpd_conf(request, machine_slug, ac_id):
    m = get_object_or_404(Machine, hostname=machine_slug)
    ac = get_object_or_404(ApacheConfig, id=ac_id)

    highlighted_code = highlight(ac.body, ApacheConfLexer(), HtmlFormatter())

    # TODO: ADD AS FILTER.
    body = ''
    lines = re.split('\n', highlighted_code)
    for line in lines:
        ls = re.split(' ', line.replace('<span class="nb">', '').replace('</span>', ''))
        if len(ls) == 2 and ls[0].lower() == 'include':
            # TODO: in Apache Config Parser, handle ``quoted`` Include filenames.

            try:
                a = ApacheConfig.objects.get(machine__id=m.id,
                                             filename__endswith=ls[1])
                i_fn = '<a href="%s">%s</a>' % (a.get_absolute_url(), ls[1])
            except (ApacheConfig.DoesNotExist, ApacheConfig.MultipleObjectsReturned):
                i_fn = '%s' % ls[1]

            line = '<span class="nb">%s</span> %s' % (ls[0], i_fn)
        body += '%s\n' % line

    # Get historical versions of ApacheConfig object.
    apacheconfig_versions = get_version_diff_field(ac, 'body')

    # Get includes.
    apacheconfig_includes = []
    for fn in ac.included:
        try:
            i_ac = ApacheConfig.objects.get(machine__id=m.id, filename=fn)

            apacheconfig_includes.append(i_ac)
        except ApacheConfig.DoesNotExist:
            pass

    # Recurse includes.
    ac_includes = recurse_ac_includes(ac)

    query = request.GET.get('q', '')
    template_context = {'machine': m,
                        'query': query,
                        'ac': ac,
                        'ac_body': body,
                        'all_machines_hn': get_all_machines('-hostname'),
                        'all_machines_ip': get_all_machines('-sys_ip'),
                        'all_domains': get_all_domains(),
                        'all_directives': get_all_directives(),
                        'apacheconfig_versions': apacheconfig_versions,
                        'apacheconfig_includes': apacheconfig_includes,
                        'ac_includes': ac_includes}
    return render_to_response('machines/httpd_conf.html', template_context,
        context_instance=RequestContext(request))


def diff(request, machine_slug, section_slug, version_number,
         compare_with='previous'):
    if section_slug not in DIFF_SECTION_SLUGS:
        raise Http404

    m = get_object_or_404(Machine, hostname=machine_slug)
    query = request.GET.get('q', '')
    v_num = int(version_number)

    body_current = ''
    body_previous = ''

    if section_slug == 'iptables':
        past_history = ApacheConfig.objects.filter(machine__id=m.id).order_by(
            '-date_added').all()
    elif section_slug == 'httpd-conf':
        past_history = ApacheConfig.objects.filter(machine__id=m.id).order_by(
            '-date_added').all()

    if past_history.exists():
        if compare_with == 'current':
            body_current = past_history[0].body

        obj_versions = Version.objects.get_for_object(
            past_history[0]).order_by('revision')
        if obj_versions:
            try:
                if compare_with == 'current':
                    body_previous = obj_versions[v_num - 1].field_dict['body']
                elif compare_with == 'previous':
                    body_current = obj_versions[v_num - 1].field_dict['body']
                    body_previous = obj_versions[v_num - 2].field_dict['body']
            except (IndexError, AssertionError):
                pass

            older_version = ''
            newer_version = ''

            if compare_with == 'current':
                if (v_num - 2) < len(obj_versions):
                    older_version = v_num - 1 # index + 1
                if v_num < len(obj_versions):
                    newer_version = v_num + 1
            elif compare_with == 'previous':
                if (v_num - 3) < len(obj_versions):
                    older_version = v_num - 2
                if v_num < len(obj_versions):
                    newer_version = v_num + 1

            if older_version < 0:
                older_version = ''
            if newer_version < 0:
                newer_version = ''

    v_num_previous = 0
    if v_num > 0:
        v_num_previous = v_num - 1

    template_context = {'machine': m,
                        'query': query,
                        'section': 'httpd-conf',
                        'obj_current': past_history[0],
                        'body_current': body_current,
                        'body_previous': body_previous,
                        'version_current': str(v_num),
                        'version_previous': str(v_num_previous),
                        'older_version': str(older_version),
                        'newer_version': str(newer_version),
                        'compare_with': compare_with,
                        'all_machines_hn': get_all_machines('-hostname'),
                        'all_machines_ip': get_all_machines('-sys_ip'),
                        'all_domains': get_all_domains(),
                        'all_directives': get_all_directives()}
    return render_to_response('machines/diff.html', template_context,
                              context_instance=RequestContext(request))


# View that that returns the JSON result.
'''
def ac_filter_directives(request, directive_slug=None):
    # TODO: prevent calls
    #if not request.is_ajax():
    #    return HttpResponse(status=400)

    all_directives = get_all_directives()
    if directive_slug:
        for v in all_directives:
            if v[0] == directive_slug:
                result = v[1]
                break
    else:
        result = [f[0] for f in all_directives]
        #result = []
        #for f in all_directives:
        #    result.append(f[0])

    # Serialize the result of the database retrieval to JSON and send an
    # application/json response.
#    return HttpResponse(serializers.serialize('json', get_all_domains()),
    return HttpResponse(simplejson.dumps(result),
                        mimetype='application/json')
'''

def ac_filter_directives_keys(request):
    # TODO: prevent calls
    #if not request.is_ajax():
    #    return HttpResponse(status=400)

    all_directives = get_all_directives()
    result = [f[0] for f in all_directives]

    # Serialize the result of the database retrieval to JSON and send an
    # application/json response.
    return HttpResponse(simplejson.dumps(result),
                        mimetype='application/json')

def ac_filter_directives(request):
    # TODO: prevent calls
    # if not request.is_ajax():
    #    return HttpResponse(status=400)

    if request.method == 'POST': # and request.is_ajax():
        #result = 'Raw Data: "%s"' % request.raw_post_data
        directive = request.POST.get('directive', '')

        all_directives = get_all_directives()
        if directive:
            for v in all_directives:
                if v[0] == directive:
                    result = v[1]
                    break
    else:
        return HttpResponse(status=400)

    # Serialize the result of the database retrieval to JSON and send an
    # application/json response.
    return HttpResponse(simplejson.dumps(result),
                        mimetype='application/json')


def machine_filter(request):
    """Find machine by hostname, IP, or domain and redirect."""
    hostname = request.GET.get('machine_hostname', '')
    ip = request.GET.get('machine_ip', '')
    domain = request.GET.get('machine_domain', '')

    if request.method != 'GET':
        return HttpResponse(status=400)

    m_hn = ''
    if hostname:
        m_hn = hostname
    elif ip:
        m_hn = ip
    elif domain:
        m_hn = domain

    if m_hn:
        m = get_object_or_404(Machine, hostname=m_hn)
        destination = reverse('machines-detail', args=[m.hostname])
    else:
        destination = reverse('machines-index')

    return HttpResponseRedirect(destination)
    #return HttpResponse(destination)


def ac_filter_results(request):
    """Filter ApacheConfig objects by parameters and values."""
    query = request.GET.get('q', '')
    ac_parameter = request.GET.get('ac_parameter', '')
    ac_value = request.GET.get('ac_value', '')

    if request.method != 'GET':
        return HttpResponse(status=400)

    results = []

    # Store matching ApacheConfig objects in results list.
    a_all = ApacheConfig.objects.all()
    for a in a_all:
        if a.directives:
            for param, values in a.directives.iteritems():
                if param == ac_parameter or ac_parameter == '':
                    for v in values:
                        if v == ac_value or ac_value == '':
                            results.append([param, v, a])

    results.sort()

    template_context = {'query': query,
                        'ac_parameter': ac_parameter,
                        'ac_value': ac_value,
                        'results': results,
                        'all_machines_hn': get_all_machines('-hostname'),
                        'all_machines_ip': get_all_machines('-sys_ip'),
                        'all_domains': get_all_domains(),
                        'all_directives': get_all_directives()}
    return render_to_response('machines/httpd_results.html', template_context,
                              context_instance=RequestContext(request))
