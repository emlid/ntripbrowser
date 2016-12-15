from distutils.core import setup

setup(
    name='ntripbrowser',
    version='0.0.5',
    author='Ivan Sapozhkov',
    author_email='ivan.sapozhkov@emlid.com',
    py_modules=['ntripbrowser'],
    install_requires=['texttable'],
    license = 'GPLv3',
    url='https://github.com/emlid/ntripbrowser.git',
    description='NTRIP Browser for terminal',
    long_description=open('README.md').read(),
    entry_points = {
        'console_scripts': [
            'ntripbrowser = ntripbrowser:main',
        ],
    },
)
