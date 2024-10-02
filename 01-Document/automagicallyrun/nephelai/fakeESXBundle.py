
"""
Class for testing - a series of faked ESXBundle objects
"""

from .bundle import Logbundle, ESXBundle, ESXBundleBase
from .util import CachingDict
from unittest.mock import patch, mock_open
from functools import partial
import unittest.mock as mock
import json
import datetime


class BundleEncoder(json.JSONEncoder):
    """
    handle datetime objects when doing JSON encoding.
    """

    def default(self, o):
        if isinstance(o, datetime.datetime):
            return str(o.__repr__())  # eval on upstream
        elif isinstance(o, CachingDict):
            print('test')
            return dict(o)
        return json.JSONEncoder.default(self, o)


def decode_datetimes(data):
    """
    recurse through the data (dict)
    :param data:
    :return:
    """
    assert type(data) is dict
    for key, value in data.items():
        if type(value) is str:
            if value.startswith('datetime.datetime'):
                try:
                    tmp = eval(value)
                    if isinstance(tmp, datetime.datetime):
                        data[key] = tmp
                except:
                    pass
        elif type(value) is dict:
            decode_datetimes(value)


def FakeBundle(**kwargs):
    return FakeESXBundle(**kwargs)


def export_esxbundle(bundle, filename):
    """
    Given ESXBundle object create JSON export in supplied filename
    :param bundle: which object.
    :param filename: where to export to
    :return:
    """
    export = {}
    exclude_list = ['_esxcfg_info']
    for key, value in bundle.__dict__.items():
        if (value is not None) and (key.startswith('_') and not key.startswith('__')) and key not in exclude_list:
            export[key] = value
    with open(filename, mode='w', encoding='utf8') as f:
        json.dump(export, f, cls=BundleEncoder)
        print('Wrote {0}'.format(filename))


class FakeESXBundle(ESXBundleBase):

    def __init__(self, path=None, **kwargs):
        self._test_validate_response = kwargs.get('test_validate', True)

        super().__init__(path, **kwargs)

        if kwargs.get('test_json_import'):
            with open(kwargs.get('test_json_import'), encoding='utf8') as f:
                test_data = json.load(f)
                decode_datetimes(test_data)
                test_keys = test_data.keys()
                for key in test_keys:
                    if key in self.__dict__:
                        self.__dict__[key] = test_data[key]

    def _open_file(self, abspath, mode='rt', recurse=True, encoding='utf-8'):
        """
        :param abspath:
        :param mode:
        :param recurse:
        :param encoding:
        :return:
        """
        m = mock_open()
        return m()

    def validate(self):
        return self._test_validate_response
