import pydoc
import pager
import argparse

from texttable import Texttable

from ntripbrowser import NtripBrowser
from ntripbrowser import ExceededTimeoutError, UnableToConnect, NoDataReceivedFromCaster, HandshakeFiledError
from ntripbrowser import CAS_HEADERS, STR_HEADERS, NET_HEADERS


SCREEN_WIDTH = pager.getwidth()


def argparser():
    parser = argparse.ArgumentParser(description='Parse NTRIP sourcetable')
    parser.add_argument('url', help='NTRIP sourcetable address')
    parser.add_argument('-p', '--port', type=int,
                        help='Set url port. Standard port is 2101', default=2101)
    parser.add_argument('-t', '--timeout', type=int,
                        help='add timeout', default=4)
    parser.add_argument('-c', '--coordinates',
                        help='Add NTRIP station distance to this coordinate', nargs=2)

    return parser.parse_args()


def display_ntrip_table(ntrip_table):
    table_cas = compile_ntrip_table(ntrip_table['cas'], CAS_HEADERS)
    table_net = compile_ntrip_table(ntrip_table['net'], NET_HEADERS)
    table_str = compile_ntrip_table(ntrip_table['str'], STR_HEADERS)

    pydoc.pager((
            'CAS TABLE'.center(SCREEN_WIDTH, '=') + '\n' + table_cas + 4 * '\n' +
            'NET TABLE'.center(SCREEN_WIDTH, '=') + '\n' + table_net + 4 * '\n' +
            'STR TABLE'.center(SCREEN_WIDTH, '=') + '\n' + table_str
    ))


def compile_ntrip_table(table, headers):
    table_to_draw = Texttable(max_width=SCREEN_WIDTH)
    for row in table:
        row_to_draw = []
        for header in headers:
            try:
                row_to_draw.append(row[header])
            except KeyError:
                row_to_draw.append(None)
        table_to_draw.add_rows((headers, row_to_draw))

    return table_to_string(table_to_draw)


def table_to_string(table):
    try:
        return str(table.draw()).center(SCREEN_WIDTH, ' ')  # python3
    except UnicodeEncodeError:
        return table.draw().center(SCREEN_WIDTH, ' ')       # python2
    except TypeError:
        return ''


def main():
    args = argparser()
    browser = NtripBrowser(args.url, port=args.port, timeout=args.timeout, coordinates=args.coordinates)
    try:
        ntrip_table = browser.get_mountpoints()
    except ExceededTimeoutError:
        print('Connection timed out')
    except UnableToConnect:
        print('Unable to connect to NTRIP caster')
    except NoDataReceivedFromCaster:
        print('No data received from NTRIP caster')
    except HandshakeFiledError:
        print('Unable to connect to NTRIP caster, handshake error')
    else:
        display_ntrip_table(ntrip_table)
