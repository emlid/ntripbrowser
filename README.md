# NTRIP Browser

A simple Python API for browse NTRIP (Networked Transport of RTCM via Internet Protocol).  

## Dependencies

`geopy`
`chardet`
`texttable`

The package was tested with **Python 2.7**

## Installation

 - `pip install ntripbrowser`

 -  or clone and run `make install`

## Usage 

```
ntripbrowser [-h] [-p] [-t] [-c] url  

positional arguments:  
  url                   NTRIP source table address

optional arguments:  
  -h, --help            Show this help message and exit  
  -p, --port            Set url port. Standard port is 2101  
  -t, --timeout         Add timeout  
  -c, --coordinates     Add NTRIP station distance to this coordinate
 ```

## Package API

```python
get_mountpoints(url, timeout=None, coordinates=None)
```
####Arguments:

 - `url`    
 
> Use `url` only with *http://* to pass url variable in function.       
> Standard port is 2101, use `:port` after `url` to set another one.    
> Example: *http://192.168.1.0:2101* or  *http://ntrip.emlid.com:2101*.

####Optional arguments:

 - `timeout`    
 
> Use `timeout` to pass timeout in function. It must be integer.    

 - `coordinates`    
 
> Use `coordinates` to pass your position coordinates in function and get distance to NTRIP station.    
> Form of coordiantes must be `(x, y)` or `(x.x, y.y)` of latitude, longitude.

####Result

As a result you'll get a dictionary consisting of a lists of dictionaries with such structure:

- CAS stations: `"Host", "Port", "ID", "Operator", "NMEA", "Country", "Latitude", "Longitude", "FallbackHost", "FallbackPort", "Site", "Other Details"` 

- NET stations: `"ID", "Operator", "Authentication", "Fee", "Web-Net", "Web-Str", "Web-Reg", "Other Details"`    

- STR stations: `"Mountpoint", "ID", "Format", "Format-Details","Carrier", "Nav-System", "Network", "Country", "Latitude", "Longitude", "NMEA", "Solution", "Generator", "Compr-Encrp", "Authentication", "Fee", "Bitrate", "Other Details"`    

##Example    
```python
from ntripbrowser import get_mountpoints
print get_mountpoints('http://emlid.ntrip.com:2101', 1, (0.0, 0.0))
```
