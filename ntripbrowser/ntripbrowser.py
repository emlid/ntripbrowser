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
#     * Neither the name of the <organization> nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL Emlid Limited BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import urllib2
import httplib
import argparse
import chardet
import subprocess
import pydoc

from geopy.distance import vincenty
from texttable import Texttable

CAS_headers = ["Host", "Port", "ID", "Operator",
               "NMEA", "Country", "Latitude", "Longitude",
               "FallbackHost", "FallbackPort", "Site", "Other Details", "Distance"]

NET_headers = ["ID", "Operator", "Authentication",
               "Fee", "Web-Net", "Web-Str", "Web-Reg", "Other Details", "Distance"]

STR_headers = ["Mountpoint", "ID", "Format", "Format-Details",
               "Carrier", "Nav-System", "Network", "Country", "Latitude",
               "Longitude", "NMEA", "Solution", "Generator", "Compr-Encrp",
               "Authentication", "Fee", "Bitrate", "Other Details", "Distance"]

def getScreenResolution():
    cmd = "stty size"
    output = subprocess.check_output(cmd, shell=True, stderr=subprocess.PIPE)
    size = output.strip().split()

    return int(size[1])


class NtripError(Exception):
    pass


def argparser():
    parser = argparse.ArgumentParser(description="Parse NTRIP sourcetable")
    parser.add_argument("url", help="NTRIP sourcetable address")
    parser.add_argument("-p", "--port", type=int,
                        help="Set url port. Standard port is 2101", default=2101)
    parser.add_argument("-t", "--timeout", type=int,
                        help="add timeout", default=None)
    parser.add_argument("-c", "--coordinates",
                        help="Add NTRIP station distance to this coordinate", nargs=2)

    return parser.parse_args()


def read_url(url, timeout):
    ntrip_request = urllib2.urlopen(url, timeout=timeout)
    ntrip_table_raw = ntrip_request.read()
    ntrip_request.close()

    return ntrip_table_raw


def decode_text(text):
    detected_table_encoding = chardet.detect(text)['encoding']
    return text.decode(detected_table_encoding).encode('utf8')


def parse_ntrip_table(raw_text):
    if 'SOURCETABLE 200 OK' in raw_text:
        raw_table = raw_text
        ntrip_tables = extract_ntrip_entry_strings(raw_table)
        return ntrip_tables
    else:
        raise NtripError("No data on the page")


def extract_ntrip_entries(raw_table):
    str_list, cas_list, net_list = extract_ntrip_entry_strings(raw_table)
    return form_ntrip_entries(str_list, cas_list, net_list)


def extract_ntrip_entry_strings(raw_table):
    str_list, cas_list, net_list = [], [], []
    for row in raw_table.splitlines():
        if row.startswith("STR"):
            str_list.append(row)
        elif row.startswith("CAS"):
            cas_list.append(row)
        elif row.startswith("NET"):
            net_list.append(row)

    return str_list, cas_list, net_list


def form_ntrip_entries(ntrip_tables):
    return {
        "str": form_str_dictionary(ntrip_tables[0]),
        "cas": form_cas_dictionary(ntrip_tables[1]),
        "net": form_net_dictionary(ntrip_tables[2])
    }


def form_str_dictionary(str_list):
    return form_dictionaries(STR_headers, str_list)


def form_cas_dictionary(cas_list):
    return form_dictionaries(CAS_headers, cas_list)


def form_net_dictionary(net_list):
    return form_dictionaries(NET_headers, net_list)


def form_dictionaries(headers, line_list):
    dict_list = []
    for i in line_list:
        line_dict = i.split(";", len(headers))[1:]
        info = dict(zip(headers, line_dict))
        dict_list.append(info)

    return dict_list


def get_distance(obs_point, coordinates):
    if coordinates is None:
        return None
    else:
        return vincenty(obs_point, coordinates).kilometers


def get_float_coordinates(obs_point):
    obs_point_list = []
    for coordinate in obs_point:
        try:
            float_coordinate = float(coordinate)
        except TypeError:
            float_coordinate = None
        except ValueError:
            try:
                float_coordinate = float(coordinate.replace(',', '.'))
            except ValueError:
                float_coordinate = None
        finally:
            obs_point_list.append(float_coordinate)

    return tuple(obs_point_list)


def add_distance_row(ntrip_type_dictionary, coordinates):
    for station in ntrip_type_dictionary:
        latlon = get_float_coordinates(
            (station.get('Latitude'), station.get('Longitude')))
        distance = get_distance(latlon, coordinates)
        station['Distance'] = distance
    return ntrip_type_dictionary


def add_distance(ntrip_dictionary, coordinates):
    return {
        "cas": add_distance_row(ntrip_dictionary.get('cas'), coordinates),
        "net": add_distance_row(ntrip_dictionary.get('net'), coordinates),
        "str": add_distance_row(ntrip_dictionary.get('str'), coordinates)
    }


def get_ntrip_table(ntrip_url, timeout, coordinates=None):
    print ntrip_url
    try:
        ntrip_table_raw = read_url(ntrip_url, timeout=timeout)
    except (IOError, httplib.HTTPException):
        raise NtripError("Bad URL")
    else:
        ntrip_table_raw_decoded = decode_text(ntrip_table_raw)
        ntrip_tables = parse_ntrip_table(ntrip_table_raw_decoded)
        ntrip_dictionary = form_ntrip_entries(ntrip_tables)
        station_dictionary = add_distance(ntrip_dictionary, coordinates)

        return station_dictionary


def get_mountpoints(url, timeout=None, coordinates=None):
    urls_to_try = (url, url + "/sourcetable.txt")
    for url in urls_to_try:
        print("Trying to get NTRIP source table from {}".format(url))
        try:
            ntrip_table = get_ntrip_table(url, timeout, coordinates)
        except NtripError:
            pass
        else:
            return ntrip_table

    raise NtripError


def compile_ntrip_table(table, header):
    draw_table = Texttable(max_width=getScreenResolution())
    current_value = []
    for row in table:
        for element in header:
            try:
                current_value.append(row[element])
            except KeyError:
                current_value.append("None")
        draw_table.add_rows((header, current_value))
        current_value = []

    return draw_table


def display_ntrip_table(ntrip_table):
    draw_cas = compile_ntrip_table(ntrip_table['cas'], CAS_headers)
    draw_net = compile_ntrip_table(ntrip_table['net'], NET_headers)
    draw_str = compile_ntrip_table(ntrip_table['str'], STR_headers)

    print pydoc.pager((
        "CAS TABLE".center(getScreenResolution(), "=") + '\n' + str(draw_cas.draw()) + 4 * '\n' +
        "NET TABLE".center(getScreenResolution(), "=") + '\n' + str(draw_net.draw()) + 4 * '\n' +
        "STR TABLE".center(getScreenResolution(), "=") + '\n' + str(draw_str.draw())
    ))


def parse_url(cli_arguments):
    if "http" in cli_arguments.url:
        pream = ''
    else:
        pream = 'http://'

    return '{}{}:{}'.format(pream, cli_arguments.url, cli_arguments.port)


def main():
    args = argparser()
    ntrip_url = parse_url(args)

    try:
        ntrip_table = get_mountpoints(
            ntrip_url, timeout=args.timeout, coordinates=args.coordinates)
    except NtripError:
        print("An error occurred")
    else:
        display_ntrip_table(ntrip_table)

if __name__ == '__main__':
    main()
