# ntripbrowser code is placed under the GPL license.
# Written by Ivan Sapozhkov (ivan.sapozhkov@emlid.com)
# Copyright (c) 2016, Emlid Limited
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
import pydoc
import subprocess
from texttable import Texttable
import chardet
from geopy.distance import vincenty

def getScreenResolution():
    cmd = "stty size"
    output = subprocess.check_output(cmd, shell=True, stderr=subprocess.PIPE)
    size = output.strip().split()
    return size

def display_output(message, max_height, nopager=False):
    if (nopager or
        len(message.split('\n')) < max_height):
        print message.strip()
    else:
        pydoc.pager(message.strip())


class NTRIP(object):

    STR_headers = ["Mountpoint","ID","Format","Format-Details",
        "Carrier","Nav-System","Network","Country","Latitude",
        "Longitude","NMEA","Solution","Generator","Compr-Encrp",
        "Authentication","Fee","Bitrate","Other Details"]

    STR_align = ['c', 'l', 'c', 'r', 'c',
                 'c', 'c', 'c', 'r', 'r',
                 'c', 'c', 'c', 'c', 'c',
                 'c', 'c', 'c']

    STR_valign = list('m'*18)

    STR_non_verbose = [0, 1, 2, 5, 7]

    CAS_headers = ["Host","Port","ID","Operator",
        "NMEA","Country","Latitude","Longitude",
        "Fallback\nHost","Fallback\nPort","Site"]


    CAS_align = ['l', 'c', 'l', 'c', 'c',
                 'c', 'r', 'r', 'r', 'c',
                 'l']

    CAS_valign = list('m'*11)


    NET_headers = ["ID","Operator","Authentication",
        "Fee","Web-Net","Web-Str","Web-Reg",""]


    NET_align = ['c', 'c', 'c', 'c',
                 'l', 'l', 'l', 'c']

    NET_valign = list('m'*8)

    def __init__(self, sourcetable, window_size, verbose = False,
            show_net = False, show_cas = False,
            nopager = False):

        self.height = int(window_size[0])
        self.width = int(window_size[1])
        self.verbose = verbose
        self.show_net = show_net
        self.show_cas = show_cas
        self.nopager = nopager
        self.sourcetable = None
        self.str_data = [self.STR_headers]
        self.cas_data = [self.CAS_headers]
        self.net_data = [self.NET_headers]
        self.caster_data = {}
        

        if self.check_page_status(sourcetable):
            self.crop_sourcetable(sourcetable)
            self.parse_sourcetable()
            self.create_ascii_table()
            self.display_tables()

    def check_page_status(self, sourcetable):
        find = sourcetable.find('SOURCETABLE')
        find_status = find + len('SOURCETABLE') + 1
        status = sourcetable[find_status:find_status+3]
        if status != '200':
            display_output("Error page code: {}".format(status),
                self.height, self.nopager)
            return False
        return True

    def crop_sourcetable(self, sourcetable):
        CAS = sourcetable.find('\n'+'CAS')
        NET = sourcetable.find('\n'+'NET')
        STR = sourcetable.find('\n'+'STR')
        first = CAS if (CAS != -1) else (NET if NET != -1 else STR)
        last = sourcetable.find('ENDSOURCETABLE')
        self.sourcetable = sourcetable[first:last]

    def parse_sourcetable(self):
        for NTRIP_data in self.sourcetable.split('\n'):
            NTRIP_data_list = NTRIP_data.split(';', 18)
            if NTRIP_data_list[0] == 'STR':
                NTRIP_data_list[4] = NTRIP_data_list[4].replace(',', '\n')
                NTRIP_data_list[6] = NTRIP_data_list[6].replace('+', '\n')
                self.str_data.append(NTRIP_data_list[1:])
                
                ntrip_caster_info = dict(zip(self.STR_headers, NTRIP_data_list[1:]))
                str_latlon = (ntrip_caster_info['Latitude'],ntrip_caster_info['Longitude'])              
                self.caster_data.update(ntrip_caster_info)

                self.str_distance = get_distance(str_latlon)


            if NTRIP_data_list[0] == 'CAS':
                if len(NTRIP_data_list) > len(self.CAS_headers):
                    self.cas_data.append(NTRIP_data_list[1:])
            if NTRIP_data_list[0] == 'NET':
                if len(NTRIP_data_list) > len(self.NET_headers):
                    self.net_data.append(NTRIP_data_list[1:])
        
    # @property
    # def point(self):
    #     return (float(self.caster_data['Latitude']), 
    #         float(self.caster_data['Longitude']))


    def change_verbosity(self):
        align = [self.STR_align[i] for i in self.STR_non_verbose]
        valign = [self.STR_valign[i] for i in self.STR_non_verbose]
        data = []
        for elem in self.str_data:
            data.append([elem[i] for i in self.STR_non_verbose])

        self.str_data = data
        self.STR_align = align
        self.STR_valign = valign

    def create_ascii_table(self):
        if not self.verbose:
            self.change_verbosity()
        if len(self.str_data) > 1:
            self.STR_table = Texttable(max_width = self.width)
            self.STR_table.add_rows(self.str_data)
            self.STR_table.set_cols_align(self.STR_align)
            self.STR_table.set_cols_valign(self.STR_valign)
           
        else:
            self.STR_table = None

        if self.show_cas:
            if len(self.cas_data) > 1:
                self.CAS_table = Texttable(max_width = self.width)
                self.CAS_table.add_rows(self.cas_data)
                self.CAS_table.set_cols_align(self.CAS_align)
                self.CAS_table.set_cols_valign(self.CAS_valign)
            else:
                self.CAS_table = None
        if self.show_net:
            if len(self.net_data) > 1:
                self.NET_table = Texttable(max_width = self.width)
                self.NET_table.add_rows(self.net_data)
                self.NET_table.set_cols_align(self.NET_align)
                self.NET_table.set_cols_valign(self.NET_valign)
            else:
                self.NET_table = None

    def display_tables(self):
        self.STR_table._compute_cols_width()
        output_data = "{:=^{}}\n\n".format("STR Table", 40)
        if self.STR_table:
            output_data += self.STR_table.draw() + '\n\n'
        if self.show_cas:
            output_data += "{:=^{}}\n\n".format("CAS Table", 40)
            if self.CAS_table:
                output_data += self.CAS_table.draw() + '\n\n'
        if self.show_net:
            output_data += "{:=^{}}\n\n".format("NET Table", 40)
            if self.NET_table:
                output_data += self.NET_table.draw()

        display_output(output_data, self.height, self.nopager)

