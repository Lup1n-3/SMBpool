import subprocess
import concurrent.futures
import os
import time
import ipaddress
from datetime import datetime
import multiprocessing

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

    # Entrada de datos (rango CIDR o IP única y opción de hilos)
    target = input("Ingrese el rango CIDR o una IP única (por ejemplo, 152.168.0.1 o 152.168.0.0/14): ")
    thread_option = input("Ingrese el nivel de uso de hilos ('low' para uso bajo, 'high' para uso alto): ").strip().lower()

    # Configurar la cantidad de hilos según la opción elegida
    cpu_count = multiprocessing.cpu_count()
    if thread_option == 'low':
        max_workers = max(1, cpu_count // 2)  # Usa la mitad de los núcleos disponibles
    elif thread_option == 'high':
        max_workers = cpu_count  # Usa todos los núcleos disponibles
    else:
        print("Opción de hilos no válida. Use 'low' o 'high'.")
        return

    # Limpiar pantalla antes de iniciar el escaneo
    os.system('clear')
    
    print(logo)

    # Mostrar mensaje de inicio del escaneo y contador de IPs escaneadas
    print("\nIniciando escaneo de IPs...")
    print("=====================================")
    print("IPs escaneadas: 0", end='', flush=True)

    try:
        found_ips = []
        scanned_ips_count = 0
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        output_file = f'scan_results_{timestamp}.txt'
        with open(output_file, 'w') as file:
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Escaneo de SMB utilizando smbclient en las IPs del rango especificado
                if '/' in target:
                    # Es un rango CIDR
                    ip_network = ipaddress.ip_network(target, strict=False)
                    ip_list = [str(ip) for ip in ip_network.hosts()]
                else:
                    # Es una IP única
                    ip_list = [target]

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

    except Exception as e:
        print(f"Error durante el escaneo: {e}")

if __name__ == "__main__":
    main()
