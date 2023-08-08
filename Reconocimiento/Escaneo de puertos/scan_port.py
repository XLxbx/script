import sys
import socket

def scan_ports(target):
    try:
        print("[+] Scanning in progress for " + target)
        for port in range(20, 6000):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex((target, port))
                if result == 0:
                    print("[+] Port open => {} ".format(port))
    except KeyboardInterrupt:
        print("\n[+] Scan interrupted by the user.")
        sys.exit(0)
    except socket.gaierror:
        print("[-] Invalid hostname or address.")
        sys.exit(1)
    except socket.error:
        print("[-] Could not connect to the target.")
        sys.exit(1)

if __name__ == "__main__":
    target = input("Enter IP or hostname: ").strip()
    scan_ports(target)
