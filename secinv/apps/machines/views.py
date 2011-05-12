import re

from django.core.urlresolvers import reverse
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import (login_required,
                                            permission_required)
from django.http import (HttpResponse, HttpResponseRedirect,
                         HttpResponseNotFound, Http404)
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.html import escape
from django.views.decorators.http import require_GET, require_POST

from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter
from pygments.lexers import ApacheConfLexer
from reversion.models import Version

from apps.decorators import json_view
from apps.json_field import JSONField
from .models import (Machine, Services, System, RPMs, Interface, SSHConfig,
                     IPTables, ApacheConfig, PHPConfig, MySQLConfig)
from .forms import MachineSearchForm
from .utils import (diff_list, diff_dict, get_version_diff,
                    get_version_diff_field, get_params)


LIMIT_PER_PAGE = 5

DIFF_SECTION_SLUGS = ['iptables', 'apacheconfig', 'phpconfig', 'mysqlconfig',
                     'sshconfig']
CONFIG_SECTIONS = ['apacheconfig', 'phpconfig', 'mysqlconfig', 'sshconfig']
DATATABLES_SECTIONS = ['machines']
DATATABLES_COLUMNS = {'machines': ['id', 'sys_ip', 'hostname', 'ext_ip']}
DATATABLES_FIELDS = {'machines': ['id', 'sys_ip', 'hostname', 'ext_ip',
                                  'httpd', 'mysqld', 'openvpn', 'nfs',
                                  'date_added', 'date_scanned']}
DATATABLES_TABLES = {'machines': 'machines_machine'}


def compare_second(a, b):
    return cmp(a[1], b[1])


def get_all_domains():
    all_domains = []
    ac = ApacheConfig.objects.filter(active=True).values_list(
        'machine__hostname', 'domains', 'machine__id')
    for c in ac:
        m_hn, domains, m_id = c
        domains = JSONField().to_python(domains).keys()
        for d in domains:
            label = '%s (%s)' % (d, m_hn)
            all_domains.append((m_hn, label, m_id))
    all_domains.sort(compare_second)
    return all_domains


def get_all_machines(order_by='id'):
    return Machine.objects.all().order_by(order_by)


# TODO: Apache Parser -- Force directives to be uppercased.
def get_all_directives(keys=False):
    """Returns directives from ApacheConfig files."""
    a_all = ApacheConfig.objects.filter(active=True).values_list('directives')
    return get_params(a_all, keys)


def get_all_items(section_slug, keys=False):
    """Returns items from PHP, MySQL, or SSH config files."""
    if section_slug not in CONFIG_SECTIONS:
        raise ValueError
    if section_slug == 'phpconfig':
        a_all = PHPConfig.objects.filter(active=True).values_list('items')
    elif section_slug == 'mysqlconfig':
        a_all = MySQLConfig.objects.filter(active=True).values_list('items')
    elif section_slug == 'sshconfig':
        a_all = SSHConfig.objects.filter(active=True).values_list('items')
    return get_params(a_all, keys)


@login_required
def index(request):
    """Machines index page."""
    return render_to_response('machines/index.html', {},
                              context_instance=RequestContext(request))


def recurse_ac_includes(ac, field_name='filename'):
    ac_includes = []
    for fn in ac.included:
        try:
            i_ac = ApacheConfig.objects.get(machine__id=ac.machine_id,
                                            filename=fn, active=True)

            l = i_ac.__getattribute__(field_name)

            if i_ac.included:
                l = [i_ac.__getattribute__(field_name),
                     recurse_ac_includes(i_ac)]

            ac_includes.append(l)
        except ApacheConfig.DoesNotExist:
            pass

    return ac_includes


