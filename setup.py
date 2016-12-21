from setuptools import setup

setup(
    name='ntripbrowser',
    version='0.0.7',
    author='Ivan Sapozhkov',
    author_email='ivan.sapozhkov@emlid.com',
    packages=['ntripbrowser'],
    install_requires=['texttable'],
    license = 'GPLv3',
    url='https://github.com/emlid/ntripbrowser.git',
    description='NTRIP Browser for terminal',
    long_description=open('README.md').read(),
    entry_points = {
        'console_scripts': [
            'ntripbrowser = ntripbrowser.ntripbrowser:main',
        ],
    },
)
