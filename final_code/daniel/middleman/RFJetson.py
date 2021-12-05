# This program waits for packets from the mouse
# and sends responses

import struct
import time
import serial


class RFJetson:

    # This is the definition of the packet in C++
    # typedef struct packet {
    #   float a_float;
    #   int32_t a_signed_int;
    #   uint8_t a_two_d_array[3][8];
    # Acutually this:
    #   byte movementCommand; // 0 stop, 1 forward, 2 left, 3 right
    #   int distance;
    #   byte response;
    # } packet_t;

    # Packet format string
    # https://docs.python.org/3/library/struct.html#format-strings
    # https://docs.python.org/3/library/struct.html#format-characters
    # 3*8*'B' means 24 B characters in a row

    # byte is the same as unsigned char
    # packet_format_str = 'fi' + 3*8*'B'
    packet_format_str = 'ii'
    packet_size = struct.calcsize(packet_format_str)

    # The magic header helps with aligining the serial streams
    # (e.g. you don't want to begin reading bytes in the middle of a transmission)
    magic_header = [0x8B, 0xEA, 0x27]
    magic_header_format_str = 'BBB'

    connection = None

    def __init__(self, serial_port):

        if self.connection is None:
            self.connection = serial.Serial(port=serial_port, baudrate=115200)
        
        self.setupRF()


    def __check_header(self, possible_header):
        for x, y in zip(possible_header, self.magic_header):
            if x != y:
                return False
        return True

    def __try_receive_packet(self):
        # if connection.in_waiting >= 4:
        
        possible_header = self.connection.read(size=1)
        possible_header_unpacked = struct.unpack('B', possible_header)
        # print(possible_header_unpacked[0], 0x8B)
        if possible_header_unpacked[0] == 0x8B:
            # print("check1")
            next_header = self.connection.read(size=1)
            possible_header_unpacked2 = struct.unpack('B', next_header)
            if possible_header_unpacked2[0] == 0xEA:
                # print("check2")
                next_header2 = self.connection.read(size=1)
                possible_header_unpacked3 = struct.unpack('B', next_header2)
                # print(possible_header_unpacked3)
                if possible_header_unpacked3[0] == 0x27:
                    # print("here")
                    packet = self.connection.read(size=self.packet_size)
                    # print(packet)
                    packet_unpacked = struct.unpack(self.packet_format_str, packet)
                    # print(packet_unpacked)
                    return packet_unpacked
        
        return None

    def __send_packet(self, packet):
        packet_packed = struct.pack(self.packet_format_str, *packet)
        bytes_written = 0
        while True:
            bytes_written += self.connection.write(packet_packed)
            if bytes_written < self.packet_size:
                time.sleep(0.001)
            else:
                break

    def send(self, command):

        transmit_packet = [command, 2]

        print('sending {}'.format(transmit_packet))
        self.__send_packet(transmit_packet)
        
        new_packet = self.__try_receive_packet()
        while new_packet is None:
            # print('sending {}'.format(transmit_packet))
            # send_packet(connection, transmit_packet)
            start = time.time()
            while time.time() - start < 10.0:
                new_packet = self.__try_receive_packet()
                if new_packet is not None:
                    break
                time.sleep(0.01)

            if new_packet is None:
                self.__send_packet(transmit_packet)
                print('sent again')
            # print('new packet', new_packet)

        print("received {}".format(new_packet))

        return new_packet


    def setupRF(self):
        resp = None
        
        while (200,200) != resp:
            resp = self.send(0)
            time.sleep(3)




# if __name__ == '__main__':
#     connection = serial.Serial(port='/dev/cu.usbserial-1440', baudrate=115200)

#     setupRF(connection)

#     time.sleep(3)

#     send(connection, 1)

#     time.sleep(3)

#     send(connection, 2)
    





