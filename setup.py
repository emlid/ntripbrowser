from distutils.core import setup

setup(
    name='ntripbrowser',
    version='0.0.1',
    author='Ivan Sapozhkov',
    author_email='ivan.sapozhkov@emlid.com',
    py_modules=['ntripbrowser'],
    license = 'GPLv3',
    url='https://github.com/emlid/ntripbrowser.git',
    description='NTRIP Browser for terminal',
    long_description=open('README.md').read(),
)
