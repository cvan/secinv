from django.db.models import Q
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from .models import Machine, Services, System, RPMs, Interface, SSHConfig, \
                    IPTableInfo, ApacheConfig
from .forms import MachineSearchForm
from .utils import diff_list, diff_dict, get_version_diff, get_version_diff_field

from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter
from pygments.lexers import ApacheConfLexer

from reversion.models import Version

import re


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

def get_all_directives():
    all_directives_dict = {}

    m_all = Machine.objects.all()
    for m in m_all:
        a_m = ApacheConfig.objects.filter(machine__id=m.id).all()
        for a in a_m:
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


def index(request):
    """Machines index page."""
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

    m = get_object_or_404(Machine, hostname=machine_slug)

    # Retrieve all the system history.
    system_history = System.objects.filter(machine__id=m.id).order_by(
        '-date_added').all()

    # Serialize the result of the database retrieval to JSON and send an
    # application/json response.
    return HttpResponse(serializers.serialize('json', system_history),
                        mimetype='application/json')


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

    interfaces_versions = sorted(interfaces_versions,
                                 key=lambda k: k['timestamp'], reverse=True)


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
    iptables_history = IPTableInfo.objects.filter(machine__id=m.id).order_by(
        '-date_added').all()

    # Get historical versions of IPTableInfo objects.
    iptables_versions = get_version_diff_field(iptables_history[0], 'body')

    if iptables_history.exists():
        iptables_latest = iptables_history[0]


    ## Apache configuration files.
    apacheconfig_latest = []
    apacheconfig_includes = []
    apacheconfig_history = ApacheConfig.objects.filter(machine__id=m.id).order_by(
        '-date_added').all()

    # Get historical versions of ApacheConfig objects.
    apacheconfig_versions = get_version_diff_field(apacheconfig_history[0], 'body')

    if apacheconfig_history.exists():
        # TODO: get main `httpd.conf` file.
        apacheconfig_latest = apacheconfig_history[0]

        code = apacheconfig_latest.body

        l = ApacheConfLexer()
        #l.add_filter(VisibleWhitespaceFilter(newlines=True))
        #diff_highlighted = highlight(code, PythonLexer(), HtmlFormatter())
        apacheconfig_latest_body = highlight(code, l, HtmlFormatter())


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
                except (ApacheConfig.DoesNotExist, ApacheConfig.MultipleObjectsReturned):
                    i_fn = '%s' % ls[1]

                line = '<span class="nb">%s</span> %s' % (ls[0], i_fn)
            body += '%s\n' % line
        apacheconfig_latest_body = body


        for fn in apacheconfig_latest.included:
            try:
                i = ApacheConfig.objects.get(machine__id=m.id, filename=fn)
                
                code = i.body
                highlighted_code = highlight(code, l, HtmlFormatter())
        
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
                
                apacheconfig_includes.append([fn, i.id, i, body])
            except ApacheConfig.DoesNotExist:
                pass


    '''
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
    '''

    all_domains = get_all_domains()
    all_directives = get_all_directives()


    template_context = {'query': query,
                        'machine': p,
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
                        'all_domains': all_domains,
                        'all_directives': all_directives}
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
                        'terms': terms}
    return render_to_response('machines/search.html', template_context,
        context_instance=RequestContext(request))


def httpd_conf(request, machine_slug, ac_id):
    m = get_object_or_404(Machine, hostname=machine_slug)
    ac = get_object_or_404(ApacheConfig, id=ac_id)

    code = ac.body
    highlighted_code = highlight(code, ApacheConfLexer(), HtmlFormatter())

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

    query = request.GET.get('q', '')
    template_context = {'machine': m,
                        'query': query,
                        'ac': ac,
                        'ac_body': body}
    return render_to_response('machines/httpd_conf.html', template_context,
        context_instance=RequestContext(request))


def history_iptables(request, machine_slug, version_number, compare_with='previous'):
    m = get_object_or_404(Machine, hostname=machine_slug)
    query = request.GET.get('q', '')
    v_num = int(version_number)

    iptables_current = ''
    iptables_previous = ''

    iptables_history = IPTableInfo.objects.filter(machine__id=m.id).order_by(
        '-date_added').all()

    if iptables_history.exists():
        if compare_with == 'current':
            iptables_current = iptables_history[0].body

        obj_versions = Version.objects.get_for_object(
            iptables_history[0]).order_by('revision')
        if obj_versions:
            try:
                if compare_with == 'current':
                    iptables_previous = obj_versions[v_num - 1].field_dict['body']
                elif compare_with == 'previous':
                    iptables_current = obj_versions[v_num - 1].field_dict['body']
                    iptables_previous = obj_versions[v_num - 2].field_dict['body']
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
                        'iptables_current': iptables_current,
                        'iptables_previous': iptables_previous,
                        'version_current': str(v_num),
                        'version_previous': str(v_num_previous),
                        'older_version': str(older_version),
                        'newer_version': str(newer_version),
                        'compare_with': compare_with,}
    return render_to_response('machines/iptables.html', template_context,
        context_instance=RequestContext(request))


# View that that returns the JSON result.
def apache(request, machine_slug):
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

