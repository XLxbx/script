$host_local = "localhost"
$port_inicial = 1041
$port_final = 1044
$i = 0

for ($port = $port_inicial; $port -le $port_final; $port++) {
    $conexion = Test-NetConnection -ComputerName $host_local -Port $port
    
    if ($conexion.TcpTestSucceeded) {
        echo "Puerto $port abierto"
        $i++
    }
}

echo "Total de puertos abiertos: $i"