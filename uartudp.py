# usage
# UDP: send "message"
# UART: type "reply" CTRL-J within 60 seconds after "message"
# echo "message" | socat -t 60 - udp:192.168.48.32:11880

# runs both UDP and UART in async mode

from dgram import UDPServer # https://github.com/perbu/dgram
import uasyncio as asyncio
from machine import UART,Pin
from micropython import const
import re

# The table below specifies the RX and TX pins
# for each of the three UART ports available in ESP32.
# UART   TX/RX     RX     TX     Note
# UART0      0     GPIO3  GPIO1
# UART1            GPIO9  GPIO10 requires reassignment of pins
# UART2      2     GPIO16 GPIO17

BAUD=const(9600)
TX=const(17)
RX=const(16)
TIMEOUT_ms=const(0)
buf = bytearray(256)
uart=UART(2,BAUD,tx=TX,rx=RX,timeout=TIMEOUT_ms)
swriter=asyncio.StreamWriter(uart, {})
sreader=asyncio.StreamReader(uart)

port=11880
udpserv=UDPServer()
led=Pin(2,Pin.OUT)

valid_uart2udp=re.compile("^[\r=0-9A-F]+$")
valid_udp2uart=re.compile("^[\r:!0-9a-zA-Z]+$")

# motor firmware 2.16.A1 and/or PCB have bug
# with primariy encoder on axis 2 
# on synscan pro app after each connect user
# should select Advanced -> Auxiliary Encoder
# rewriting encoder select command fixes this bug
# ":W2050000\r" -> ":W2040000\r"
# AT command should not reach firmware
# rewrite it as ":e1\r"
def udpcb(msg,adr):
    led(1)
    if msg==b":W2050000\r":
      swriter.write(b":W2040000\r")
      print("rewritten as :W2040000 (bugfix)")
    elif msg==b"AT+CWMODE_CUR?\r\n":
      swriter.write(b":e1\r")
      print("rewritten as :e1 (bugfix)")
    else:
      if re.search(valid_udp2uart,msg):
        swriter.write(msg)
    print('UDP->UART:',msg)
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

# uses only timeout to delimit UDP
# needs timeout 20 ms
async def receiver1():
    #print('started receiver loop')
    while True:
        #print('waiting on receive')
        len = await sreader.readinto(buf)
        led(1)
        if udpserv.addr:
          print('UART->UDP:',buf[:len])
          udpserv.sock.sendto(buf[:len], udpserv.addr)
        led(0)

# receive serial stream from "=" to "\r", send as UDP
# needs timeout 20 ms
async def receiver2():
    #print('started receiver loop')
    pos=0
    mv=memoryview(buf)
    while True:
        #print('waiting on receive')
        n=await sreader.readinto(mv[pos:])
        led(1)
        if pos+n<len(buf):
          pos+=n
        else:
          pos=0
        r1 = buf[:pos].find(b"=")
        if r1>=0:
          r2 = buf[r1+1:pos].find(b"\r")
          #print(buf[:pos],r1,r2)
          if r2>=0:
            if udpserv.addr:
              print('UART->UDP:',buf[r1:r1+2+r2])
              udpserv.sock.sendto(buf[r1:r1+2+r2], udpserv.addr)
            pos = 0
        led(0)

# receive serial stream from "=" to "\r", send as UDP
# tries to get rid of line junk
# line is half duplex
# sending while receiving results in junk received
# works with timeout 0
async def receiver3():
  #print('started receiver loop')
  line=b""
  while True:
    #print('waiting on receive')
    n=await sreader.readinto(buf)
    led(1)
    #print("UART read",n)
    b=buf[:n].splitlines(b"\r")
    for x in b:
      if line!=b"":
        line+=x
      else:
        r0=x.find(b"=")
        if r0>=0:
          line+=x[r0:]
      r1=line.find(b"=")
      r2=line[r1:].find(b"\r")
      if r2>r1:
        if udpserv.addr:
          udpserv.sock.sendto(line[r1:r2+1], udpserv.addr)
          print('UART->UDP:',line[r1:r2+1])
        else:
          print("no host")
        line=line[r2+1:]
      else:
        #print("junk",line)
        if not re.search(valid_uart2udp,line):
          line=b""
    led(0)

async def main():
    print("Connect RJ-11 4-pin or RJ-12 6-pin STRAIGHT cable")
    print("TX=",TX,"RX=",RX,"BAUD=",BAUD,"TIMEOUT_ms=",TIMEOUT_ms,"UART<->UDP bridge started")
    print('echo -ne ":e1\\r" | socat -t 1 - udp:192.168.48.32:11880')
    print(":e1\\r=0210A1\\r")
    asyncio.create_task(udpserv.serve(udpcb, '0.0.0.0', port))
    #asyncio.create_task(sender())
    #asyncio.create_task(receiver1())
    #asyncio.create_task(receiver2())
    asyncio.create_task(receiver3())
    
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