@login_required
def detail(request, machine_slug):
    m = get_object_or_404(Machine, hostname=machine_slug)

    ## System.
    system_latest = []
    system_versions = []
    system_history = System.objects.filter(machine__id=m.id).order_by(
        '-date_added').all()

    if system_history.exists():
        system_latest = system_history[0]

        # Get historical versions of System objects.
        system_versions = get_version_diff(system_history[0])

    ## Services.
    services_latest = []
    services_versions = []
    services_history = Services.objects.filter(machine__id=m.id).order_by(
        '-date_added').all()

    if services_history.exists():
        services_latest = services_history[0]

        # Get historical versions of Services objects.
        services_versions = get_version_diff(services_history[0], '|')


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


    ## SSH configuration file.
    sshconfig_latest = []
    sshconfig_versions = []
    sshconfig_history = SSHConfig.objects.filter(machine__id=m.id, active=True
        ).order_by('-date_added').all()

    if sshconfig_history.exists():
        sshconfig_latest = sshconfig_history[0]

        sshconfig_versions = get_version_diff_field(sshconfig_history[0],
                                                    'body')


    ## RPMs.
    rpms_list = []
    rpms_date_added = None
    rpms_versions = []
    rpms_history = RPMs.objects.filter(machine__id=m.id).order_by(
        '-date_added').all()

    if rpms_history.exists():
        rpms_list = rpms_history[0].v_rpms.split('\n')
        rpms_date_added = rpms_history[0].date_added

        rpms_versions = get_version_diff(rpms_history[0], '\n')

    rpms_latest = {'installed': rpms_list, 'date_added': rpms_date_added}


    ## iptables.
    iptables_latest = []
    iptables_versions = []
    iptables_history = IPTables.objects.filter(machine__id=m.id).order_by(
        '-date_added').all()

    if iptables_history.exists():
        iptables_latest = iptables_history[0]

        iptables_versions = get_version_diff_field(iptables_history[0],
                                                   'body')


    ## Apache configuration files.
    apacheconfig_latest = []
    apacheconfig_includes = []
    ac_includes = []
    apacheconfig_history = ApacheConfig.objects.filter(machine__id=m.id,
        active=True).order_by('-date_added').all()


    # Get historical versions of ApacheConfig objects.
    apacheconfig_versions = []
    for a_h in apacheconfig_history:
        a_v = get_version_diff_field(a_h, 'body')
        apacheconfig_versions += a_v

    if apacheconfig_versions:
        apacheconfig_versions = sorted(apacheconfig_versions,
                                       key=lambda k: k['timestamp'],
                                       reverse=True)

    apacheconfig_latest_body = ''
    if apacheconfig_history.exists():
        try:
            apacheconfig_latest = ApacheConfig.objects.filter(
                machine__id=m.id, filename__endswith='/httpd.conf',
                active=True).order_by('-date_added').all()[0]
        except:
            pass

        try:
            apacheconfig_latest_body = highlight(apacheconfig_latest.body,
                                                 ApacheConfLexer(),
                                                 HtmlFormatter())

            body = ''
            lines = apacheconfig_latest_body.split('\n')
            for line in lines:
                ls = line.replace('<span class="nb">', '').replace('</span>', '').split()
                if len(ls) == 2 and ls[0].lower() == 'include':
                    # Strip quotation marks, if available, for filenames.
                    if ls[1][0] == ls[1][-1] and ls[1][0] in ('"', "'"):
                        ls[1] = ls[1:-1]

                    try:
                        a = ApacheConfig.objects.get(machine__id=m.id,
                            filename__endswith=ls[1],
                            active=True)
                        i_fn = '<a href="%s">%s</a>' % (a.get_absolute_url(), ls[1])
                    except (ApacheConfig.DoesNotExist,
                            ApacheConfig.MultipleObjectsReturned):
                        i_fn = '%s' % ls[1]

                    line = '<span class="nb">%s</span> %s' % (ls[0], i_fn)
                body += '%s\n' % line
            apacheconfig_latest_body = body
        except TypeError:
            apacheconfig_latest_body = apacheconfig_latest.body


        for fn in apacheconfig_latest.included:
            try:
                i_ac = ApacheConfig.objects.get(machine__id=m.id, filename=fn,
                                                active=True)

                apacheconfig_includes.append(i_ac)
            except ApacheConfig.DoesNotExist:
                pass

        # Recurse includes.
        ac_includes = recurse_ac_includes(apacheconfig_latest)


    ## PHP configuration file.
    phpconfig_latest = []
    phpconfig_versions = []
    phpconfig_history = PHPConfig.objects.filter(machine__id=m.id, active=True
        ).order_by('-date_added').all()

    if phpconfig_history.exists():
        phpconfig_latest = phpconfig_history[0]

        phpconfig_versions = get_version_diff_field(phpconfig_history[0],
                                                    'body')


    ## MySQL configuration file.
    mysqlconfig_latest = []
    mysqlconfig_versions = []
    mysqlconfig_history = MySQLConfig.objects.filter(machine__id=m.id,
        active=True).order_by('-date_added').all()

    if mysqlconfig_history.exists():
        mysqlconfig_latest = mysqlconfig_history[0]

        mysqlconfig_versions = get_version_diff_field(mysqlconfig_history[0],
                                                      'body')


    template_context = {'machine': m,
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
                        'phpconfig': phpconfig_latest,
                        'phpconfig_versions': phpconfig_versions,
                        'mysqlconfig': mysqlconfig_latest,
                        'mysqlconfig_versions': mysqlconfig_versions,}
    return render_to_response('machines/detail.html', template_context,
                              context_instance=RequestContext(request))


