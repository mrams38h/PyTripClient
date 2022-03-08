#!/usr/bin/env python3
#################################
######    PyTRIP Client    ######
###### MAX RAMSTORFER 2022 ######
#################################

### LIB pyserial mit 
###		python -m pip install pyserial
### installieren


###########################################################################################
import time
import socket
import os
import sys
import serial # pySerial
import base64
from optparse import OptionParser
import datetime

version=0.1
useragent="NTRIP PyTRIP_Client/%.1f" % version

def killall(aus):
    global socki, ser, file, GGAcount
    if serial != 0:
        ser.close()
        #print('Serial closed')
    if file != 0:
        file.close()
        #print('File closed')
    if socket is not None:
        socki.close()
        #print('Socket closed!')

    if aus != 9:
      print('\n\nConnection try %d von %d' % (GGAcount+1,maxGGAcount))
      if GGAcount == maxGGAcount:
          killall(9)
      else:
          GGAcount = GGAcount+1
          print('Reconnecting....')
          time.sleep(5)
          startfunc()
    else:
      print('### KILLALL (All Closed) ###')
      sys.exit(1)

def secs():
    return time.time()

def calcultateCheckSum(stringToCheck):
    xsum_calc = 0
    for char in stringToCheck:
        xsum_calc = xsum_calc ^ ord(char)
    return "%02X" % xsum_calc

def setPosition(lat, lon):
    global flagN, flagE, lonDeg, latDeg, lonMin, latMin
    flagN="N"
    flagE="E"
    if lon>180:
        lon=(lon-360)*-1
        flagE="W"
    elif (lon<0 and lon>= -180):
        lon=lon*-1
        flagE="W"
    elif lon<-180:
        lon=lon+360
        flagE="E"
    else:
        lon=lon
    if lat<0:
        lat=lat*-1
        flagN="S"
    lonDeg=int(lon)
    latDeg=int(lat)
    lonMin=(lon-lonDeg)*60
    latMin=(lat-latDeg)*60

def getGGABytes():
    global mode, gga, flagN, flagE, lonDeg, latDeg, lonMin, latMin
    if mode == 2:
        now = datetime.datetime.utcnow()
        ggaString= "GPGGA,%02d%02d%04.2f,%02d%010.7f,%1s,%03d%010.7f,%1s,1,09,0.19,%5.3f,M,45.60,M,," % \
            (now.hour,now.minute,now.second,latDeg,latMin,flagN,lonDeg,lonMin,flagE,height)
        checksum = calcultateCheckSum(ggaString)
        if verbose == 1 or verbose==3:
           print("$%s*%s" % (ggaString, checksum))
        return bytes("$%s*%s\r\n" % (ggaString, checksum),'ascii')
    if mode == 1:
        #if verbose==1 or verbose == 3:
            #print("%s" % (gga))
        return bytes("%s\r\n" % (gga),'ascii')

#########

def mainfunction():
    global socki, ser, file
    sent = 0
    ok = 0
    pre = 0
    count= 0
    curr =  0
    pre1 = 0
    flag = 1
    while flag == 1:
        curr = secs()
        if (curr-pre) > inter:
            pre = curr
            sent = 0
            ok = 0
 #           if maxGGAcount > 0:
 #               if count < maxGGAcount:
 #                   count = count+1
 #               else:
 #                   flag = 0
 #                   killall(9)
##        if (curr - pre1) > 60 and sent == 1:
##            pre1 = curr
##            socket.sendall(bytes(requeststring,'ascii'))
##            print('Send request String')

        if sent == 0:
            ##############################################
            if mode == 0:
                line = ser.readline()
                #print(line)
                try:
                    lin = str(line,'ascii')
                except Exception:
                    lin = '';
                if len(lin)>10:
                    if lin[0]=='$':
                        ok = 1
                        #print("Serial has "+str(len(lin))+" Bytes")
                        print(lin)
                        lin = lin +'\r\n'
                        socki.send(bytes(lin,'ascii'))
                        sent = 1

            ###############################################
            else:
                setPosition(lat, lon)
                los = getGGABytes()
                #print("GGABYTES has "+str(len(los))+" Bytes")
                ok = 1
                sent = 1
                #try:
                socki.send(los)
                #except socket.error:
                #    killall()

            ###############################################

        if ok == 1:
            try:
                data=socki.recv(1024)
                print("RTCM has "+str(len(data))+" Bytes")

                #high = data[5]
                #low = data[6]
                #msg = high*256+low;
                #print('MSG = %i'%msg)
                if data[0]!=211:
                     print(data)
                try:
                    if len(logfile) > 2:
                        file.write(data)
                        file.write(bytes('\r\n','ascii'))
                except IOError:
                    print('File Problem')
                    flag = 0
                    #break
                    killall(9)
                    sys.exit(1)
                ser.write(data)
            except :
                flag = 0
                print('RECV Timeout!')
                #break
                killall(0)

