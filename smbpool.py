import subprocess
import concurrent.futures
from scapy.all import *
import os
import ipaddress

def check_installation(tool):
    """Verifica si una herramienta está instalada y la instala si no lo está."""
    try:
        subprocess.run([tool, '--version'], capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError:
        print(f"{tool} no está instalado. Instalando...")
        subprocess.run(['sudo', 'apt-get', 'install', '-y', tool])
        print(f"{tool} instalado.")

def scan_ip(ip):
    try:
        print(f"Probando IP: {ip}")
        # Escanear el puerto SMB (445)
        syn_packet = IP(dst=ip)/TCP(dport=445, flags="S")
        response = sr1(syn_packet, timeout=1, verbose=0)
        if response and response.haslayer(TCP) and response.getlayer(TCP).flags == 0x12:
            # Si el puerto está abierto, ejecutar smbclient
            print(f"Conexión exitosa a {ip}:445")
            result = subprocess.run(['smbclient', '-L', f'//{ip}', '-N'], capture_output=True, text=True)
            if "Sharename" in result.stdout:
                print(f"Recursos compartidos encontrados en {ip}")
                return ip
    except Exception as e:
        pass
    return None

def main():
    os.system('clear')
    print("========= SMB Scanner =========")

    # Verificar e instalar smbclient si es necesario
    check_installation('smbclient')

    # Verificar conectividad de red
    try:
        subprocess.run(['ping', '-c', '1', '8.8.8.8'], capture_output=True, text=True, check=True)
        print("Conectividad de red verificada.")
    except subprocess.CalledProcessError:
        print("No hay conectividad de red. Verifique su conexión.")
        return

    cidr_range = input("Ingrese el rango CIDR (por ejemplo, 152.168.0.0/14): ")
    max_workers = int(input("Ingrese la cantidad de hilos a usar: "))

    try:
        ip_network = ipaddress.ip_network(cidr_range)
    except ValueError as e:
        print(f"Error en el rango CIDR: {e}")
        return

    ip_range = [str(ip) for ip in ip_network]

    print(f"Iniciando escaneo de IPs en el rango {cidr_range}...")
    found_ips = []

    with open('list.txt', 'w') as file:
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            results = executor.map(scan_ip, ip_range)
            for ip in results:
                if ip:
                    found_ips.append(ip)
                    file.write(f'{ip}:445\n')

    print("Escaneo completado. IPs encontradas:")
    for ip in found_ips:
        print(ip)

if __name__ == "__main__":
    conf.verb = 0  # Silenciar advertencias de Scapy
    main()
