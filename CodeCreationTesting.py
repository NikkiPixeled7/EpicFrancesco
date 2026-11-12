import ipaddress, socket
from datetime import datetime, timezone

hostname = socket.gethostname()
host_ip = socket.gethostbyname(hostname)

def daily_key():    
    today = datetime.now(timezone.utc).date()
    return today.toordinal()

print(daily_key())

def encode_ip(ip):
    ip_number = int(ipaddress.IPv4Address(ip))

    key = daily_key()

    encoded_number = ip_number ^ key

    return format(encoded_number, "08X")

def decode_ip(encoded_ip):
    
# still have to decode, then implement into the main code
