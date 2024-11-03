# ESP32 UART UDP Bridge

Micropython asyncio UART to UDP bridge for ESP32.
Intended use: wireless interface for
SynScan Virtuoso 90 Heritage telescope mount
that should be more stable than original
SynScan WiFi dongle.

# Principle of operation

When ESP32 receives UDP packet at port 11880
it sends it via UART 9600,8,n,1

When data are received at UART and 20 ms
of idle UART passes, send data over UDP
back to host IP from which recent UDP
was receiver.

# Electrical

There is 12->3.3V converter onboard.
RJ-12 plug can't guarantee that GND makes
connection before other pins.
There should be 3.6V zener diodes to protect
sensitive 3.3V data pins from getting 12V
during plugging in.

In the mount manual see RJ12 pinout.
Conenct RJ12 RX/TX with short straight
RJ12 cable to ESP32 RX2/TX2 pins.

# Test connection

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

# Firmware bugfix

Motor firmware version 2.16.A1 is the latest but has
problem with SynScan application on android.
After each connect user must enable "Auxiliary Encoder"
otherwise mount will start turning around azimuth axis
and will never stop by itself (user should press cancel to stop).

To fix this in function "udpcb" one message is rewritten

    :W2050000\r -> :W2040000\r

Synscan sends some AT command probably for ESP AT
firmware which should not reach motor firmware so
"udpcb" rewrites this AT command as ":e1\\r"
this command returns motor firmware version

    AT+CWMODE_CUR?\r\n -> :e1\r
