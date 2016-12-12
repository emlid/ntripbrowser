# NTRIP Browser

A simple Python API for browse NTRIP (Networked Transport of RTCM via Internet Protocol).  

### Dependencies

`texttable`

The package was tested with **Python 2.7**

### Installation

`pip install ntripbrowser`

or clone and run `make install`

### Usage 

```
ntripbrowser [-h] [-p PORT] [-v] [-N] [-C] [-n] [-s] url  

positional arguments:  
  url                   NTRIP source table address

optional arguments:  
  -h, --help            Show this help message and exit  
  -p PORT, --port PORT  Change url port. Default port is 2101  
  -v, --verbose         Increase output verbosity  
  -N, --NETtable        Additionaly show NET table  
  -C, --CATtable        Additionaly show CAT table  
  -n, --no-pager        No pager  
  -s, --source          Display url source data  
  ```
