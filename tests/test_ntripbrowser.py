import pytest
from collections import namedtuple

from ntripbrowser import (NtripBrowser, UnableToConnect, ExceededTimeoutError,
                          NoDataReceivedFromCaster)
import testing_content


Caster = namedtuple('Caster', ['url', 'port'])

HTTP_CASTER = Caster('euref-ip.net', 2101)
HTTPS_CASTER = Caster('cddis-caster.gsfc.nasa.gov', 443)
WIN1252_CASTER = Caster('rtk.geospider.ru', 8032)
HTML_PAGE_CASTER = Caster('193.190.66.25', 2102)
HEADERLESS_CASTER = Caster('195.77.88.220', 2101)
NONEXISTENT_CASTER = Caster('emlid.com', 443)
INCOMPLETE_DATA_CASTER = Caster('rtk.topnetlive.com', 2101)


def run_caster_test(caster):
    browser = NtripBrowser(caster.url, caster.port)
    try:
        browser.get_mountpoints()
    except (UnableToConnect, ExceededTimeoutError):
        pass


def test_http_caster():
    run_caster_test(HTTP_CASTER)


def test_https_caster():
    run_caster_test(HTTPS_CASTER)


def test_win1252_caster():
    run_caster_test(WIN1252_CASTER)


def test_html_page_caster():
    run_caster_test(HTML_PAGE_CASTER)


def test_headerless_caster():
    run_caster_test(HEADERLESS_CASTER)


def test_incomplete_data_caster():
    run_caster_test(INCOMPLETE_DATA_CASTER)


def test_nonexistent_caster():
    with pytest.raises(NoDataReceivedFromCaster):
        run_caster_test(NONEXISTENT_CASTER)


def test_reassign_parameters():
    browser = NtripBrowser('example', 1234)
    assert [
               'http://example:1234',
               'http://example:1234/sourcetable.txt',
               'https://example:1234',
               'https://example:1234/sourcetable.txt',
           ] == browser.urls
    browser.host = 'http://sample'
    browser.port = 4321
    assert [
               'http://sample:4321',
               'http://sample:4321/sourcetable.txt',
               'https://sample:4321',
               'https://sample:4321/sourcetable.txt',
           ] == browser.urls
    browser.host = 'https://eg'
    browser.port = 123
    assert [
               'http://eg:123',
               'http://eg:123/sourcetable.txt',
               'https://eg:123',
               'https://eg:123/sourcetable.txt',
           ] == browser.urls


def test_invalid_data():
    browser = NtripBrowser('example', 1234)
    with pytest.raises(NoDataReceivedFromCaster):
        browser._process_raw_data(b'<Some invalid NTRIP data>')


def test_valid_net_data():
    browser = NtripBrowser('test', 1234)
    assert browser._process_raw_data(testing_content.VALID_NET_NTRIP) == {
        'cas': [],
        'net': [
            {
                'Authentication': 'B',
                'Distance': None,
                'Fee': 'N',
                'ID': 'Str1',
                'Operator': 'Str2',
                'Other Details': 'none',
                'Web-Net': 'https://example.htm',
                'Web-Reg': 'http://sample',
                'Web-Str': 'http://example.htm'
            }
        ],
        'str': []
    }


def test_valid_str_data():
    browser = NtripBrowser('test', 1234)
    assert browser._process_raw_data(testing_content.VALID_STR_NTRIP) == {
        'cas': [],
        'net': [],
        'str': [
            {
                'Carrier': 'https://example2.htm',
                'Country': 'none',
                'Distance': None,
                'Format': 'B',
                'Format-Details': 'N',
                'ID': 'Str4',
                'Mountpoint': 'Str3',
                'Nav-System': 'http://example2.htm',
                'Network': 'http://sample2'
             }
        ]
    }


def test_valid_cas_data():
    browser = NtripBrowser('test', 1234)
    assert browser._process_raw_data(testing_content.VALID_CAS_NTRIP) == {
        'cas': [
            {
                'Country': 'Null',
                'Distance': None,
                'FallbackHost': '1.2.3.4',
                'FallbackPort': '5',
                'Host': 'example',
                'ID': 'NtripCaster',
                'Latitude': '11',
                'Longitude': '22.33',
                'NMEA': '0',
                'Operator': 'None',
                'Port': '2101',
                'Site': 'http://sample.htm'
            }
        ],
        'net': [],
        'str': []
    }


