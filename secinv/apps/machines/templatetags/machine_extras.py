from django import template
from django.utils.safestring import mark_safe, SafeData
from django.template.defaultfilters import stringfilter

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
