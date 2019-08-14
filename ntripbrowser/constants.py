CAS_HEADERS = ('Host', 'Port', 'ID', 'Operator',
               'NMEA', 'Country', 'Latitude', 'Longitude',
               'FallbackHost', 'FallbackPort', 'Site', 'Other Details', 'Distance')

NET_HEADERS = ('ID', 'Operator', 'Authentication',
               'Fee', 'Web-Net', 'Web-Str', 'Web-Reg', 'Other Details', 'Distance')

STR_HEADERS = ('Mountpoint', 'ID', 'Format', 'Format-Details',
               'Carrier', 'Nav-System', 'Network', 'Country', 'Latitude',
               'Longitude', 'NMEA', 'Solution', 'Generator', 'Compr-Encryp',
               'Authentication', 'Fee', 'Bitrate', 'Other Details', 'Distance')

PYCURL_COULD_NOT_RESOLVE_HOST_ERRNO = 6
PYCURL_CONNECTION_FAILED_ERRNO = 7
PYCURL_TIMEOUT_ERRNO = 28
PYCURL_HANDSHAKE_ERRNO = 35

MULTICURL_SELECT_TIMEOUT = 0.5
