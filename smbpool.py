import subprocess
import concurrent.futures
import os
import time

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

    # Entrada de datos (rango CIDR o IP única y cantidad de hilos)
    target = input("Ingrese el rango CIDR o una IP única (por ejemplo, 152.168.0.1 o 152.168.0.0/14): ")
    max_workers = int(input("Ingrese la cantidad de hilos a usar: "))

    # Limpiar pantalla antes de iniciar el escaneo
    os.system('clear')
    
    print(logo)

    # Animación para "Iniciando escaneo de IPs ..." justo antes de comenzar el escaneo
    print("\nIniciando escaneo de IPs...")
    print("=====================================")

    try:
        found_ips = []
        with open('list.txt', 'w') as file:
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Escaneo de SMB utilizando smbclient en las IPs del rango especificado
                if '/' in target:
                    # Es un rango CIDR
                    ip_range = subprocess.run(['nmap', '-p', '445', '--open', '--script', 'smb-os-discovery', '-oG', '-', target], capture_output=True, text=True, timeout=300)
                    if not ip_range:
                        print("No se encontraron IPs con el puerto SMB (445) abierto.")
                        return
                    ip_list = [line.split()[1] for line in ip_range.stdout.splitlines() if "/open/" in line]
                else:
                    # Es una IP única
                    ip_list = [target]

                num_ips = len(ip_list)
                count_found = 0

                for ip in ip_list:
                    time.sleep(0.5)  # Simular un proceso de verificación

                    print(f"Probando IP: {ip}")
                    result = check_smb(ip)
                    if result:
                        found_ips.append(result)
                        file.write(f'{result}\n')
                        count_found += 1
                        print(f"Número de IPs encontradas: {count_found}")

                # Limpiar la pantalla y mostrar la cantidad de IPs encontradas junto con el logo
                os.system('clear')
                print(logo)
                print(f"\nNúmero total de IPs encontradas con recursos compartidos: {count_found}")

    except Exception as e:
        print(f"Error durante el escaneo: {e}")

if __name__ == "__main__":
    main()
