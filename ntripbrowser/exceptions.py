class NtripbrowserError(Exception):
    pass


class UnableToConnect(NtripbrowserError):
    pass


class ExceededTimeoutError(NtripbrowserError):
    pass


class NoDataReceivedFromCaster(NtripbrowserError):
    pass
