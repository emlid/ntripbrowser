# ntripbrowser code is placed under the 3-Clause BSD License.
# Written by Andrew Yushkevich (andrew.yushkevich@emlid.com)
#
# If you are interested in using ntripbrowser code as a part of a
# closed source project, please contact Emlid Limited (info@emlid.com).
#
# Copyright (c) 2017, Emlid Limited
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the Emlid Limited nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS 'AS IS' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL Emlid Limited BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import pycurl
import chardet
import logging
from geopy.distance import geodesic

try:
    from io import BytesIO  # Python 3
except ImportError:
    from StringIO import StringIO as BytesIO  # Python 2

from .constants import (CAS_HEADERS, STR_HEADERS, NET_HEADERS, PYCURL_TIMEOUT_ERRNO,
                        PYCURL_COULD_NOT_RESOLVE_HOST_ERRNO, PYCURL_CONNECTION_FAILED_ERRNO,
                        PYCURL_HANDSHAKE_ERRNO)
from .exceptions import (ExceededTimeoutError, UnableToConnect, NoDataFoundOnPage,
                         NoDataReceivedFromCaster, HandshakeFiledError)


logger = logging.getLogger(__name__)


class NtripBrowser(object):
    def __init__(self, host, port=2101, timeout=4, coordinates=None):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.coordinates = coordinates

    @property
    def host(self):
        return self._host

    @host.setter
    def host(self, host):
        host = host.replace('http://', '')
        host = host.replace('https://', '')
        self._host = host

    @property
    def urls(self):
        http_url = '{}{}:{}'.format('http://', self.host, self.port)
        https_url = '{}{}:{}'.format('https://', self.host, self.port)
        http_sourcetable_url = '{}{}'.format(http_url, '/sourcetable.txt')
        https_sourcetable_url = '{}{}'.format(https_url, '/sourcetable.txt')
        return [http_url, http_sourcetable_url, https_url, https_sourcetable_url]

    def get_mountpoints(self):
        for url in self.urls:
            logger.debug('Trying to read NTRIP data from{}'.format(url))
            raw_data = self._read_data(url)
            try:
                return self._process_raw_data(raw_data)
            except NoDataFoundOnPage:
                logger.info('No data found on the {}'.format(url))

        raise NoDataReceivedFromCaster()

    def _read_data(self, url):
        buffer = BytesIO()
        curl = pycurl.Curl()
        curl.setopt(pycurl.URL, url)
        curl.setopt(pycurl.TIMEOUT, self.timeout)
        curl.setopt(pycurl.CONNECTTIMEOUT, self.timeout)
        curl.setopt(pycurl.WRITEDATA, buffer)
        self._perform_data_reading(curl)
        return buffer.getvalue()

    @staticmethod
    def _perform_data_reading(curl):
        try:
            curl.perform()
        except pycurl.error as error:
            errno, errstr = error.args
            if errno in (PYCURL_COULD_NOT_RESOLVE_HOST_ERRNO, PYCURL_CONNECTION_FAILED_ERRNO):
                raise UnableToConnect(errstr)
            if errno == PYCURL_TIMEOUT_ERRNO:
                raise ExceededTimeoutError(errstr)
            if errno == PYCURL_HANDSHAKE_ERRNO:
                raise HandshakeFiledError()
            logger.error('pycurl.error({}) while reading data from url: {}'.format(errno, errstr))
        curl.close()

    def _process_raw_data(self, raw_data):
        decoded_raw_ntrip = self._decode_data(raw_data)
        ntrip_tables = self._get_ntrip_tables(decoded_raw_ntrip)
        ntrip_dictionary = self._form_ntrip_entries(ntrip_tables)
        return self._add_distance(ntrip_dictionary)

    @staticmethod
    def _decode_data(data):
        data_encoding = chardet.detect(data)['encoding']
        return data.decode('utf8' if not data_encoding else data_encoding)

    def _get_ntrip_tables(self, data):
        if 'ENDSOURCETABLE' in data:
            return self._extract_ntrip_entry_strings(data)
        raise NoDataFoundOnPage()

    @staticmethod
    def _extract_ntrip_entry_strings(raw_table):
        str_list, cas_list, net_list = [], [], []
        for row in raw_table.splitlines():
            if row.startswith('STR'):
                str_list.append(row)
            elif row.startswith('CAS'):
                cas_list.append(row)
            elif row.startswith('NET'):
                net_list.append(row)
        return str_list, cas_list, net_list

    def _form_ntrip_entries(self, ntrip_tables):
        return {
            'str': self._form_dictionaries(STR_HEADERS, ntrip_tables[0]),
            'cas': self._form_dictionaries(CAS_HEADERS, ntrip_tables[1]),
            'net': self._form_dictionaries(NET_HEADERS, ntrip_tables[2])
        }

    @staticmethod
    def _form_dictionaries(headers, line_list):
        def form_line(index):
            line = index.split(';', len(headers))[1:]
            return dict(zip(headers, line))

        return [form_line(i) for i in line_list]

    def _add_distance(self, ntrip_dictionary):
        return {
            'cas': self._add_distance_column(ntrip_dictionary.get('cas')),
            'net': self._add_distance_column(ntrip_dictionary.get('net')),
            'str': self._add_distance_column(ntrip_dictionary.get('str'))
        }

    def _add_distance_column(self, ntrip_type_dictionary):
        for station in ntrip_type_dictionary:
            latlon = self._get_float_coordinates((station.get('Latitude'), station.get('Longitude')))
            station['Distance'] = self._get_distance(latlon)
        return ntrip_type_dictionary

    @staticmethod
    def _get_float_coordinates(obs_point):
        def to_float(arg):
            try:
                return float(arg.replace(',', '.'))
            except (ValueError, AttributeError):
                return None

        return [to_float(coordinate) for coordinate in obs_point]

    def _get_distance(self, obs_point):
        if self.coordinates:
            return geodesic(obs_point, self.coordinates).kilometers
        return None
