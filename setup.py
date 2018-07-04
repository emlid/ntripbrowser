import os
import sys
from setuptools import setup


MAC_OS_ENVIRONMENT_VARIABLES = {
    'LDFLAGS': '-L/usr/local/opt/openssl/lib',
    'CPPFLAGS': '-I/usr/local/opt/openssl/include',
    'PKG_CONFIG_PATH': '/usr/local/opt/openssl/lib/pkgconfig',
    'PYCURL_SSL_LIBRARY': 'openssl',
}

if sys.platform.startswith('darwin'):
    os.environ.update(MAC_OS_ENVIRONMENT_VARIABLES)

setup(
    name='ntripbrowser',
    version='2.0.1',
    author='Andrew Yushkevich',
    author_email='andrew.yushkevich@emlid.com',
    packages=['ntripbrowser'],
    install_requires=['chardet', 'geopy>=1.14', 'texttable', 'pager', 'pycurl', 'cachecontrol>=0.12.4'],
    tests_requires=['pytest', 'mock', 'tox'],
    license='BSD-3-Clause',
    url='https://github.com/emlid/ntripbrowser.git',
    description='NTRIP cli browser',
    entry_points={
        'console_scripts': [
            'ntripbrowser = ntripbrowser.browser:main',
        ],
    },
)
