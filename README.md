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
  -p PORT, --port PORT  Change url port. Default port is 2101  
  -v, --verbose         Increase output verbosity  
  -N, --NETtable        Additionaly show NET table  
  -C, --CATtable        Additionaly show CAT table  
  -n, --no-pager        No pager  
  -s, --source          Display url source data  
  -t, --timeout         Add timeout  
  -b, --BasePointCoord  Add base point coordinates x,y
  ```

### Package API

Output keys:
-STR:
  ```
  "Mountpoint", "ID", "Format", "Format Details", "Carrier", "Nav System",
  "Network", "Country", "Latitude", "Longitude", "NMEA", "SOL", "Generator",
  "Compr-Encrp", "Authentication", "Fee", "Bitrate", "Other Details", "Distance"
  ```
-CAS:
  ```
  "Host", "Port", "ID", "Operator", "NMEA", "Country", "Latitude", "Longitude",
  "FallbackHost","FallbackPort","Site", "Other Details", "Distance"
  ```
-NET:
  ```
  "ID", "Operator", "Authentication", "Fee", "Web-Net", "Web-Str", "Web-Reg", 
  "Other Details"
  ```


```python
python ntripbrowser.py "url"
```