def argparser():
    parser = argparse.ArgumentParser(description='Parse NTRIP sourcetable')
    parser.add_argument("url", help="NTRIP sourcetable address")
    parser.add_argument("-p", "--port", type=int,
                        help="change url port. Standart port is 2101", default=2101)
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="increase output verbosity")
    parser.add_argument("-N", "--NETtable", action="store_true",
                        help="additional show NET table")
    parser.add_argument("-C", "--CATtable", action="store_true",
                        help="additional show CAT table")
    parser.add_argument("-n", "--no-pager", action="store_true",
                        help="no pager")
    parser.add_argument("-s", "--source", action="store_true",
                        help="display url source data")
    parser.add_argument("-t", "--timeout", type=int,
                        help="add timeout", default=None)
    parser.add_argument("-b", "--BasePointCoord",
                        help="add base point coordiantes x,y")
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
    CAS = sourcetable.find('\n'+'CAS')
    NET = sourcetable.find('\n'+'NET')
    STR = sourcetable.find('\n'+'STR')
    first = CAS if (CAS != -1) else (NET if NET != -1 else STR)
    last = sourcetable.find('ENDSOURCETABLE')
    return sourcetable[first:last]

def parse_ntrip_table(raw_text):
    raw_table = crop_sourcetable(raw_text)
    ntrip_tables = extract_ntrip_entry_strings(raw_table)
    return ntrip_tables

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
    STR_headers = ["Mountpoint","ID","Format","Format-Details",
        "Carrier","Nav-System","Network","Country","Latitude",
        "Longitude","NMEA","Solution","Generator","Compr-Encrp",
        "Authentication","Fee","Bitrate","Other Details"]

    return form_dictionaries(STR_headers, str_list)

def form_cas_dictionary(cas_list):
    CAS_headers = ["Host","Port","ID","Operator",
        "NMEA","Country","Latitude","Longitude",
        "Fallback\nHost","Fallback\nPort","Site"]

    return form_dictionaries(CAS_headers, cas_list)

def form_net_dictionary(net_list):
    NET_headers = ["ID","Operator","Authentication",
        "Fee","Web-Net","Web-Str","Web-Reg",""]

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

def add_distance_row(ntrip_type_dictionary, base_point):
    for station in ntrip_type_dictionary:
        dictionary_latlon = (station.get('Latitude'), station.get('Longitude'))
        distance = get_distance(dictionary_latlon, base_point)
        station['Distance'] = distance
    return ntrip_type_dictionary

def station_distance(ntrip_dictionary, base_point):
    return {
        "cas": add_distance_row(ntrip_dictionary.get('cas'), base_point),
        "net": add_distance_row(ntrip_dictionary.get('net'), base_point),
        "str": add_distance_row(ntrip_dictionary.get('str'), base_point)
    }

def main():
    args = argparser()
    NTRIP_url = None

    if (args.url.find("http") != -1):
        pream = ''
    else:
        pream = 'http://'

    ntrip_url = '{}{}:{}'.format(pream, args.url, args.port)
    print(ntrip_url)

    try:
        ntrip_table_raw = read_url(ntrip_url, timeout=args.timeout)
    except (IOError, httplib.HTTPException):
        print("Bad url")
        pass
    else:
        ntrip_table_raw_decoded = decode_text(ntrip_table_raw)
        ntrip_tables = parse_ntrip_table(ntrip_table_raw_decoded)
        ntrip_dictionary = form_ntrip_entries(ntrip_tables)
        station_dict = station_distance(ntrip_dictionary, base_point = (args.BasePointCoord))

    #     print "Socket error. Connection refused"

    # else:
    #     url_for_parse = '{}{}:{}/sourcetable.txt'.format(pream, args.url, args.port)
    #     NTRIP_url = urlopen(url_for_parse, timeout = args.timeout)
    #     ntrip_response = NTRIP_url.read()
    
    #     encoding_detect = chardet.detect(ntrip_response)
    #     encoding_key = encoding_detect.get('encoding')
    #     ntrip_response = ntrip_response.decode(encoding_key)

    # finally:
    #     if NTRIP_url == None: ###
    #         return
    #     else:
    #         NTRIP_url.close()
    #         window_size = getScreenResolution()
    #         if args.source:
    #             display_output(ntrip_response, int(window_size[0]),  args.no_pager)
    #         else:
    #             ntrip = NTRIP(ntrip_response, window_size, args.verbose, args.NETtable,
    #                 args.CATtable, args.no_pager)
            
if __name__ == '__main__':
    main()