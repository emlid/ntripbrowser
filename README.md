# NTRIP Browser

A simple Python API for browse NTRIP (Networked Transport of RTCM via Internet Protocol).  

## Dependencies

`geopy`
`chardet`

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
 
> Use `coordinates` to pass your position coordinates in function.    
> Form of coordiantes must be `(x, y)` or `(x.x, y.y)` of latitude, longitude.

