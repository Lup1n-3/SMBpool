
# SMBpool

SMBpool es una herramienta en Python diseñada para escanear redes en busca de servidores SMB con recursos compartidos accesibles. Utiliza smbclient para verificar la existencia de recursos compartidos en las direcciones IP especificadas.


## Requisitos

Antes de ejecutar SMBpool, asegúrate de tener instalado smbclient. Si no está instalado, el script intentará instalarlo automáticamente utilizando apt-get.

## Uso
Ejecución del Script:
```bash
python3 smbpool.py
```

Al iniciar, el script solicitará al usuario ingresar un rango CIDR o una IP única y la cantidad de hilos para el escaneo.

Escaneo:

El script ejecutará un escaneo utilizando smbclient para cada IP en el rango especificado.
Durante el escaneo, se mostrará el progreso y las IPs encontradas con recursos compartidos.
Resultados:

Al finalizar generara en la misma carpeta que el .py un txt con todas las IPs a las que puede ingresar usando:

```bash
smbclient -L //IP -N
```





