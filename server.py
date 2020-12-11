# -*-coding:utf-8-*-
#!/usr/bin/python

import socket
import sys
import os
import json
import subprocess
import time
import threading
from threading import Timer

from interpreterMininet import interpreter

# Creacion dinamica de variables
g = globals()

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Creador de elementos en mininet
# Bind the socket to the port
#server_address = ('10.55.6.146', 10000)
server_adress = ('192.168.56.104', 10000)
print('Iniciando Servidor: {} en el puerto: {}'.format(*server_adress))
sock.bind(server_adress)

# Listen for incoming connections
sock.listen(1)

while True:
    # Wait for a connection
    print('Esperando Conexcion Entrante ...')
    connection, client_address = sock.accept()
    print('Conexion desde: ', client_address)

    try:

        # Receive the data in small chunks and retransmit it
        while True:
            print("Esperando Order ...")
            data = connection.recv(8192)

            if not data:
                print('Sin datos ...')
                break
            else:
                # ***-******-*****-*****-******-*****-*****-****-****-***-****
                # Esta seccion decodifica y filtra los elementos en su grupo correspondiente
                # ***-******-*****-*****-******-*****-*****-****-****-***-****
                decode_data = data.decode()
                dict_data = eval(decode_data)
                json_data = json.loads(dict_data)
                print('++++++++++++++++++++++++++')
                print("MENSAJE ENTRANTE:", json_data)
                print('---------------------------')
                aux = interpreter(json_data, connection)
                if not aux:
                    break

    except:
        pass
    finally:

        # Clean up the connection
        print('Cerrando el Socket ...')
        connection.close()
