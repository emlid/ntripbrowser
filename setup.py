from setuptools import setup

from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md')) as f:
    readme = f.read()

setup(
    name='ntripbrowser',
    version='2.2.2',
    author='Andrew Yushkevich, Alexander Yashin',
    author_email='andrew.yushkevich@emlid.com, alexandr.yashin@emlid.com',
    packages=['ntripbrowser'],
    install_requires=['cchardet>=2.1.4', 'geopy>=1.14', 'texttable', 'pager', 'pycurl', 'cachecontrol>=0.12.4'],
    tests_requires=['pytest', 'mock', 'tox'],
    license='BSD-3-Clause',
    url='https://github.com/emlid/ntripbrowser.git',
    description='CLI tool to easily get NTRIP caster information',
    long_description=readme,
    long_description_content_type='text/markdown',
    entry_points={
        'console_scripts': [
            'ntripbrowser = ntripbrowser.browser:main',
        ],
    },
)
