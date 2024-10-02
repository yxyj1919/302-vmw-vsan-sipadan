import collections
import datetime


class CachingDict(collections.MutableMapping):
    """
    Implementation of dict() like object which when a value is set to a callable() will execute the callable and store
    the result in the value when initially looked at.
    """

    def __contains__(self, x):
        pass

    def __init__(self, *args, **kwargs):
        self.__dict__.update(*args, **kwargs)

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __getitem__(self, key):
        """
        Here is where most of the changes are.
        :param key:
        :return: value or results of value() if callable
        """
        if isinstance(self.__dict__[key], collections.Callable):
            self.__dict__[key] = self.__dict__[key]()
        return self.__dict__[key]

    def __delitem__(self, key):
        del self.__dict__[key]

    def __iter__(self):
        return iter(self.__dict__)

    def __len__(self):
        return len(self.__dict__)

    def has_key(self, k):
        return k in self.__dict__

    def update(self, *args, **kwds):
        self.__dict__.update(*args, **kwds)

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return '{0}, CachingDict({1})'.format(super(CachingDict, self).__repr__(), self.__dict__)


def vmw_time_parser(ts):
    """
    Takes a VMW formatted ISO8601 ts and returns tz-aware datetime object.
    :param ts: string
    :return: datetime object
    """
    format = '%Y-%m-%dT%H:%M:%S.%f%z'
    format_utc = '%Y-%m-%dT%H:%M:%S.%f'
    if ts.endswith('Z'):  # UTC
        tmp = ts.rstrip('Z') + '000'  # Pull off the UTC notation - add 0's to conv to usec
        return datetime.datetime.strptime(tmp, format_utc).replace(tzinfo=datetime.timezone.utc)
    elif ts[-1].isdigit():
        tmp = ts[:-6] + '000' + ts[-6:].replace(':', '')  # Re- jig the tz specification and insert usec
        return datetime.datetime.strptime(tmp, format)