@login_required
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
                        'terms': terms,}
    return render_to_response('machines/search.html', template_context,
        context_instance=RequestContext(request))


@login_required
def apacheconfig(request, machine_slug, ac_id):
    m = get_object_or_404(Machine, hostname=machine_slug)
    ac = get_object_or_404(ApacheConfig, id=ac_id)

    highlighted_code = highlight(ac.body, ApacheConfLexer(), HtmlFormatter())

    # TODO: ADD AS FILTER.
    body = ''
    lines = highlighted_code.split('\n')
    for line in lines:
        ls = line.replace('<span class="nb">', '').replace('</span>', '').split()
        if len(ls) == 2 and ls[0].lower() == 'include':
            if ls[1][0] == ls[1][-1] and ls[1][0] in ('"', "'"):
                ls[1] = ls[1:-1]

            try:
                a = ApacheConfig.objects.get(machine__id=m.id,
                                             filename__endswith=ls[1],
                                             active=True)
                i_fn = '<a href="%s">%s</a>' % (a.get_absolute_url(), ls[1])
            except (ApacheConfig.DoesNotExist,
                    ApacheConfig.MultipleObjectsReturned):
                i_fn = '%s' % ls[1]

            line = '<span class="nb">%s</span> %s' % (ls[0], i_fn)
        body += '%s\n' % line

    # Get historical versions of ApacheConfig object.
    apacheconfig_versions = get_version_diff_field(ac, 'body')

    # Get includes.
    apacheconfig_includes = []
    for fn in ac.included:
        try:
            i_ac = ApacheConfig.objects.get(machine__id=m.id, filename=fn,
                                            active=True)

            apacheconfig_includes.append(i_ac)
        except ApacheConfig.DoesNotExist:
            pass

    # Recurse includes.
    ac_includes = recurse_ac_includes(ac)

    template_context = {'machine': m,
                        'ac': ac,
                        'ac_body': body,
                        'apacheconfig_versions': apacheconfig_versions,
                        'apacheconfig_includes': apacheconfig_includes,
                        'ac_includes': ac_includes}
    return render_to_response('machines/apacheconfig.html', template_context,
        context_instance=RequestContext(request))


