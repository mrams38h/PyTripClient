# PyTripClient
Ntrip client written in python with many debugging options

This special NTRIP Client is written to be used on an Raspberry Pi Zero with a Novatel SPAN-SE INS system.
For detailed instructions how to use ist, see inside the script.

It can take a position from the SPAN, send it to the NTRIP Server and send the repeated RTCM data back to the SPAN. 
There is also the posibility to set a fix position, only send the RCTM data to the SPAN and ignore serial input from SPAN.

## Installing
Install pyserial with the command python3 -m pip install pyserial


## Usage:
python3 pytripclient.py <options>
  
-s  --server  IP
  
-r  --port  port
  
-m  --mount Mountpoint
  
-D  --device  Serial Port
  
-B  --baud  Baud Rate
  
-u  --user  Username
  
-p  --password Passsword
  
-t  --latitude  optional Latitude (48.12)
  
-g  --longitude optional Longitude (16.xx)
  
-e  --height optional height in m
  
-v  --verbose 0,1,2
  
-a  --gga optional full GGA String
  
-l  --log logfile path
  
-M  --max max. reconnect trys
  
-T  --interval  gga resend intervall in secs
  
