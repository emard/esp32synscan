# ESP32 UART UDP Bridge

Micropython asyncio UART to UDP bridge for ESP32.
Intended use: wireless interface for
SynScan Virtuoso 90 Heritage telescope mount
that should be more stable than original
SynScan WiFi dongle.

# Synscan Parameters

Create access point on android or wifi router to which ESP32 will
connect as client, default is:

    ssid: syn scan
    pass: syn scan

Tested with synscan 2.5.2

    Settings -> Connect Settings ->

    Resend Tries:        0
    Read Timeout (ms): 300 

# Principle of operation

ESP32 listens to UDP packets at port 11880.
Each packet received is checked with regex.
If it seems valid then ESP32 sends it via
UART. Uart parameters are 9600,8,n,1.

When data are received at UART ESP32 checks
validity and if valid then ESP32 sends data
over UDP back to host IP from which recent UDP
was received.

# Firmware bugfix

Motor firmware version 2.16.A1 is the latest but has
problem with SynScan application on android.
After each connect user must enable "Auxiliary Encoder"
otherwise mount will start turning around azimuth axis
and will never stop by itself (user should press cancel to stop).

To fix this in function "udpcb()" one message is rewritten

    :W2050000\r -> :W2040000\r

Second fix is more to prevent sending junk to
motor firmware which is easy to crash.

Synscan sends some AT command probably for its
original SynScan WiFi ESP8266 AT firmware.
This AT command should not reach motor firmware so
"udpcb()" function rewrites this AT command as ":e1\\r"
and to this command motor firmware responds with
version number which is not really response to AT
command but synscan accepts it.

    AT+CWMODE_CUR?\r\n -> :e1\r

# Electrical

There is 12->3.3V switching converter onboard (Canton Power).
RJ-12 plug can't guarantee that GND makes
connection before other pins.
There should be 3.6V zener diodes to protect
sensitive 3.3V data pins from getting 12V
during plugging in.

In the mount manual see RJ12 pinout.
Conenct RJ12 RX/TX with short straight
RJ12 cable to ESP32 RX2/TX2 pins.

# Connection

Looking at female RJ-12 socket on the mount:

       ____
    ---    ---
    | 654321 |
    ----------

    1 blue   N.C.
    2 yellow TX       (3.3V) (mount receives)
    3 green  Vpp+     ( 12V)
    4 red    RX       (3.3V) (mount sends)
    5 black  GND
    6 white  Reserved (3.3V)

RX/TX roles on the mount are swapped and
actually indicate RX/TX on remote end

# WARNING WARNING WARNING

There are different RJ-11 and RJ-12 cables,
with [straight and cross wiring](/doc/straight-vs-cross-cable.pdf).
For the telephones it does not matter but here it matters!

STANDARD PHONE CROSS CABLE MAY NOT BE SUITABLE.
USE ONLY STRAIGHT WIRED 4-PIN RJ-11 or
STRAIGHT WIRED 6-PIN RJ-12. CROSS RJ-11 AND RJ-12 
CABLES AND ALL 2-PIN RJ-11 CABLES ARE NOT SUITABLE.
IF A CROSS WIRED CABLE OR ANY 2-PIN CABLE IS CONNECTED
THEN 12V WILL FRY ELECTRONICS IN THE MOUNT AND ESP32.

# Test serial connection

https://stargazerslounge.com/topic/239925-skywatcher-heritage-virtuoso-controlled-via-bluetooth/page/6/
Another way to test is to connect to the mount using a terminal program
9600,8,n,1 and type:

:e1

Typing these three characters plus a ENTER or CTRL-M "\r" should
echo typed ":e1\r" and produce the response "=0210A\r" from the mount.

=0210A

The working serial cable connects using these parameters:
Baud rate 9600
Data bits=8, Stop bits=1, Parity=None
Set chars: Eof=0x00, Error=0x00, Break=0x00, Event=0x00, Xon=0x11, Xoff=0x13
Handflow: ControlHandShake=(), FlowReplace=(XOFF_CONTINUE), XonLimit=2048, XoffLimit=512 

# Install

Install micropython 1.24 (flash image with esptool.py)

Bring micropython online to internet.

Install asyncio

    import mip
    mip.install("asyncio")

Upload files "uartudp.py" and "dgram.py" to root ESP32,
use lftp

    lftp> mput uartudp.py dgram.py

In file "main.py" let it execute uartudp.py to start on boot.

    import mip
    mip.install("esp32ecp5")

from "emard/esp32ecp5" "uftpd.py" and "ecp5setup.py" are useful
to config wifi and uploads via ftp.

In "ecp5setup.py" add last line generated for generated "main.py"
to autostart "uartudp"

    import uartudp

from "https://github.com/perbu/dgram" project I slightly modified
"dgram.py" for the UDP server to expose "addr" so serial receiver
can "know" to whom it should send data received from uart.

