#!/bin/bash 

if [ -z $1 ]; then 
	echo -e "[-] Uso => ./escaneo.sh <IP objetivo> "
	exit 1
fi

echo -e "Bienvenido usuario $(whoami)"
echo -e  "Iniciamos con el Escaneo de Puertos"
echo -e "===================================="
echo -e "[.......Espere un momento......]"
echo -e "===================================="

for p in {1..65535}; do 

2>/dev/null echo > /dev/tcp/$1/$p

if [ $? -eq 0 ]; then 
	echo -e  "[+] Puerto Abierto => [$p]"
	
fi 
done  

echo "[+]-----Finalizado--------"