def test_valid_data():
    browser = NtripBrowser('test', 1234)
    assert browser._process_raw_data(testing_content.VALID_NTRIP) == {
        'cas': [
            {
                'Country': 'Null',
                'Distance': None,
                'FallbackHost': '1.2.3.4',
                'FallbackPort': '5',
                'Host': 'example',
                'ID': 'NtripCaster',
                'Latitude': '11',
                'Longitude': '22.33',
                'NMEA': '0',
                'Operator': 'None',
                'Port': '2101',
                'Site': 'http://sample.htm'
            }
        ],
        'net': [
            {
                'Authentication': 'B',
                'Distance': None,
                'Fee': 'N',
                'ID': 'Str1',
                'Operator': 'Str2',
                'Other Details': 'none',
                'Web-Net': 'https://example.htm',
                'Web-Reg': 'http://sample',
                'Web-Str': 'http://example.htm'
            }
        ],
        'str': [
            {
                'Carrier': 'https://example2.htm',
                'Country': 'none',
                'Distance': None,
                'Format': 'B',
                'Format-Details': 'N',
                'ID': 'Str4',
                'Mountpoint': 'Str3',
                'Nav-System': 'http://example2.htm',
                'Network': 'http://sample2'
             }
        ]
    }


def test_add_coordinates():
    browser = NtripBrowser('test', 1234, coordinates=(1.0, 2.0))
    assert browser._process_raw_data(testing_content.VALID_NTRIP) == {
        'cas': [
            {
                'Country': 'Null',
                'Distance': 2505.0572138274565,
                'FallbackHost': '1.2.3.4',
                'FallbackPort': '5',
                'Host': 'example',
                'ID': 'NtripCaster',
                'Latitude': '11',
                'Longitude': '22.33',
                'NMEA': '0',
                'Operator': 'None',
                'Port': '2101',
                'Site': 'http://sample.htm'
            }
        ],
        'net': [
            {
                'Authentication': 'B',
                'Distance': None,
                'Fee': 'N',
                'ID': 'Str1',
                'Operator': 'Str2',
                'Other Details': 'none',
                'Web-Net': 'https://example.htm',
                'Web-Reg': 'http://sample',
                'Web-Str': 'http://example.htm'
            }
        ],
        'str': [
            {
                'Carrier': 'https://example2.htm',
                'Country': 'none',
                'Distance': None,
                'Format': 'B',
                'Format-Details': 'N',
                'ID': 'Str4',
                'Mountpoint': 'Str3',
                'Nav-System': 'http://example2.htm',
                'Network': 'http://sample2'
             }
        ]
    }

def test_max_dist_trimmed():
    near_parsed = {
        'Mountpoint': 'near',
        'ID': 'Rehakka',
        'Format': 'RTCM 3.3',
        'Format-Details': '1004(1),1005(10),1008(10),1012(1),1019(3),1020(2),1033(10),1042(3),1046(1),1077(1),1087(1),1097(1),1127(1),1230(30)',
        'Carrier': '2',
        'Nav-System': 'GPS+GLO+GAL+BDS',
        'Network': 'SNIP',
        'Country': 'FIN',
        'Latitude': '1.1',
        'Longitude': '2.2',
        'NMEA': '1',
        'Solution': '0',
        'Generator': 'sNTRIP',
        'Compr-Encryp': 'none',
        'Authentication': 'B',
        'Fee': 'N',
        'Bitrate': '12220',
        'Other Details': '',
        'Distance': 24.8552454935518,
    }
    far_parsed = {
        'Mountpoint': 'far',
        'ID': 'Drummond',
        'Format': 'RTCM 3.2',
        'Format-Details': '1005(10),1074(1),1084(1),1094(1),1124(1),1230(1)',
        'Carrier': '2',
        'Nav-System': 'GPS+GLO+GAL+BDS',
        'Network': 'SNIP',
        'Country': 'BRA',
        'Latitude': '10.1',
        'Longitude': '20.2',
        'NMEA': '1',
        'Solution': '0',
        'Generator': 'sNTRIP',
        'Compr-Encryp': 'none',
        'Authentication': 'B',
        'Fee': 'N',
        'Bitrate': '7300',
        'Other Details': '',
        'Distance': 2251.719387114077,
    }
    test_cases = {
        50: [near_parsed],
        2500: [near_parsed, far_parsed],
    }
    for maxdist, expected_str in test_cases.items():
        browser = NtripBrowser('test', 1234, coordinates=(1.0, 2.0), maxdist=maxdist)
        assert browser._process_raw_data(testing_content.VALID_NTRIP_TRIM_DISTANCE)['str'] == expected_str
