# usage
# echo "message" | socat - udp:192.168.48.32:11880
# ack

# runs both UDP and UART in async mode

from dgram import UDPServer
import uasyncio as asyncio
from machine import UART

# The table below specifies the RX and TX pins
# for each of the three UART ports available in ESP32.
# UART   TX/RX     RX     TX     Note
# UART0      0     GPIO3  GPIO1
# UART1            GPIO9  GPIO10 requires reassignment of pins
# UART2      2     GPIO16 GPIO17

uart = UART(2, 9600, timeout=0)
swriter = asyncio.StreamWriter(uart, {})
sreader = asyncio.StreamReader(uart)

port=11880
udpserv = UDPServer()

# https://github.com/perbu/dgram

def udpcb(msg, adr):
    print('Got:', msg)
    return 'ack\n'.encode('ascii')

#def udp_main():
#    s = UDPServer()
#    l = asyncio.get_event_loop()
#    l.run_until_complete(s.serve(cb, '0.0.0.0', port))

async def sender():
    print('started sender loop')
    while True:
        ascii = "step1\n"
        #print(f'writing >>>{ascii}<<<')
        print(ascii,end="")
        swriter.write(ascii)
        await swriter.drain()
        await asyncio.sleep(10)
        ascii = "step2\n"
        #print(f'writing >>>{ascii}<<<')
        print(ascii,end="")
        swriter.write(ascii)
        await swriter.drain()
        await asyncio.sleep(10)

async def receiver():
    print('started receiver loop')
    while True:
        # print('waiting on receive')
        res = await sreader.readline()
        print('Received', res)

async def main():
    asyncio.create_task(udpserv.serve(udpcb, '0.0.0.0', port))
    asyncio.create_task(sender())
    asyncio.create_task(receiver())
    
    while True:
        await asyncio.sleep(1)

def test():
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Interrupted')
    finally:
        asyncio.new_event_loop()
        print('asyncuart.test() to run again.')

test()