@login_required
def diff(request, machine_slug, section_slug, version_number,
         compare_with='previous', item_id=None):
    if section_slug not in DIFF_SECTION_SLUGS:
        raise Http404

    m = get_object_or_404(Machine, hostname=machine_slug)
    v_num = int(version_number)

    body_current = ''
    body_previous = ''

    if section_slug == 'iptables':
        past_history = IPTables.objects.filter(machine__id=m.id).order_by(
            '-date_added').all()
    elif section_slug == 'apacheconfig':
        past_history = ApacheConfig.objects.filter(machine__id=m.id,
            id=item_id, active=True).order_by('-date_added').all()
    elif section_slug == 'phpconfig':
        past_history = PHPConfig.objects.filter(machine__id=m.id,
            active=True).order_by('-date_added').all()
    elif section_slug == 'mysqlconfig':
        past_history = MySQLConfig.objects.filter(machine__id=m.id,
            active=True).order_by('-date_added').all()


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

            num_vers = len(obj_versions)

            if compare_with == 'current':
                if (v_num - 2) < num_vers:
                    older_version = v_num - 1 # index + 1
                if v_num < num_vers:
                    newer_version = v_num + 1
            elif compare_with == 'previous':
                if (v_num - 3) < num_vers:
                    older_version = v_num - 2
                if v_num < num_vers:
                    newer_version = v_num + 1

            if older_version < 0:
                older_version = ''
            if newer_version < 0:
                newer_version = ''
    else:
        raise Http404

    v_num_previous = 0
    if v_num > 0:
        v_num_previous = v_num - 1

    template_context = {'machine': m,
                        'section': section_slug,
                        'obj_current': past_history[0],
                        'body_current': body_current,
                        'body_previous': body_previous,
                        'version_current': str(v_num),
                        'version_previous': str(v_num_previous),
                        'older_version': str(older_version),
                        'newer_version': str(newer_version),
                        'compare_with': compare_with}
    return render_to_response('machines/diff.html', template_context,
                              context_instance=RequestContext(request))


@login_required
@json_view
def ac_filter_directives_keys(request):
    return get_all_directives(keys=True)


@login_required
@require_POST
@json_view
def ac_filter_directives(request):
    result = ''
    parameter = request.POST.get('parameter', '')
    dirs = dict(get_all_directives())
    result = dirs[parameter]
    return result


@login_required
@json_view
def conf_filter_parameters_keys(request, section_slug):
    if section_slug == 'apacheconfig':
        params = get_all_directives(keys=True)
    elif section_slug in ('phpconfig', 'mysqlconfig', 'sshconfig'):
        params = get_all_items(section_slug, keys=True)
    return params


@login_required
@require_POST
@json_view
def conf_filter_parameters(request, section_slug):
    if section_slug not in CONFIG_SECTIONS:
        return HttpResponse(status=400)
    result = ''
    parameter = request.POST.get('parameter', '')
    if section_slug == 'apacheconfig':
        params = get_all_directives()
    elif section_slug in ('phpconfig', 'mysqlconfig', 'sshconfig'):
        params = get_all_items(section_slug)
    parms = dict(params)
    result = dirs[parameter]
    return result


@login_required
@require_GET
def machine_filter(request):
    """Find machine by hostname, IP, or domain and redirect."""
    hostname = request.GET.get('machine_hostname', '')
    ip = request.GET.get('machine_ip', '')
    domain = request.GET.get('machine_domain', '')

    m_hn = hostname or ip or domain

    if m_hn:
        m = get_object_or_404(Machine, hostname=m_hn)
        destination = reverse('machines-detail', args=[m.hostname])
    else:
        destination = reverse('machines-index')

    return HttpResponseRedirect(destination)


@login_required
def conf_filter_results(request, section_slug):
    """Filter other configuration objects by parameters and values."""
    if section_slug not in CONFIG_SECTIONS:
        return HttpResponse(status=400)

    conf_parameter = request.GET.get('conf_parameter', '')
    conf_value = request.GET.get('conf_value', '')

    a_all = []
    results = []

    # Field name for dictionary of parameters/values.
    params_field = 'items'

    if section_slug == 'apacheconfig':
        a_all = ApacheConfig.objects.filter(active=True).all()
        params_field = 'directives'
    elif section_slug == 'phpconfig':
        a_all = PHPConfig.objects.filter(active=True).all()
    elif section_slug == 'mysqlconfig':
        a_all = MySQLConfig.objects.filter(active=True).all()
    elif section_slug == 'sshconfig':
        a_all = SSHConfig.objects.filter(active=True).all()

    for a in a_all:
        if a.__getattribute__(params_field):
            for param, values in a.__getattribute__(params_field).iteritems():
                if param == conf_parameter or not conf_parameter:
                    for v in values:
                        if conf_value == v or not conf_value:
                            results.append((param, v, a))

    results = sorted(results)

    template_context = {'conf_parameter': conf_parameter,
                        'conf_value': conf_value,
                        'results': results,
                        'section_slug': section_slug}
    return render_to_response('machines/conf_results.html', template_context,
                              context_instance=RequestContext(request))


