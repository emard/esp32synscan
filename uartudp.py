# usage
# UDP: send "message"
# UART: type "reply" CTRL-J within 60 seconds after "message"
# echo "message" | socat -t 60 - udp:192.168.48.32:11880

# runs both UDP and UART in async mode

from dgram import UDPServer # https://github.com/perbu/dgram
import uasyncio as asyncio
from machine import UART,Pin
from micropython import const

# The table below specifies the RX and TX pins
# for each of the three UART ports available in ESP32.
# UART   TX/RX     RX     TX     Note
# UART0      0     GPIO3  GPIO1
# UART1            GPIO9  GPIO10 requires reassignment of pins
# UART2      2     GPIO16 GPIO17

BAUD=const(9600)
TX=const(17)
RX=const(16)
TIMEOUT_ms=const(20)
buf = bytearray(1024)
uart=UART(2,BAUD,tx=TX,rx=RX,timeout=TIMEOUT_ms)
swriter=asyncio.StreamWriter(uart, {})
sreader=asyncio.StreamReader(uart)

port=11880
udpserv=UDPServer()
led=Pin(2,Pin.OUT)

def udpcb(msg, adr):
    led(1)
    print('UDP->UART:', msg)
    swriter.write(msg)
    # if serial data were available already,
    # we could reply instantly
    #return 'ack\n'.encode('ascii')
    # but 9600 baud is slow
    led(0)
    return None

# not used
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

async def receiver_defunct():
    #print('started receiver loop')
    while True:
        #print('waiting on receive')
        res = await sreader.readline()
        led(1)
        if udpserv.addr:
          print('UART->UDP:',res)
          udpserv.sock.sendto(res, udpserv.addr)
        led(0)

async def receiver():
    #print('started receiver loop')
    while True:
        #print('waiting on receive')
        len = await sreader.readinto(buf)
        led(1)
        if udpserv.addr:
          print('UART->UDP:',buf[:len])
          udpserv.sock.sendto(buf[:len], udpserv.addr)
        led(0)

async def main():
    print("Connect RJ-11 4-pin or RJ-12 6-pin STRAIGHT cable")
    print("TX=",TX,"RX=",RX,"BAUD=",BAUD,"TIMEOUT_ms=",TIMEOUT_ms,"UART<->UDP bridge started")
    print('echo -ne ":e1\\r" | socat -t 60 - udp:192.168.48.32:11880')
    print(":e1\\r=0210A1\\r\\n")
    asyncio.create_task(udpserv.serve(udpcb, '0.0.0.0', port))
    # asyncio.create_task(sender())
    asyncio.create_task(receiver())
    
    while True:
        await asyncio.sleep(1)

def run():
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Interrupted')
    finally:
        asyncio.new_event_loop()
        #print('uartudp.run() to run again.')
run()
