# NTRIP Browser

A simple Python API for browse NTRIP (Networked Transport of RTCM via Internet Protocol).  

### Dependencies

`geopy`
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


### Package API

 - `get_mountpoints(url, port, my_position, timeout)`. Return list of dictionaries.  
Input arguments:
    - url: NTRIP url
    - port: NTRIP port. Default value: 2101
    - my_position: Point for distance calculation. Point format - (float(lat), float(lon)). Default value: None
    - timeout: timeout for url request. Default value: None

Output keys:
```
"Mountpoint", "ID", "Format", "Format Details", "Carrier", "Nav System",
"Network", "Country", "Latitude", "Longitude", "NMEA", "SOL", "Generator",
"Compr-Encrp", "Authentication", "Fee", "Bitrate", "Other Details", "Distance"
```


```python
from ntripparser import get_mountpoints

mntpoints = get_mountpoints("ntrip.emlid.com", my_position=(59.96032, 30.33409))
for mnt in sorted(mntpoints, key=lambda mnt: mnt["Distance"]):
    print("{:10} ({}): {:.4f} km".format(mnt["Mountpoint"], mnt["Format"], mnt["Distance"]))
```