#########
def startfunc():
    global socki, ser, file, maxGGAcount, logfile
    try:
        ser = serial.Serial(device, baud, timeout=1, write_timeout=1)
        #print('Serial Open!')
    except serial.SerialException as e:
        print(e);
        sys.exit(1)
    except OSError as e:
        print(e)
        sys.exit(1)
    except serial.serialutil.SerialTimeoutException as e:
        print(e)
        sys.exit(1)
    except Exception as e:
        print(e)
        sys.exit(1)

    try:
        try:
            #if socki is None:
            socki = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socki.connect((caster,port));
 #       except socket.gaierror as e:
 #           print('GAI ERROR %s'%e)
 #           ser.close()
 #           sys.exit(1)
 #       except socket.timeout as e:
 #           print('Caster Timeout! %s'%e)
 #           ser.close()
 #           socket.close()
 #           sys.exit(1)
 #       except socket.error as e:
 #           print('Connection Error %s'%e)
 #           ser.close()
 #           sys.exit(1)
        except Exception as msg:
            print('Connection Error! %s' %msg)
            ser.close()
            sys.exit(1)
    except KeyboardInterrupt:
            print("User Interrupt: Going Home!")
            maxGGAcount = 1
            killall(9)
            sys.exit(9)

    socki.settimeout(10)
    socki.sendall(bytes(requeststring,'ascii'))
    casterResponse=socki.recv(100)
    header_lines = casterResponse.decode('utf-8').split("\r\n")
    print(header_lines)


    if header_lines[0].find('CETABLE')>0: # Wenn der satz mit dem Wort beginnt, dann kommt 0 raus!
        print("Wrong Mountpoint")
        killall(9)
        sys.exit(1)
    elif header_lines[0].find('401 Unauthorized')>0:
        print("Authorization Error")
        killall(9)
        sys.exit(1)
    elif header_lines[0].find('CY 200 OK')>0:
        print('OK')
        if len(logfile) > 2:
            nowi = datetime.datetime.today()
            logi = ('%s_%d%02d%02d.rtcmlog' % (logfile,nowi.year,nowi.month,nowi.day))
            print('Logfile Open: %s ' % logi)
            file = open(logi,'wb')
        mainfunction()

 ###############
usage="neuerntripclient.py [options]"
parser=OptionParser(version=str(version), usage=usage)

parser.add_option("-s", "--server", type="string", dest="caster", default="xxx", help="NTRIP Caster IP")
parser.add_option("-r", "--port", type="int", dest="port", default="2101", help="NTRIP Caster Port")
parser.add_option("-m", "--mount", type="string", dest="mountpoint", default="xxx", help="Mountpoint")
parser.add_option("-D", "--device", type="string", dest="dev", default="/dev/ttyUSB0", help="Serial Port")
parser.add_option("-B", "--baud", type="int", dest="baud", default="38400", help="Serial Baudrate")
parser.add_option("-u", "--user", type="string", dest="user", default="xxx", help="Username NTRIP Account")
parser.add_option("-p", "--password", type="string", dest="passwd", default="xxx", help="Password NTRIP Account")
parser.add_option("-t", "--latitude", type="float", dest="lat", default=0.0, help="Breitengrad 48.  Default: %default")
parser.add_option("-g", "--longitude", type="float", dest="lon", default=0.0, help="Laengengrad 16.  Default: %default")
parser.add_option("-e", "--height", type="float", dest="height", default=0, help="Hoehe.  Default: %default")
parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=3, help="Verbose. 0=nix, 1=gga+head, 2=rtcm, 3=alles")
parser.add_option("-a", "--gga", type="string", dest="gga", default='', help="GPGGA Sentence fuer fixe Position")
parser.add_option("-l", "--log", type="string", dest="log", default='', help="Log file for rtcm raw data")
parser.add_option("-M", "--max", type="int", dest="maxGGAcount", default='0', help="max. reconnection trys. 0 sendet fuer immer")
parser.add_option("-T", "--interval", type="int", dest="inter", default='5', help="GGA Send Interval in Sekunden")


(options, args) = parser.parse_args()

caster=options.caster
port=options.port
mtp=options.mountpoint
device=options.dev
baud=options.baud
user=options.user
passi=options.passwd
lat=options.lat
lon=options.lon
height=options.height
verbose=options.verbose
gga=options.gga
mode=1
logfile = options.log
flagN = "N"
flagE = "E"
lonDeg = 0.0
latDeg = 0.0
lonMin = 0.0
latMin = 0.0
maxGGAcount = options.maxGGAcount #Wieviele ggas gesendet werden bis programm beendet wird
inter = options.inter
GGAcount = 0
file = 0
ser = 0
socki = None

if gga != '':
    print('Fixed GGA Mode')
    mode = 1
elif lat>0 and lon>0 and height>0:
    mode = 2
    gga=setPosition(lat, lon)
    print("Fixed Pos Mode")
else:
    print("Live Mode")
    mode = 0

at=base64.b64encode(bytes(user+':'+passi,'utf-8')).decode("utf-8")

#requeststring = "GET RTK-3-ETRF HTTP/1.1\r\nUser-Agent: NTRIP Pytrip\r\nAuthorization: Basic "+at+"\r\nConnection: close\r\n\r\n"
requeststring = "GET %s HTTP/1.1\r\nUser-Agent: %s\r\nAuthorization: Basic %s\r\nConnection: close\r\n\r\n" % (mtp,useragent,at)


print('\n\n#################################')
print('######    PyTRIP Client    ######')
print('###### MAX RAMSTORFER 2022 ######')
print('#################################\n')

try:
 startfunc()
except KeyboardInterrupt:
     print('Key unten')
     killall(9)








