from ntripbrowser import NtripBrowser
import json

host = "rtk2go.com"
coordinates = (47.1291, 15.2119)
maxdist = 50 #km

browser = NtripBrowser(host, port=2101, timeout=15,
coordinates=coordinates, maxdist=maxdist)
mp = browser.get_mountpoints()
print(json.dumps(mp, indent=4))
