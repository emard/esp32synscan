# ESP32 UART UDP Bridge

Micropython asyncio UART to UDP bridge for ESP32.
Intended use: wireless interface for
SynScan Virtuoso 90 Heritage telescope mount
that should be more stable than original
SynScan WiFi dongle.

Install micropython (flash image)

Bring micropython online

Install asyncio

    import mip
    mip.install("asyncio")

Upload files "uartudp.py" and "dgram.py" to root ESP32,
use lftp

    lftp> mput uartudp.py dgram.py

In file "main.py" let it execute uartudp.py to start on boot