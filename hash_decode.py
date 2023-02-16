#!/usr/bin/python3

import hashlib

opciones = input(str("[1] $1$-MD5\n[2] SHA-1\n[3] SHA-224\n[4] $6$-SHA-512\n[5] $5$-SHA-256\n=>  "))
password = input("Ingrese Hash => ")
diccionario = input("Seleccione un diccionario => ")

try: 
    file_pass = open(diccionario, 'r')
except:
    print("Error: " + diccionario + "no encontrado")

if opciones == "1": 
    for md5 in file_pass: 
        codificar_md5 = md5.encode('utf-8')
        desco_md5 = hashlib.md5(codificar_md5.strip())
        resultado_md5 = desco_md5.hexdigest()

        if resultado_md5 == password:
            print("[+] MD5 => " + md5)
    if not md5:
        print("[-]Sin resultado")
       
if opciones == "2":
    for sha1 in file_pass: 
        codificar_sha1 = sha1.encode('utf-8')
        desco_sha1 = hashlib.sha1(codificar_sha1.strip())
        resultado_sha1 = desco_sha1.hexdigest()

        if resultado_sha1 == password:
            print("[+] SHA1 => " + sha1)
    if not sha1:
        print("[-]Sin resultado")

if opciones == "3":
    for sha224 in file_pass: 
        codificar_sha224 = sha224.encode('utf-8')
        desco_sha224 = hashlib.sha224(codificar_sha224.strip())
        resultado_sha224 = desco_sha224.hexdigest()

        if resultado_sha1 == password:
            print("[+] SHA224 => " + sha224)
    if not sha1:
        print("[-]Sin resultado")

if opciones == "4":
    for sha512 in file_pass: 
        codificar_sha512 = sha512.encode('utf-8')
        desco_sha512 = hashlib.sha512(codificar_sha512.strip())
        resultado_sha512 = desco_sha512.hexdigest()

        if resultado_sha512 == password:
            print("[+] SHA512 => " + sha512)
    if not sha1:
        print("[-]Sin resultado")

if opciones == "5":
    for sha256 in file_pass: 
        codificar_sha256 = sha256.encode('utf-8')
        desco_sha256 = hashlib.sha256(codificar_sha256.strip())
        resultado_sha256 = desco_sha256.hexdigest()

        if resultado_sha256 == password:
            print("[+] SHA256 => " + sha256)
    if not sha1:
        print("[-]Sin resultado")
 