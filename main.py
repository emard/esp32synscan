import network
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect("user", "pass")
import uftpd
import uartudp
