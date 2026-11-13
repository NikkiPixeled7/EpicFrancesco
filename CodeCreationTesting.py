import ipaddress, socket
from datetime import datetime, timezone

hostname = socket.gethostname()
host_ip = socket.gethostbyname(hostname)

def daily_key():    
    today = datetime.now(timezone.utc).date()
    return today.toordinal()

def encode_ip(ip):
    ip_number = int(ipaddress.IPv4Address(ip))

    D = daily_key()
    key = (D * 8) ^ D ^ D

    if key % 7 == 0:
        encoded_number = ip_number ^ (key * 7)
    elif key % 5 == 0:
        encoded_number = ip_number ^ (key * 5)
    elif key % 3 == 0:
        encoded_number = ip_number ^ (key * 3)
    elif key % 2 == 0:
        encoded_number = ip_number ^ (key * 2)
    else:
        encoded_number = ip_number ^ key

    return format(encoded_number, "08X")

def decode_ip(code):

    encoded_number = int(code, 16)

    D = daily_key()
    key = (D * 8) ^ D ^ D

    if key % 7 == 0:
            ip_number = encoded_number ^ (key * 7)
    elif key % 5 == 0:
        ip_number = encoded_number ^ (key * 5)
    elif key % 3 == 0:
        ip_number = encoded_number ^ (key * 3)
    elif key % 2 == 0:
        ip_number = encoded_number ^ (key * 2)
    else:
        ip_number = encoded_number ^ key

    return str(ipaddress.IPv4Address(ip_number))

print(host_ip)

encoded_ip = encode_ip(host_ip)

print(encoded_ip)

decoded_ip = decode_ip(encoded_ip)

print(decoded_ip)
