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

import urllib
import argparse
import pydoc
from texttable import Texttable

class NTRIP(object):

    STR_headers = ["Mountpoint","ID","Format","Format-Details",
        "Carrier","Nav-System","Network","Country","Latitude",
        "Longitude","NMEA","Solution","Generator","Compr-Encrp",
        "Authentication","Fee","Bitrate",""]

    STR_colomn_width = [5, 10, 5, 9, 3,
                        4, 5, 3, 9, 9,
                        3, 3, 5, 5, 3,
                        3, 4, 5]

    STR_align = ['c', 'l', 'c', 'r', 'c',
                 'c', 'c', 'c', 'r', 'r',
                 'c', 'c', 'c', 'c', 'c',
                 'c', 'c', 'c']

    STR_valign = list('m'*18)

    STR_colomn_width_non_verbose = [10, 30, 10, 12, 10]
    
    STR_non_verbose = [0, 1, 2, 5, 7]

    CAS_headers = ["Host","Port","ID","Operator",
        "NMEA","Country","Latitude","Longitude", 
        "Fallback\nHost","Fallback\nPort",""]

    CAS_colomn_width = [20, 4, 10, 10, 4,
                        7, 9, 9, 16, 4, 
                        20]

    CAS_align = ['l', 'c', 'l', 'c', 'c',
                 'c', 'r', 'r', 'r', 'c',
                 'l']

    CAS_valign = list('m'*11)


    NET_headers = ["ID","Operator","Authentication",
        "Fee","Web-Net","Web-Str","Web-Reg",""]

    NET_colomn_width = [8, 10, 10, 3,
                        15, 15, 15, 4]

    NET_align = ['c', 'c', 'c', 'c',
                 'l', 'l', 'l', 'c']

    NET_valign = list('m'*8)

    def __init__(self, sourcetable, verbose = False, 
            show_net = False, show_cas = False,
            nopager = False):

        self.verbose = verbose 
        self.show_net = show_net
        self.show_cas = show_cas
        self.nopager = nopager
        self.sourcetable = None    
        self.str_data = [self.STR_headers]
        self.cas_data = [self.CAS_headers]
        self.net_data = [self.NET_headers]

        if self.check_page_status(sourcetable):
            self.crop_sourcetable(sourcetable)
            self.parce_sourcetable()
            self.create_ascii_table()
            self.display_tables()

    def check_page_status(self, sourcetable):
        find = sourcetable.find('SOURCETABLE')
        find_status = find + len('SOURCETABLE') + 1
        status = sourcetable[find_status:find_status+3]
        if status != '200':
            if self.nopager:
                print "Error page code: {}".format(status)
            else:
                pydoc.pager("Error page code: {}".format(status))
            return False
        return True

    def crop_sourcetable(self, sourcetable):
        CAS = sourcetable.find('CAS') 
        NET = sourcetable.find('NET')
        STR = sourcetable.find('STR')
        first = CAS if (CAS != -1) else (NET if NET != -1 else STR)
        last = sourcetable.find('ENDSOURCETABLE')        
        self.sourcetable = sourcetable[first:last]

    def parce_sourcetable(self):
        for NTRIP_data in self.sourcetable.split('\n'):
            NTRIP_data_list = NTRIP_data.split(';')
            if NTRIP_data_list[0] == 'STR':
                NTRIP_data_list[4] =  NTRIP_data_list[4].replace(',', '\n')
                self.str_data.append(NTRIP_data_list[1:])
            if NTRIP_data_list[0] == 'CAS':
                self.cas_data.append(NTRIP_data_list[1:])
            if NTRIP_data_list[0] == 'NET':
                self.net_data.append(NTRIP_data_list[1:])

    def change_verbosity(self):
        align = [self.STR_align[i] for i in self.STR_non_verbose]
        valign = [self.STR_valign[i] for i in self.STR_non_verbose]
        data = []
        for elem in self.str_data:
            data.append([elem[i] for i in self.STR_non_verbose])
        
        self.str_data = data
        self.STR_colomn_width = self.STR_colomn_width_non_verbose
        self.STR_align = align
        self.STR_valign = valign
        
    def create_ascii_table(self):
        if not self.verbose:
            self.change_verbosity()  
            
        self.STR_table = Texttable()
        self.STR_table.add_rows(self.str_data)
        self.STR_table.set_cols_width(self.STR_colomn_width)
        self.STR_table.set_cols_align(self.STR_align)
        self.STR_table.set_cols_valign(self.STR_valign)

        if self.show_cas:
            self.CAS_table = Texttable()
            self.CAS_table.add_rows(self.cas_data)
            self.CAS_table.set_cols_width(self.CAS_colomn_width)
            self.CAS_table.set_cols_align(self.CAS_align)
            self.CAS_table.set_cols_valign(self.CAS_valign)        
        if self.show_net:
            self.NET_table = Texttable()
            self.NET_table.add_rows(self.net_data)
            self.NET_table.set_cols_width(self.NET_colomn_width)
            self.NET_table.set_cols_align(self.NET_align)
            self.NET_table.set_cols_valign(self.NET_valign)

    def display_tables(self):
        output_data = "STR Table\n"
        output_data += self.STR_table.draw() + '\n'
        if self.show_cas:
            output_data += "CAS Table\n"
            output_data += self.CAS_table.draw() + '\n'
        if self.show_net:
            output_data += "NET Table\n"
            output_data += self.NET_table.draw()
        if self.nopager:
            print(output_data)
        else:
            pydoc.pager(output_data)

def argparser():
    parser = argparse.ArgumentParser(description='Parse NTRIP sourcetable')
    parser.add_argument("url", help="NTRIP sourcetable address")
    parser.add_argument("-p", "--port", type=int,
                        help="change url port. Standart port is 2101")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="increase output verbosity")
    parser.add_argument("-N", "--NETtable", action="store_true",
                        help="additional show NET table")
    parser.add_argument("-C", "--CATtable", action="store_true",
                        help="additional show CAT table")
    parser.add_argument("-n", "--nopager", action="store_true",
                        help="no pager")
    parser.add_argument("-s", "--source", action="store_true",
                        help="display url source data")
    return parser.parse_args()


def main():
    args = argparser()
    if (args.url.find("http") != -1):
        pream = ''
    else:
        pream = 'http://'

    if args.port:
        url_for_parse = '{}{}:{}'.format(pream, args.url, args.port)
    else:
        url_for_parse = '{}{}:2101'.format(pream, args.url)

    try:
        NTRIP_url = urllib.urlopen(url_for_parse)
        url_data = NTRIP_url.read()
    except IOError:
        print "Socket error. Connection refused"
    else:
        if args.source:
            if args.nopager:
                print(url_data)
            else:
                pydoc.pager(url_data)
        else:
            NTRIP(url_data, args.verbose, args.NETtable, 
                args.CATtable, args.nopager)

if __name__ == '__main__':
    main()