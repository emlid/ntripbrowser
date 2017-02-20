# ntripbrowser code is placed under the GPL license.
# Written by Andrew Yushkevich (andrew.yushkevich@emlid.com)
# Copyright (c) 2017, Emlid Limited
# All rights reserved.

# If you are interested in using ntripbrowser code as a part of a
# closed source project, please contact Emlid Limited (info@emlid.com).

# This file is part of ntripbrowser.

# ntripbrowser is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# ntripbrowser is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with ntripbrowser.  If not, see <http://www.gnu.org/licenses/>.
# from __future__ import unicode_literals

import urllib2
import httplib
import argparse
import chardet

from geopy.distance import vincenty


class NtripError(Exception):
    pass


def argparser():
    parser = argparse.ArgumentParser(description="Parse NTRIP sourcetable")
    parser.add_argument("url", help="NTRIP sourcetable address")
    parser.add_argument("-p", "--port", type=int, help="Set url port. Standard port is 2101", default=2101)
    parser.add_argument("-t", "--timeout", type=int, help="add timeout", default=None)
    parser.add_argument("-c", "--coordinates", help="Add NTRIP station distance to this coordiante", nargs=2)

    return parser.parse_args()


def read_url(url, timeout):
    ntrip_request = urllib2.urlopen(url, timeout=timeout)
    ntrip_table_raw = ntrip_request.read()
    ntrip_request.close()

    return ntrip_table_raw


def decode_text(text):
    detected_table_encoding = chardet.detect(text)['encoding']

    return text.decode(detected_table_encoding)


def crop_sourcetable(sourcetable):
    CAS = sourcetable.find('\n' + 'CAS')
    NET = sourcetable.find('\n' + 'NET')
    STR = sourcetable.find('\n' + 'STR')
    first = CAS if (CAS != -1) else (NET if NET != -1 else STR)
    last = sourcetable.find('ENDSOURCETABLE')

    return sourcetable[first:last]


def parse_ntrip_table(raw_text):
    if 'SOURCETABLE 200 OK' in raw_text:
        raw_table = crop_sourcetable(raw_text)
        ntrip_tables = extract_ntrip_entry_strings(raw_table)
        return ntrip_tables
    else:
        raise NtripError("No data on the page")


def extract_ntrip_entries(raw_table):
    str_list, cas_list, net_list = extract_ntrip_entry_strings(raw_table)
    return form_ntrip_entries(str_list, cas_list, net_list)


def extract_ntrip_entry_strings(raw_table):
    str_list, cas_list, net_list = [], [], []
    for row in raw_table.split("\n"):
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
    STR_headers = ["Mountpoint", "ID", "Format", "Format-Details",
                   "Carrier", "Nav-System", "Network", "Country", "Latitude",
                   "Longitude", "NMEA", "Solution", "Generator", "Compr-Encrp",
                   "Authentication", "Fee", "Bitrate", "Other Details"]

    return form_dictionaries(STR_headers, str_list)


def form_cas_dictionary(cas_list):
    CAS_headers = ["Host", "Port", "ID", "Operator",
                   "NMEA", "Country", "Latitude", "Longitude",
                   "FallbackHost", "FallbackPort", "Site", "Other Details"]

    return form_dictionaries(CAS_headers, cas_list)


def form_net_dictionary(net_list):
    NET_headers = ["ID", "Operator", "Authentication",
                   "Fee", "Web-Net", "Web-Str", "Web-Reg", "Other Details"]

    return form_dictionaries(NET_headers, net_list)


def form_dictionaries(headers, line_list):
    dict_list = []
    for i in line_list:
        line_dict = i.split(";", len(headers))[1:]
        info = dict(zip(headers, line_dict))
        dict_list.append(info)

    return dict_list


def get_distance(obs_point, base_point):

    return vincenty(obs_point, base_point).kilometers


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


def add_distance_row(ntrip_type_dictionary, base_point):
    for station in ntrip_type_dictionary:
        latlon = get_float_coordinates(
            (station.get('Latitude'), station.get('Longitude')))
        distance = get_distance(latlon, base_point)
        station['Distance'] = distance
    return ntrip_type_dictionary


def station_distance(ntrip_dictionary, base_point):
    return {
        "cas": add_distance_row(ntrip_dictionary.get('cas'), base_point),
        "net": add_distance_row(ntrip_dictionary.get('net'), base_point),
        "str": add_distance_row(ntrip_dictionary.get('str'), base_point)
    }


def get_ntrip_table(ntrip_url, timeout, base_point=None):
    print ntrip_url
    try:
        ntrip_table_raw = read_url(ntrip_url, timeout=timeout)
    except (IOError, httplib.HTTPException):
        raise NtripError("Bad URL")
    else:
        ntrip_table_raw_decoded = decode_text(ntrip_table_raw)
        ntrip_tables = parse_ntrip_table(ntrip_table_raw_decoded)
        ntrip_dictionary = form_ntrip_entries(ntrip_tables)
        station_dictionary = station_distance(ntrip_dictionary, base_point)

        return station_dictionary

def display_ntrip_table(ntrip_table):
    print(ntrip_table)


def main():
    args = argparser()

    if "http" in args.url:
        pream = ''
    else:
        pream = 'http://'

    ntrip_url = '{}{}:{}'.format(pream, args.url, args.port)
    urls_to_try = (ntrip_url, ntrip_url + "/sourcetable.txt")

    for url in urls_to_try:
        print("Trying to get NTRIP source table from {}".format(url))
        try:
            ntrip_table = get_ntrip_table(url, args.timeout, args.coordinates)
        except NtripError:
            print("An error occurred")
        else:
            display_ntrip_table(ntrip_table)
            break

if __name__ == '__main__':
    main()









