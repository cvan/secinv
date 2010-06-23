from django.db.models import get_model
from django import template
from django.template.defaultfilters import stringfilter
from django.utils.encoding import force_unicode, iri_to_uri
from django.utils.safestring import mark_safe, SafeData
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext

from .. import utils
from ..models import ApacheConfig

import re

register = template.Library()

@register.filter
@stringfilter
def split_as_list(value, splitter=',', autoescape=None):
    if not isinstance(value, SafeData):
        value = mark_safe(value)
    value = value.split(splitter)
    #iresult = ""
    #for v in value:
    #    result += '<option value="%s">%s</option>\n' % (v, v)
    return value
split_as_list.is_safe = True
split_as_list.needs_autoescape = True

def dict_get(value, arg):
    #custom template tag used like so:
    #{{dictionary|dict_get:var}}
    #where dictionary is duh a dictionary and var is a variable representing
    #one of it's keys

    return value[arg]

register.filter('dict_get', dict_get)

'''
@register.filter
def diff(value, arg, autoescape=None):
    # value = sytem
    if arg in value['diff']['added']:
        result = '<ins>%s</ins>' % value['fields'][arg]

    if arg in value['diff']['changed']:
        result = '<mark>%s</mark>' % value['fields'][arg]

    if arg in value['diff']['removed']:
        result = '<del>%s</del>' % value['fields'][arg]

    if arg in value['diff']['unchanged']:
        result = '%s' % value['fields'][arg]

    return result
diff.is_safe = True
diff.needs_autoescape = True


@register.filter
def diff(value, arg, autoescape=False):
    # value = sytem
    if arg in value['diff']['added']:
        result = '<ins>%s</ins>' % value['fields'][arg]

    if arg in value['diff']['changed']:
        result = '<mark>%s</mark>' % value['fields'][arg]

    if arg in value['diff']['removed']:
        result = '<del>%s</del>' % value['fields'][arg]

    if arg in value['diff']['unchanged']:
        result = '%s' % value['fields'][arg]

    return result
diff.is_safe = True
diff.needs_autoescape = True
'''


@register.filter
def enum(value, arg, autoescape=False):
    if autoescape:
        from django.utils.html import conditional_escape
        escaper = conditional_escape
    else:
        escaper = lambda x: x

    choices = arg.split(',')
    yes = ugettext('%(yes)s') % {'yes': escaper(force_unicode(choices[0]))}
    no = ugettext('%(no)s') % {'no': escaper(force_unicode(choices[1]))}
    return yes if value else no
enum.is_safe = True
enum.needs_autoescape = True


'''
from ..models import *
def do_latest_content(parser, token):
    bits = token.split_contents()
    if len(bits) != 5:
        raise template.TemplateSyntaxError("'get_latest_content' tag takes exactly four arguments")
    model_args = bits[1].split('.')
    model = get_model(model_args[0], model_args[1])
    return LatestContentNode(model, bits[2], bits[4])
'''

'''
def do_latest_content(parser, token):
    bits = token.split_contents()
    if len(bits) != 5:
        raise template.TemplateSyntaxError("'get_latest_content' tag takes exactly four arguments")

    model_args = bits[1].split('.')
    if len(model_args) != 2:
        raise template.TemplateSyntaxError("First argument to 'get_latest_content' must be an 'application name'.'model name' string")
        model = get_model(*model_args)
        if model is None:
            raise template.TemplateSyntaxError("'get_latest_content' tag got an invalid model: %s" % bits[1])
        return LatestContentNode(model, bits[2], bits[4])
    #return ''


class LatestContentNode(template.Node):
    def __init__(self, model, num, varname):
        self.model = model
        self.num = int(num)
        self.varname = varname

    def render(self, context):
        context[self.varname] = self.model._default_manager.all()[:self.num]
        #context[self.varname] = self.model.objects.all()[:self.num]
        return ''

register.tag('get_latest_content', do_latest_content)
'''



class DifferNode(template.Node):
    def __init__(self, nodelist, diff_dict, field_name):
        self.nodelist = nodelist
        self.diff_dict = diff_dict
        self.field_name = field_name

    def render(self, context):
        # Remove quotation marks from string value.
        field_name = self.field_name
        if field_name[0] in ('"', "'") and field_name[0] == field_name[-1]:
            field_name = field_name[1:-1]
        else:
            field_name = template.Variable(field_name).resolve(context)


        diff_dict = template.Variable(self.diff_dict).resolve(context)

        emphasis_tag = ''

        if 'added' in diff_dict and field_name in diff_dict['added']:
            emphasis_tag = 'ins'

        if 'changed' in diff_dict and field_name in diff_dict['changed']:
            emphasis_tag = 'mark'

        if 'removed' in diff_dict and field_name in diff_dict['removed']:
            emphasis_tag = 'del'

        output = self.nodelist.render(context)

        emphasis_start = ('<%s>' % emphasis_tag) if len(emphasis_tag) else ''
        emphasis_end = ('</%s>' % emphasis_tag) if len(emphasis_tag) else ''

        return '%s%s%s' % (emphasis_start, output, emphasis_end)


