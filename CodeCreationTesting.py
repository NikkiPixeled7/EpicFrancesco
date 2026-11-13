import ipaddress, socket
from datetime import datetime, timezone

hostname = socket.gethostname()
host_ip = socket.gethostbyname(hostname)

def daily_key():    
    today = datetime.now(timezone.utc).date()
    return today.toordinal()

def encode_ip(ip):
    ip_number = int(ipaddress.IPv4Address(ip))

    key = daily_key()

    encoded_number = ip_number ^ key

    return format(encoded_number, "08X")

def decode_ip(code):

    encoded_number = int(code, 16)

    key = daily_key()

    ip_number = encoded_number ^ key

    return str(ipaddress.IPv4Address(ip_number))

# print(host_ip)

# encoded_ip = encode_ip(host_ip)

# print(encoded_ip)

# decoded_ip = decode_ip(encoded_ip)

# print(decoded_ip)
