# NTRIP Browser

A simple Python API for browse NTRIP (Networked Transport of RTCM via Internet Protocol).  

### Dependencies

`geopy`
`chardet`

The package was tested with **Python 2.7**

### Installation

`pip install ntripbrowser`

or clone and run `make install`

### Usage 

```
ntripbrowser [-h] [-p PORT] [-v] [-N] [-C] [-n] [-s] [-t] [-b] url  

positional arguments:  
  url                   NTRIP source table address

optional arguments:  
  -h, --help            Show this help message and exit  
  -p PORT, --port PORT  Set url port. Standard port is 2101  
  -t, --timeout         Add timeout  
  -c, --coordinates     Add NTRIP station distance to this coordinate
  ```

### Package API

```python
get_mountpoints(url, timeout=None, coordinates=None)
```
Arguments:

  `-url`   

Optional arguments:

  `-timeout`     
  `-coordinates`   

### Console Command
```python
python ntripbrowser.py "url"
```