@register.tag
def differ(parser, token):
    """
    This wraps the enclosed text with the appropriate element: ins, mark, del.

    Requires two arguments: (1) a dictionary of the field differences,
    and (2) a string of the field name.

    Example::

        {% differ system.diff 'rh_rel' %}{{ system.fields.rh_rel }}{% enddiffer %}
    """

    bits = token.split_contents()

    if len(bits) != 3:
        raise template.TemplateSyntaxError('%r tag requires two arguments.' % bits[0])

    diff_dict = bits[1]
    field_name = bits[2]


    nodelist = parser.parse(('enddiffer',))
    parser.delete_first_token()
    return DifferNode(nodelist, diff_dict, field_name)
#differ = register.tag(differ)




class SplitAsListNode(template.Node):
    def __init__(self, source_list, destination_list, delimiter=','):
        self.source_list = source_list
        self.destination_list = destination_list
        self.delimiter = delimiter

    def render(self, context):
        source_list = template.Variable(self.source_list).resolve(context)
        new_list = source_list.split(self.delimiter)
        context[self.destination_list] = new_list
        return ''


@register.tag
def split_as_list(parser, token):
    """
    This wraps the enclosed text with the appropriate element: ins, mark, del.

    Requires two arguments: (1) a string delimited by some character,
    and (2) a string of the destination list name.

    Optional first argument: (1) delimiter.

    Example::

        {% split_as_list services.processes as processes_list %}

        or

        {% split_as_list ',' services.processes as processes_list %}
    """

    bits = token.split_contents()
    num_bits = len(bits)

    if num_bits != 4 and num_bits != 5:
        raise template.TemplateSyntaxError('%r tag requires at least four arguments (at most five).' % bits[0])
    elif (bits[2] != 'as' and num_bits == 4) or (bits[3] != 'as' and num_bits == 5):
        raise template.TemplateSyntaxError("%r tag must contain an 'as' argument." % bits[0])

    source_string = bits[1]
    destination_list = bits[3]

    # Remove quotation marks from string value.
    delimiter = ','
    if num_bits == 5:
        delimiter = bits[1]
        if delimiter[0] in ('"', "'") and delimiter[0] == delimiter[-1]:
            delimiter = delimiter[1:-1]

        source_string = bits[2]
        destination_list = bits[4]

    return SplitAsListNode(source_string, destination_list, delimiter)



def autolinebreaks(value, autoescape=None):
    """
    Checks if the content is HTML or plain text. If plain text ,
    line breaks are replaced with the appropriate HTML; a single
    newline becomes an HTML line break (`<br>`) and a new line
    followed by a blank line becomes a paragraph break (`</p>`).
    """
    import re
    html_match = re.compile('<br>|<br />|<p>|<table>', re.IGNORECASE)
    if not html_match.search(value):
        from django.utils.html import linebreaks
        autoescape = autoescape and not isinstance(value, SafeData)
        return mark_safe(linebreaks(value, autoescape).replace('<br />', '<br>\n'))
    else:
        return value.replace('<br />', '<br>\n')
autolinebreaks.is_safe = True
autolinebreaks.needs_autoescape = True
autolinebreaks = stringfilter(autolinebreaks)
register.filter(autolinebreaks)


def engine(f):
    def apply(text_a, text_b):
        # Don't need to consider autoescape because difflib does the escaping.
        return mark_safe(f(text_a, text_b))
    return apply

register.filter('diff_html', engine(utils.diff_html))
register.filter('diff_table', engine(utils.diff_table))


