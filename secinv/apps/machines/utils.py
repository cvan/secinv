import difflib
import re

from reversion.models import Version


def diff_html(text_a, text_b):
    """Create a 'diff' from text_a to text_b."""
    d = difflib.HtmlDiff()
    return d.make_file(text_a.splitlines(1), text_b.splitlines(1))


def diff_table(text_a, text_b):
    """Create a 'diff' from text_a to text_b."""
    d = difflib.HtmlDiff()
    return d.make_table(text_a.splitlines(1), text_b.splitlines(1)).replace(
           '&nbsp;', ' ').replace('nowrap="nowrap"',
           'class="diff_text"').encode('utf-8')


def diff_list(l_old, l_new):
    """Creates a new dictionary representing a difference between two lists."""
    set_old, set_new = set(l_old), set(l_new)
    intersect = set_new.intersection(set_old)

    added = list(set_new - intersect)
    removed = list(set_old - intersect)

    return {'added': added, 'removed': removed}


def diff_dict(a, b, delimiter=None):
    """
    Returns the differences from dictionaries a to b.

    Returns a dictionary of four dictionaries:
    (removed, added, changed, unchanged).
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
            b = a_pair_v + b_pair_v

        if value_name:
            diffs['pair'] = {'merged': b, 'diff': pair}

    return diffs


def get_version_diff(obj_item, delimiter=None):
    """
    Returns a dictionary of fields and differences for each historical version
    of the selected model.
    """
    obj_version = Version.objects.get_for_object(obj_item).order_by('revision')
    versions = []
    for index, ver in enumerate(obj_version):
        try:
            old_v = obj_version[index - 1].field_dict
        except AssertionError:
            old_v = {}

        patch = diff_dict(old_v, ver.field_dict, delimiter)
        new_fields = ver.field_dict

        # If there are old fields, merge the dictionaries.
        if old_v:
            new_fields = dict(old_v, **ver.field_dict)

        versions.append({'fields': new_fields, 'diff': patch,
                         'timestamp': ver.field_dict['date_added'],
                         'version': index + 1})
    versions.reverse()
    return versions


def get_version_diff_field(obj_item, field_name):
    """
    Generates pygments differences for each version of `obj_item`.`field`.
    Returns a dictionary of fields and differences for the `field` for each
    historical version of the selected model.
    """
    from pygments import highlight
    from pygments.lexers import PythonLexer
    from pygments.formatters import HtmlFormatter
    from pygments.lexers import guess_lexer
    from pygments.filters import VisibleWhitespaceFilter

    from reversion.helpers import generate_patch
    from diff_match_patch import diff_match_patch

    obj_version = Version.objects.get_for_object(obj_item).order_by('revision')
    versions = []
    is_newest = False
    for index, ver in enumerate(obj_version):
        try:
            if index == (len(obj_version) - 1):
                is_newest = True

            old_v = obj_version[index - 1]

            try:
                code = generate_patch(old_v, ver, field_name)

                l = guess_lexer(patch_txt)
                l.add_filter(VisibleWhitespaceFilter(newlines=True))
                #diff_highlighted = highlight(code, PythonLexer(), HtmlFormatter())
                diff_highlighted = highlight(code, l, HtmlFormatter())
            except:
                diff_highlighted = old_v
        except AssertionError:
            '''
            dmp = diff_match_patch()
            diffs = dmp.diff_main('', ver.field_dict[field_name].replace('\r',''))
            patch = dmp.patch_make(diffs)
            patch_txt = dmp.patch_toText(patch)

            #diff_highlighted = highlight(patch_txt, PythonLexer(), HtmlFormatter())
            l = guess_lexer(patch_txt)
            l.add_filter(VisibleWhitespaceFilter(newlines=True))
            diff_highlighted = highlight(patch_txt, l, HtmlFormatter())
            '''

            patch_txt = ver.field_dict[field_name]
            try:
                # Guess a lexer by the contents of the block.
                l = guess_lexer(patch_txt)

                l.add_filter(VisibleWhitespaceFilter(newlines=True))
                diff_highlighted = highlight(patch_txt, l, HtmlFormatter())
            except:
                diff_highlighted = patch_txt


        versions.append({'fields': ver.field_dict, 'diff': diff_highlighted,
                         'timestamp': ver.field_dict['date_added'],
                         'version': index + 1, 'is_newest': is_newest})
    versions.reverse()
    return versions

