#!/usr/bin/python3

#   @file       deserializer_kiss.py (keep it simple stupid)
#
#   @about      The most simpliest of examples for deserializing and parsing
#               serial packets.
#
#               |       PACKET      |
#               | <marker> | <data> |
#
#               <marker>    -   Uniquely identifies the start of a packet
#               <data>      -   The data section of the packet
#
#   @notes      There are a few disadvantages and limitations to this
#               implementation...
#                   1)  Length is calculated and explicitly defined on the 
#                       receiving side (this side) and also the sending side.
#                       Ideally, we should define it on the sending side as a 
#                       field in the packet. This way the receiving side could 
#                       parse the length field and use it as input into the 
#                       serial.read function to get the remainder of the packet
#                   2)  There is no way to validate the contents of the packet.
#                       Ideally, a mechanism would be used to validate the 
#                       contents (e.g. CRC, Checksum). This would require we 
#                       add an additional field (preferrably on the end of the 
#                       packet).
#                   3)  All the above would require a more elaborate packet 
#                       protocol (e.g. CCSDS). Since this is a keep it simple 
#                       stupid example a CCSDS protocol is out of scope.
#
#   @sender     Below is the packet implementation on the sender side that is 
#               being implemented.
#                   from pyb import UART
#                   import struct
#                   import time
#                   class Packet:
#                       def __init__(self, m, x, y, z):
#                           self.m = m
#                           self.x = x
#                           self.y = y
#                           self.z = z
#                       def serialize(self):
#                           return struct.pack(
#                               '<IIII',
#                               self.m,
#                               self.x,
#                               self.y,
#                               self.z)
#                   uart = UART(1, 115200)
#                   pkt = Packet(0xdeadbeef, 0xaa, 0xbb, 0xcc)
#                   while True:
#                       time.sleep(1)
#                       uart.write(pkt.serialize())
#
#   @result     Below is what the expected output of this program would be. The 
#               messages would appear across the console at a 1Hz rate
#                   > ./deserializer_kiss.py
#                   x: 0x000000aa, y: 0x000000bb, z: 0x000000cc
#                   x: 0x000000aa, y: 0x000000bb, z: 0x000000cc
#                   x: 0x000000aa, y: 0x000000bb, z: 0x000000cc


import serial
import struct


class Marker:
    """
    @class      Marker
    @about      A component level class defining a sync marker
    @attrb      
                marker  -   The sync marker
                format  -   The format string of the sync marker
    """
    def __init__(self, marker, format):
        self.marker = marker
        self.format = format
        self.length = struct.calcsize(self.format)

    def sync(self, bytes_object: bytes) -> bool:
        result = struct.unpack(self.format, bytes_object)[0]
        if self.marker == result:
            return True
        else:
            return False

class Packet:
    """
    @class      Packet
    @about      A class for defining a packet of data and through composition 
                a marker component
    @attrb      (see class marker)
    """
    def __init__(self, marker, marker_format):
        self.marker = Marker(marker, marker_format)

        self.format = '<III'
        self.length = struct.calcsize(self.format)

        self.x = 0 
        self.y = 0 
        self.z = 0

    def deserialize(self, bytes_object: bytes) -> None:
        pkt = struct.unpack(self.format, bytes_object)
        self.x = pkt[0]
        self.y = pkt[1]
        self.z = pkt[2]

    def log(self) -> None:
        print("x: 0x{:08x}, y: 0x{:08x}, z: 0x{:08x}".format(
            self.x, self.y, self.z))


def main():
    """
    1)  Obtain sync by reading one byte at a time. It's ok to read one byte at 
        a time when dealing with packets on serial interface. This will ensure 
        good sync is kept.
    2)  Once sync is obtained read the rest of the packet based on the length
        of the packet. 
    3)  Repeat
    """
    packet = Packet(0xdeadbeef, '<I')
    serial_port = serial.Serial("/dev/ttyUSB0", 115200)

    while True:

        # Obtain sync 
        raw_bytes_object = serial_port.read(packet.marker.length)
        if packet.marker.sync(raw_bytes_object):
            # Read packet
            raw_bytes_object = serial_port.read(packet.length)
            packet.deserialize(raw_bytes_object)
            packet.log()
        
        # Future implementation of more than one packet type can be supported by
        # creating more packet classes and extending to more elif statements. 
        # However, a dictionary lookup would be more efficient than several 
        # elif statements here. This way the application doesn't have to 
        # evaluate each elif statement. 

    
if __name__ == "__main__":
    main()