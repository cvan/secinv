from django.db.models import get_model
from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe, SafeData
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext

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
    choices = arg.split(',')
    yes = ugettext('%(yes)s') % {'yes': choices[0]}
    no = ugettext('%(no)s') % {'no': choices[1]}
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

        {% differ system.diff 'rh_rel' %}{{ system.fields.rh_rel}}{% enddiffer %}
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


