from setuptools import setup

setup(
    name='ntripbrowser',
    version='1.1.0',
    author='Andrew Yushkevich',
    author_email='andrew.yushkevich@emlid.com',
    packages=['ntripbrowser'],
    install_requires=['chardet', 'geopy','texttable'],
    license = 'BSD-3-Clause',
    url='https://github.com/emlid/ntripbrowser.git',
    description='NTRIP Browser for terminal',
    long_description=open('README.md').read(),
    entry_points = {
        'console_scripts': [
            'ntripbrowser = ntripbrowser.ntripbrowser:main',
        ],
    },
)