@register.filter
def unordered_list_dl(value, autoescape=None):
    """
    Recursively takes a self-nested list and returns an HTML unordered list --
    WITHOUT opening and closing <ul> tags.

    The list is assumed to be in the proper format. For example, if ``var``
    contains: ``['States', ['Kansas', ['Lawrence', 'Topeka'], 'Illinois']]``,
    then ``{{ var|unordered_list_dl }}`` would return::

        <li>States
        <ul>
                <li>Kansas
                <ul>
                        <li>Lawrence</li>
                        <li>Topeka</li>
                </ul>
                </li>
                <li>Illinois</li>
        </ul>
        </li>
    """
    if autoescape:
        from django.utils.html import conditional_escape
        escaper = conditional_escape
    else:
        escaper = lambda x: x
    def convert_old_style_list(list_):
        """
        Converts old style lists to the new easier to understand format.

        The old list format looked like:
            ['Item 1', [['Item 1.1', []], ['Item 1.2', []]]

        And it is converted to:
            ['Item 1', ['Item 1.1', 'Item 1.2]]
        """
        if not isinstance(list_, (tuple, list)) or len(list_) != 2:
            return list_, False
        first_item, second_item = list_
        if second_item == []:
            return [first_item], True
        old_style_list = True
        new_second_item = []
        for sublist in second_item:
            item, old_style_list = convert_old_style_list(sublist)
            if not old_style_list:
                break
            new_second_item.extend(item)
        if old_style_list:
            second_item = new_second_item
        return [first_item, second_item], old_style_list

    def _helper(list_, tabs=1):
        indent = u'    ' * tabs
        output = []

        list_length = len(list_)
        i = 0
        while i < list_length:
            title = list_[i]
            sublist = ''
            sublist_item = None
            if isinstance(title, (list, tuple)):
                sublist_item = title
                title = ''
            elif i < list_length - 1:
                next_item = list_[i+1]
                if next_item and isinstance(next_item, (list, tuple)):
                    # The next item is a sub-list.
                    sublist_item = next_item
                    # We've processed the next item now too.
                    i += 1
            if sublist_item:
                sublist = _helper(sublist_item, tabs+1)
                sublist = '\n%s<ul>\n%s\n%s</ul>\n%s' % (indent, sublist,
                                                         indent, indent)
            output.append('%s<li>%s%s</li>' % (indent,
                    escaper(force_unicode(title)), sublist))
#            output.append('%s<li>%s%s</li>' % (indent,
#                    title[0], sublist))
            i += 1
        return '\n'.join(output)
    value, converted = convert_old_style_list(value)

    return mark_safe(_helper(value))

unordered_list_dl.is_safe = True
unordered_list_dl.needs_autoescape = True






class GetNestedItemsNode(template.Node):
    """
    TODO: Merge tag with 'unordered_list_dl'.
    """
    def __init__(self, nodelist, field_name, machine_id):
        self.nodelist = nodelist
        self.field_name = field_name
        self.machine_id = machine_id

    def render(self, context):
        # Remove quotation marks from string value.
        field_name = self.field_name
        machine_id = self.machine_id

        if field_name[0] in ('"', "'") and field_name[0] == field_name[-1]:
            field_name = field_name[1:-1]
        else:
            field_name = template.Variable(field_name).resolve(context)

        if machine_id[0] in ('"', "'") and machine_id[0] == machine_id[-1]:
            machine_id = machine_id[1:-1]
        else:
            machine_id = template.Variable(machine_id).resolve(context)

        content = self.nodelist.render(context)

        lines = re.split('\n', content)
        output = ''

        for line in lines:
            m = re.compile(r'(\s*)<li>(.+)</li>$').match(line)
            if m:
                ws, value = m.groups()
                closing = '</li>'
            else:
                m = re.compile(r'(\s*)<li>(.+)$').match(line)
                if m:
                    ws, value = m.groups()

                    closing = ''
                else:
                    output += '%s\n' % line
                    continue

            try:
                ac = ApacheConfig.objects.get(machine__id=machine_id, filename=value)

                domains = '\n'

                if domains:
                    domains = '<ul>\n'
                    for d in ac.domains.keys():
                        domains += '  <li>%s</li>\n' % d
                    domains += '</ul>\n'

                line = '%s<li><h6><a href="%s">%s</a></h6>%s%s' % (
                     ws, ac.get_absolute_url(), value, domains, closing)

            except ApacheConfig.DoesNotExist:
                pass

            output += '%s\n' % line



        #matches = re.findall(r'<span class="item">([^<]+)</span>', output)
        #for m in matches:
        #    print m


        return '%s' % output


@register.tag
def get_nested_items(parser, token):
    """
    This wraps the enclosed text with the appropriate element: ins, mark, del.

    Requires two arguments: (1) a dictionary of the field differences,
    and (2) a string of the field name.

    Example::

        {% get_nested_items 'filename' machine.id %}{{ ac_includes|unordered_list_dl }}{% endget_nested_items %}
    """

    bits = token.split_contents()

    if len(bits) != 3:
        raise template.TemplateSyntaxError("%r tag requires two arguments: (field name) and machine_id." % bits[0])

    field_name = bits[1]
    machine_id = bits[2]

    nodelist = parser.parse(('endget_nested_items',))
    parser.delete_first_token()
    return GetNestedItemsNode(nodelist, field_name, machine_id)

