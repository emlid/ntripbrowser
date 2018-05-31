# NTRIP Browser

A Python API for browsing NTRIP (Networked Transport of RTCM via Internet Protocol).

## Requirements
 - geopy
 - pycurl
 - chardet
 - texttable
 - Python 2.6–2.7 & 3.4–3.6

## Installation

 - `pip install ntripbrowser`

 -  or clone and run `make install`

## Usage 

```
ntripbrowser [-h] [-p] [-t] [-c] host

positional arguments:  
  host                  NTRIP source table host address

optional arguments:  
  -h, --help            Show this help message and exit  
  -p, --port            Set url port. Standard port is 2101  
  -t, --timeout         Add timeout  
  -c, --coordinates     Add NTRIP station distance to this coordinate
 ```

#### CLI workflow example:

    ntripbrowser cddis-caster.gsfc.nasa.gov -p 443 -t 5 -c 1.0 2.0

## Package API
#### Workflow example:

```python
browser = NtripBrowser(host, port=2101, timeout=None, coordinates=None)
browser.get_mountpoints()
browser.host = another_host
browser.get_mountpoints()
```

#### Arguments:

 - `host`

> NTRIP caster host.
> Standard port is 2101, use `:port` optional argument to set another one.

#### Optional arguments:

 - `port`

> NTRIP caster port.

 - `timeout`    
 
> Use `timeout` to define, how long to wait for a connection to NTRIP caster.
 - `coordinates`
 
> Use `coordinates` to pass your position coordinates in function and get distance to NTRIP station.    
> Form of coordiantes must be `(x, y)` or `(x.x, y.y)` of latitude, longitude.

#### Result

As a result you'll get a dictionary consisting of a lists of dictionaries with such structure:

- CAS stations: `"Host", "Port", "ID", "Operator", "NMEA", "Country", "Latitude", "Longitude", "FallbackHost", "FallbackPort", "Site", "Other Details", "Distance"` 

- NET stations: `"ID", "Operator", "Authentication", "Fee", "Web-Net", "Web-Str", "Web-Reg", "Other Details", "Distance"`    

- STR stations: `"Mountpoint", "ID", "Format", "Format-Details","Carrier", "Nav-System", "Network", "Country", "Latitude", "Longitude", "NMEA", "Solution", "Generator", "Compr-Encryp", "Authentication", "Fee", "Bitrate", "Other Details", "Distance"`

#### Exceptions

 - `ntripbrowser.NtripbrowserError` - base class for all ntripbrowser exceptions.
 - `ntripbrowser.UnableToConnect` - raised when ntripbrowser could not connect to the assigned url.
 - `ntripbrowser.NoDataReceivedFromCaster` - raised when ntripbrowser could not find any data on the page.
 - `ntripbrowser.ExceededTimeoutError` - raised when connection timeout is exceeded.
 - `ntripbrowser.HandshakeFiledError` - raised when connection handshake is failed.

## To test

    make test

#### Known Issues
Tests with `tox` may fail if python*-dev is not installed.
So, you need to install python2.7-dev and python3.6-dev:

    sudo apt-get install python2.7-dev
    sudo apt-get install python3.6-dev


