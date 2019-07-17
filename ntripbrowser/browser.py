import argparse
import pydoc
import pager

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
    parser.add_argument('-M', '--maxdist',
                        help='Only report stations less than this number of km away from given coordinate', type=float, default=-1)

    return parser.parse_args()


def display_ntrip_table(ntrip_table, maxdist=-1):
    table_cas = compile_ntrip_table(ntrip_table['cas'], CAS_HEADERS, maxdist=maxdist)
    table_net = compile_ntrip_table(ntrip_table['net'], NET_HEADERS, maxdist=maxdist)
    table_str = compile_ntrip_table(ntrip_table['str'], STR_HEADERS, maxdist=maxdist)

    pydoc.pager((
        'CAS TABLE'.center(SCREEN_WIDTH, '=') + '\n' + table_cas + 4 * '\n' +
        'NET TABLE'.center(SCREEN_WIDTH, '=') + '\n' + table_net + 4 * '\n' +
        'STR TABLE'.center(SCREEN_WIDTH, '=') + '\n' + table_str
    ))


def compile_ntrip_table(table, headers, maxdist=-1):
    table_to_draw = Texttable(max_width=SCREEN_WIDTH)
    # sort by distance, closest first
    table.sort(key=lambda row : row['Distance'])

    for row in table:
        # allow for filtering by maximum distance
        if maxdist > 0 and row['Distance'] > maxdist:
            continue
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
        display_ntrip_table(ntrip_table, maxdist=args.maxdist)
