from setuptools import setup

setup(
    name='ntripbrowser',
    version='2.2.0',
    author='Andrew Yushkevich, Alexander Yashin',
    author_email='andrew.yushkevich@emlid.com, alexandr.yashin@emlid.com',
    packages=['ntripbrowser'],
    install_requires=['cchardet>=2.1.4', 'geopy>=1.14', 'texttable', 'pager', 'pycurl', 'cachecontrol>=0.12.4'],
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
