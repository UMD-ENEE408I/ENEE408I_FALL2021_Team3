# This program waits for packets from the mouse
# and sends responses

import struct
import time
import serial

# This is the definition of the packet in C++
# typedef struct packet {
#   float a_float;
#   int32_t a_signed_int;
#   uint8_t a_two_d_array[3][8];
# } packet_t;

# Packet format string
# https://docs.python.org/3/library/struct.html#format-strings
# https://docs.python.org/3/library/struct.html#format-characters
# 3*8*'B' means 24 B characters in a row
packet_format_str = 'fi' + 3*8*'B'
packet_size = struct.calcsize(packet_format_str)

# The magic header helps with aligining the serial streams
# (e.g. you don't want to begin reading bytes in the middle of a transmission)
magic_header = [0x8B, 0xEA, 0x27, 0x55]
magic_header_format_str = 'BBBB'
def check_header(possible_header):
    for x, y in zip(possible_header, magic_header):
        if x != y:
            return False
    return True

def try_receive_packet(connection):
    if connection.in_waiting >= 4:
        possible_header = connection.read(size=4)
        possible_header_unpacked = struct.unpack(magic_header_format_str, possible_header)
        if check_header(possible_header_unpacked):
            packet = connection.read(size=packet_size)
            packet_unpacked = struct.unpack(packet_format_str, packet)
            return packet_unpacked
    return None

def send_packet(connection, packet):
    packet_packed = struct.pack(packet_format_str, *packet)
    bytes_written = 0
    while True:
        bytes_written += connection.write(packet_packed)
        if bytes_written < packet_size:
            time.sleep(0.001)
        else:
            break

if __name__ == '__main__':
    connection = serial.Serial(port='/dev/ttyUSB0', baudrate=115200)

    transmit_packet = [0.0, 0] + 3*8*[0]

    while True:
        new_packet = try_receive_packet(connection)
        if new_packet is not None:
            # Got a packet, lets print it!
            print('Received: {}'.format(new_packet))

            # Try to send something back
            transmit_packet[0] += 1
            #transmit_packet[1] += 1
            print('Sending: {}'.format(transmit_packet))
            send_packet(connection, transmit_packet)                
        else:
            time.sleep(0.01)
