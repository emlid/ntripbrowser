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
python ntripbrowser.py [-h] [-p PORT] [-v] [-n] [-c] [-t] [-s] url  

positional arguments:  
  url                   NTRIP soursetable address

optional arguments:  
  -h, --help            Show this help message and exit  
  -p PORT, --port PORT  Change url port. Standart port is 2101  
  -v, --verbose         Increase output verbosity  
  -n, --nettable        Additional show NET table  
  -c, --cattable        Additional show CAT table  
  -t, --terminal        Redirect output data to terminal  
  -s, --source          Display url sourse data  
  ```