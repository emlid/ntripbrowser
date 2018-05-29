class NtripbrowserError(Exception):
    pass


class UnableToConnect(NtripbrowserError):
    pass


class ExceededTimeoutError(NtripbrowserError):
    pass


class NoDataFoundOnPage(NtripbrowserError):
    pass


class HandshakeFiledError(NtripbrowserError):
    pass


class NoDataReceivedFromCaster(NtripbrowserError):
    pass
