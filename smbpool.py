import subprocess
import concurrent.futures
import os
import time
import ipaddress
from datetime import datetime

def check_installation(tool):
    """Verifica si una herramienta está instalada y la instala si no lo está."""
    try:
        subprocess.run([tool, '--version'], capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError:
        print(f"{tool} no está instalado. Instalando...")
        subprocess.run(['sudo', 'apt-get', 'install', '-y', tool])
        print(f"{tool} instalado.")

def check_smb(ip):
    try:
        result = subprocess.run(['smbclient', '-L', f'//{ip}', '-N'], capture_output=True, text=True, timeout=10)
        if "Sharename" in result.stdout:
            print(f"Recursos compartidos encontrados en {ip}")
            return ip
    except Exception as e:
        print(f"Error al ejecutar smbclient en {ip}: {e}")
    return None

def generate_filename():
    """Genera un nombre de archivo único basado en la fecha y hora actuales."""
    return f"scan_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

def get_ip_list_from_file(filename):
    """Obtiene una lista de IPs o rangos de IPs desde un archivo."""
    with open(filename, 'r') as file:
        ip_ranges = file.read().splitlines()
    return ip_ranges

def main():
    os.system('clear')  # Limpiar pantalla al iniciar
    logo = """
==========================================================
  _________   _____ __________                      .__   
 /   _____/  /     \\______   \______   ____   ____ |  |  
 \_____  \  /  \ /  \|    |  _/\____ \ /  _ \ /  _ \|  |  
 /        \/    Y    \    |   \|  |_> >  <_> |  <_> )  |__
/_______  /\____|__  /______  /|   __/ \____/ \____/|____/
        \/         \/       \/ |__|                       
===========================================================
                      SMBpool by Lup1n
===========================================================
"""

    # Verificar e instalar smbclient si es necesario
    check_installation('smbclient')

    print(logo)

    # Verificar conectividad de red
    try:
        subprocess.run(['ping', '-c', '1', '8.8.8.8'], capture_output=True, text=True, check=True)
        print("\nConectividad de red verificada.")
    except subprocess.CalledProcessError:
        print("\nNo hay conectividad de red. Verifique su conexión.")
        return

    # Entrada de datos (rango CIDR o IP única y cantidad de hilos)
    input_option = input("Ingrese '1' para ingresar IPs/rangos manualmente o '2' para cargar desde un archivo: ")

    if input_option == '1':
        target = input("Ingrese las IPs o rangos CIDR separados por comas (por ejemplo, 152.168.0.1,152.168.0.0/14): ")
        ip_ranges = target.split(',')
    elif input_option == '2':
        filename = input("Ingrese el nombre del archivo con las IPs o rangos CIDR: ")
        ip_ranges = get_ip_list_from_file(filename)
    else:
        print("Opción no válida.")
        return

    max_workers = int(input("Ingrese la cantidad de hilos a usar: "))

    # Limpiar pantalla antes de iniciar el escaneo
    os.system('clear')
    
    print(logo)

    # Mostrar mensaje de inicio del escaneo y contador de IPs escaneadas
    print("\nIniciando escaneo de IPs...")
    print("=====================================")
    print("IPs escaneadas: 0", end='', flush=True)

    # Generar un nombre de archivo único para este escaneo
    filename = generate_filename()

    try:
        found_ips = []
        scanned_ips_count = 0
        with open(filename, 'w') as file:
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                ip_list = []

                for ip_range in ip_ranges:
                    if '/' in ip_range:
                        # Es un rango CIDR
                        ip_network = ipaddress.ip_network(ip_range.strip(), strict=False)
                        ip_list.extend([str(ip) for ip in ip_network.hosts()])
                    else:
                        # Es una IP única
                        ip_list.append(ip_range.strip())

                num_ips = len(ip_list)
                count_found = 0

                futures = {executor.submit(check_smb, ip): ip for ip in ip_list}

                for future in concurrent.futures.as_completed(futures):
                    scanned_ips_count += 1
                    print(f"\rIPs escaneadas: {scanned_ips_count}", end='', flush=True)
                    result = future.result()
                    if result:
                        found_ips.append(result)
                        file.write(f'{result}\n')
                        count_found += 1
                        print(f"\nNúmero de IPs encontradas: {count_found}")

                # Limpiar la pantalla y mostrar la cantidad de IPs encontradas junto con el logo
                os.system('clear')
                print(logo)
                print(f"\nNúmero total de IPs encontradas con recursos compartidos: {count_found}")
                print(f"Resultados guardados en: {filename}")

    except Exception as e:
        print(f"Error durante el escaneo: {e}")

if __name__ == "__main__":
    main()
