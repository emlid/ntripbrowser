from setuptools import setup

setup(
    name='ntripbrowser',
    version='1.1.1',
    author='Andrew Yushkevich',
    author_email='andrew.yushkevich@emlid.com',
    packages=['ntripbrowser'],
    install_requires=['chardet', 'geopy', 'texttable', 'pager', 'pycurl'],
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