@staff_member_required
@permission_required('machines.add_machine')
@permission_required('machines.add_authtoken')
@require_POST
@json_view
def add_multiple_machines(request):
    template_context = {}
    return render_to_response('machines/add_multiple_machines.html',
                              template_context,
                              context_instance=RequestContext(request))


@login_required
@json_view
def datatables(request, section_slug):
    if section_slug not in DATATABLES_SECTIONS:
        raise Http404

    s_columns = DATATABLES_COLUMNS[section_slug]
    s_fields = DATATABLES_FIELDS[section_slug]
    s_table = DATATABLES_TABLES[section_slug]

    try:
        s_index = s_columns[s_columns.index('id')]
    except ValueError:
        s_index = s_columns[0]

    result = ''

    # Paging.
    i_display_length = int(escape(request.GET.get('iDisplayLength', '0')))
    s_limit = ''
    if i_display_length and i_display_length != -1:
        i_display_start = int(escape(request.GET.get('iDisplayStart', '0')))
        s_limit = "LIMIT %s, %s" % (i_display_start, i_display_length)

    # Ordering.
    i_sort_col_0 = escape(request.GET.get('iSortCol_0', ''))
    s_order = ''
    s_order_by = []
    if i_sort_col_0:
        s_orders = []
        for i in xrange(int(escape(request.GET.get('iSortingCols', '')))):
            i_sort_col_i = escape(request.GET.get('iSortCol_%s' % i, ''))
            if request.GET.get('bSortable_%s' % i_sort_col_i) == 'true':
                s_orders.append(' '.join([s_fields[int(i_sort_col_i)],
                    escape(request.GET.get('sSortDir_%s' % i))]))

                s_order_by.append((int(i_sort_col_i),
                                  escape(request.GET.get('sSortDir_%s' % i))))

        if s_orders:
            s_order = 'ORDER BY %s' % ', '.join(s_orders)


    # Filtering.
    s_where = ''
    s_search = escape(request.GET.get('sSearch', ''))
    if s_search:
        s_likes = []
        for value in s_columns:
            s_likes.append("%s LIKE '%%%s%%'" % (value, s_search))
        s_where = 'WHERE (%s)' % (' OR '.join(s_likes))

    for index, value in enumerate(s_columns):
        i_index = request.GET.get('sSearch_%s' % index)
        if request.GET.get('bSearchable_%s' % index) == 'true' and i_index:
            if s_where:
                s_where += ' AND '
            else:
                s_where = 'WHERE '
            s_where += "%s LIKE '%%%s%%'" % (value, escape(i_index))

    from django.db import connection
    cursor = connection.cursor()

    r = Machine.objects.raw("SELECT SQL_CALC_FOUND_ROWS %s FROM %s %s %s" % (
        ', '.join(s_columns), s_table, s_where.replace('%', '%%'), s_limit))

    r_l = list(r)
    aa_data = [r.__getattribute__('json_data')() for r in r_l]

    i_filtered_total = len(r_l)

    cursor.execute("SELECT COUNT(%s) AS count FROM %s" % (s_index, s_table))
    i_total = int(cursor.fetchone()[0])

    for s in s_order_by:
        s_by, s_order = s

        def compare_order_by(a, b):
            return cmp(a[s_by], b[s_by])

        aa_data.sort(compare_order_by)

        if s_order == 'desc':
            aa_data.reverse()

    result = {'sEcho': int(escape(request.GET.get('sEcho', '0'))),
              'iTotalRecords': i_total,
              'iTotalDisplayRecords': i_filtered_total,
              'aaData': aa_data}

    return result
