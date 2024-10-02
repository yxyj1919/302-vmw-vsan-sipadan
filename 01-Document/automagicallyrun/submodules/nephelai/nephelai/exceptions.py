
class NephelaiBaseException(Exception):
    pass


class NephelaiValidateException(NephelaiBaseException):
    """
    Class init failures
    """
    pass


class NephelaiParseException(NephelaiBaseException):
    pass


class NephelaiUnavailException(NephelaiParseException):
    pass


class NephelaiDisabledException(NephelaiUnavailException):
    pass


class NephelaiVersionException(NephelaiParseException):
    pass

"""
Base -> Init
|--> Parse
    |--> Unavailable
        |--> Disabled
    |--> Version
"""