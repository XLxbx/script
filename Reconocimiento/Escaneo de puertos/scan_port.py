import sys
import socket 

target = socket.gethostbyname(input("Ingrese IP ==> | "))

print("[+] Escaneo en curso......" + target)

try: 
    for port in range(1,1000):
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socket.setdefaulttimeout(1)
            resultado = s.connect_ex((target, port))
            if resultado == 0: 
                print("[+] Port open => {} ".format(port))
            s.close
except: 
    print("[-] Sin resultado")
    sys.exit(0)