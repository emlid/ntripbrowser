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

import logging
from geopy.distance import geodesic

import pycurl
import cchardet

try:
    from io import BytesIO  # Python 3
except ImportError:
    from StringIO import StringIO as BytesIO  # Python 2

from .constants import (CAS_HEADERS, STR_HEADERS, NET_HEADERS, PYCURL_TIMEOUT_ERRNO,
                        MULTICURL_SELECT_TIMEOUT)
from .exceptions import (ExceededTimeoutError, UnableToConnect, NoDataReceivedFromCaster)


logger = logging.getLogger(__name__)


class DataFetcher(object):
    """Fetch data from specified urls, execute custom callback on results.

    Parameters
    ----------
    urls : [str, str, ...]
        URL's to fetch data from.
    timeout : int
    parser_method : callable
        Custom callback to be executed on fetched from url's results.

    Attributes
    ----------
    urls_processed : [str, str, ...]
        URL's which are processed and on which no valid data was found.

    result :
        Return value of `parser_method` function or None.
    """
    def __init__(self, urls, timeout, parser_method):
        self.timeout = timeout
        self.urls = urls
        self._parser_method = parser_method
        self.urls_processed = []
        self.results = None
        self._multicurl = None
        self._buffers = {}
        self._curls_failed = []

    @property
    def curls(self):
        return self._buffers.keys()

    @property
    def _result_found(self):
        return bool(self.results)

    def setup(self):
        self.urls_processed = []
        self.results = None
        self._multicurl = pycurl.CurlMulti()
        self._buffers = {}
        self._curls_failed = []
        self._initialize()
        logger.info('DataFetcher: curls setup in process')
        for curl in self.curls:
            self._multicurl.add_handle(curl)

    def _initialize(self):
        for url in self.urls:
            logger.debug('DataFetcher: Buffered curl creation for url "%s" in process', url)
            buffer = BytesIO()
            curl = pycurl.Curl()
            curl.setopt(pycurl.URL, url)
            curl.setopt(pycurl.TIMEOUT, self.timeout)
            curl.setopt(pycurl.CONNECTTIMEOUT, self.timeout)
            curl.setopt(pycurl.WRITEFUNCTION, buffer.write)
            curl.setopt(pycurl.WRITEDATA, buffer)
            self._buffers.update({curl: buffer})

    def read_data(self):
        while not self._result_found:
            ret, num_handles = self._multicurl.perform()
            if ret != pycurl.E_CALL_MULTI_PERFORM:
                break

        while num_handles:
            self._multicurl.select(MULTICURL_SELECT_TIMEOUT)
            while not self._result_found:
                ret, num_handles = self._multicurl.perform()
                self._read_multicurl_info()
                if self._result_found:
                    return
                if ret != pycurl.E_CALL_MULTI_PERFORM:
                    break
        self._process_fetch_failure()

    def _read_multicurl_info(self):
        _, successful_curls, failed_curls = self._multicurl.info_read()
        self._curls_failed.extend(failed_curls)
        for curl in successful_curls:
            self._process_successful_curl(curl)
            if self._result_found:
                return

    def _process_successful_curl(self, curl):
        curl_results = self._buffers[curl].getvalue()
        url_processed = curl.getinfo(pycurl.EFFECTIVE_URL)
        self.urls_processed.append(url_processed)
        logger.info('DataFetcher: Trying to parse curl response from "%s"', url_processed)
        try:
            self.results = self._parser_method(curl_results)
            logger.info('DataFetcher: Results from "%s" is processed successfully', url_processed)
        except NoDataReceivedFromCaster:
            self.results = None
            logger.info('DataFetcher: No valid data found in curl response from "%s"', url_processed)

    def _process_fetch_failure(self):
        """- If the number of processed URL's is equal to the number of URL's
        which are requested to poll, this means that no data received from casters.
        - If in failed curls list timeout error exist, use it as a fail reason.
        - If no curls with exceeded timeout are found, throw UnableToConnect
        with first failed curl reason.
        - Otherwise, there are no failed curls and all curls which are succeeds
        received no data from the caster, so throw a NoDataReceivedFromCaster.
        """
        logger.info('DataFetcher: No valid result is received')
        if len(self.urls_processed) == len(self.urls):
            raise NoDataReceivedFromCaster()
        for _, error_code, error_text in self._curls_failed:
            if error_code == PYCURL_TIMEOUT_ERRNO:
                raise ExceededTimeoutError(error_text)
        if self._curls_failed:
            _, _, error_text = self._curls_failed[0]
            raise UnableToConnect(error_text)
        raise NoDataReceivedFromCaster()

    def teardown(self):
        for curl in self.curls:
            self._multicurl.remove_handle(curl)
        self._multicurl.close()
        for curl in self.curls:
            curl.close()
        logger.info('DataFetcher: Curls are closed succesfully')
        self._buffers = {}


class NtripBrowser(object):
    def __init__(self, host, port=2101, timeout=4,  # pylint: disable-msg=too-many-arguments
                 coordinates=None, maxdist=None):
        self._host = None
        self.host = host
        self.port = port
        self.timeout = timeout
        self.coordinates = coordinates
        self.maxdist = maxdist
        self._fetcher = DataFetcher(self.urls, self.timeout, self._process_raw_data)

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
        self._fetcher.setup()
        self._fetcher.read_data()
        self._fetcher.teardown()
        return self._fetcher.results

    def _process_raw_data(self, raw_data):
        decoded_raw_ntrip = self._decode_data(raw_data)
        ntrip_tables = self._get_ntrip_tables(decoded_raw_ntrip)
        ntrip_dictionary = self._form_ntrip_entries(ntrip_tables)
        ntrip_dictionary = self._add_distance(ntrip_dictionary)
        return self._trim_outlying(ntrip_dictionary)

    @staticmethod
    def _decode_data(data):
        data_encoding = cchardet.detect(data)['encoding']
        return data.decode('utf8' if not data_encoding else data_encoding)

    def _get_ntrip_tables(self, data):
        ntrip_tables = self._extract_ntrip_entry_strings(data)
        if not any(ntrip_tables):
            raise NoDataReceivedFromCaster()
        return ntrip_tables

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

    def _trim_outlying(self, ntrip_dictionary):
        if (self.maxdist is not None) and (self.coordinates is not None):
            return {
                'cas': self._trim_outlying_casters(ntrip_dictionary.get('cas')),
                'net': self._trim_outlying_casters(ntrip_dictionary.get('net')),
                'str': self._trim_outlying_casters(ntrip_dictionary.get('str'))
            }
        return ntrip_dictionary

    def _trim_outlying_casters(self, ntrip_type_dictionary):
        def by_distance(row):
            return row['Distance'] < self.maxdist
        inlying_casters = list(filter(by_distance, ntrip_type_dictionary))
        inlying_casters.sort(key=lambda row: row['Distance'])
        return inlying_casters
