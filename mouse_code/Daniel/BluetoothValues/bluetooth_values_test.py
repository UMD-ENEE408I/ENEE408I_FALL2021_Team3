import asyncio
from bleak import BleakClient
import struct
import time

address = "58:98:22:7D:03:70"
# MOTOR_CHAR_UUID = "0fe79935-cd39-480a-8a44-06b70f36f249"
MOTOR_CHAR_UUID = "58BA3821-E0E9-4474-8E94-FA6A78315A3F"

async def run(address):
    async with BleakClient(address) as client:
        left_value = -15
        right_value = -20

        t_start = time.time()
        for i in range(40):
            await client.write_gatt_char(MOTOR_CHAR_UUID, struct.pack('hh', left_value, right_value))

            value = await client.read_gatt_char(MOTOR_CHAR_UUID)
            (left_value, right_value) = struct.unpack('hh', value)
            print("value: {} {}".format(left_value, right_value))

            left_value += 1
            right_value += 1
        t_end = time.time()

        print('{} Hz'.format(40*2 / (t_end-t_start)))

loop = asyncio.get_event_loop()
loop.run_until_complete(run(address))
