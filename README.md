# rptrlist2kml
This program will convert the WWARA repeater list CSV file into a KML file that can display all of the repeaters in Google Earth.

The [WWARA](https://www.wwara.org/) provides a database of all the ham radio repeaters in western Washington state.  
The database is updated frequently and the current version can be downloaded from [here](https://www.wwara.org/DataBaseExtract.zip).  



## Usage:
To convert the repeater list CSV file into a KML file run:
``` 
rptrlist2kml.py -i WWARA-rptrlist.csv Repeaters.kml
```

If no output filename is given, the output will be written to STDOUT.  
Use "-" as the input filename if you want to read from STDIN.

## Requirements
* Python 3.6 or newer.
