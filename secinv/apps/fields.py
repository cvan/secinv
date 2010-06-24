from django.db import models

import base64

try:
    import cPickle as pickle
except ImportError:
    import pickle

'''
class SerializedDataField(models.TextField):
    """
    Because Django for some reason feels its needed to repeatedly call
    to_python even after it's been converted this does not support strings.
    """
    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        if value is None:
            return
        if not isinstance(value, basestring):
            return value
        value = pickle.loads(base64.b64decode(value))
        return value

    def get_db_prep_save(self, value):
        if value is None:
            return
        return base64.b64encode(pickle.dumps(value))
'''


class SerializedTextField(models.TextField):
    """
    A field which serializes python values to the database, and returns
    them intact.
    """
    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        if value is None or value is '':
            return
        if not isinstance(value, basestring):
            return value
        try:
            return pickle.loads(base64.b64decode(value))
        except:
            return

    def get_db_prep_save(self, value):
        if value is None or value is '':
            return
        return base64.b64encode(pickle.dumps(value))


class CompressedTextField(models.TextField):
    """
    model Fields for storing text in a compressed format (bz2 by default).
    """
    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        if not value:
            return value

        try:
            return value.decode('base64').decode('bz2').decode('utf-8')
        except Exception:
            return value

    def get_prep_value(self, value):
        if not value:
            return value

        try:
            value.decode('base64')
            return value
        except Exception:
            try:
                tmp = value.encode('utf-8').encode('bz2').encode('base64')
            except Exception:
                return value
            else:
                if len(tmp) > len(value):
                    return value

                return tmp

