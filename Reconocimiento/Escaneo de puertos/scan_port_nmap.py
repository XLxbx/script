import nmap
from colorama import init, Fore
#python3 -m pip install python-nmap


def port_versiones(target):
    nm = nmap.PortScanner()
    resultado = nm.scan(target, arguments='-sV -T4 -F')

    for host in resultado['scan']:
        print(f"{Fore.YELLOW}[+] Resultados para {target}{Fore.RESET}")
        for puerto in resultado['scan'][host]['tcp']:
            if resultado['scan'][host]['tcp'][puerto]['state'] == 'open':
                servicio = resultado['scan'][host]['tcp'][puerto]['name']
                version = resultado['scan'][host]['tcp'][puerto]['version']
                print(f"[+] Puerto {puerto} ({servicio}): Versión {version}")

if __name__ == "__main__":
    target= input("Ingresa la dirección IP o el nombre del host: ").strip()
    port_versiones(target)
    
