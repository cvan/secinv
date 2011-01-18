from functools import wraps

from django.http import HttpResponse
from django.utils import simplejson


def json_view(f):
    @wraps(f)
    def wrapper(*args, **kw):
        response = f(*args, **kw)
        if isinstance(response, HttpResponse):
            return response
        else:
            return HttpResponse(simplejson.dumps(response),
                                content_type='application/json')
    return wrapper


json_view.error = lambda s: HttpResponseBadRequest(
    simplejson.dumps(s), content_type='application/json')
