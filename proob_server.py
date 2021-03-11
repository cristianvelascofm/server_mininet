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

from mininet.topo import Topo
from mininet.cli import CLI
from mininet.net import Mininet
from mininet.node import OVSSwitch, RemoteController
import mininet.link
import mininet.log
import mininet.node


# Create a variable for the elements of topology
host_group = []
swithc_group = []
controller_group = []
link_group = []
port_group = []

host_container = []
switch_container = []
controller_container = []
link_container = []
link_array = []
link_dict = {}
port_container = []


host_added = []
switch_added = []
controller_added = []
link_added = []

#Variables para la generacion de trafico ITG

hots_receiver = None
host_sender = None

# Creacion de la red en Mininet
#net = Mininet(build=False)
net = Mininet()

def run_mininet():
    
    print('Creacion de la Red ...')


    for b in host_container:
        host_added.append(net.addHost(b))
    print('Hosts Creados ...')

    for d in switch_container:
        switch_added.append(net.addSwitch(d))
    print('Switchs Creados ...')
    for f in controller_container:
        # controller_added.append(net.addController(
        #    name=f, controller=RemoteController, ip='10.556.150', port=6633))
        controller_added.append(net.addController(f))
    print('Controladores Creados ...')
    for n in link_array:
        l = n['cn'].split(",")

    for n in link_array:
        l = n['cn'].split(",")
        for m in switch_added:
            if l[0] == m.name:
                for j in host_added:
                    if l[1] == j.name:
                        link_added.append(net.addLink(
                            m, j, intfName1=n['intfName1'], intfName2=n['intfName2']))

    print('Links Creados ...')
    net.build()
    net.start()
    print('RED INICIADA!! ...')
    net.pingAll()
    print('Hecho Ping')
    #net.stop()
    for h in host_added:
        h.stop()
    for s in switch_added:
        s.stop()
    for c in controller_added:
        c.stop()
    for l in link_added:
        l.stop()
    print('Terminado')


def wireshark_launcher():
    run_wireshark = subprocess.call(['wireshark-gtk', '-S'])

# Creacion del hilo para lanzar Wireshark
w = threading.Thread(target=wireshark_launcher,)

# Creacion de hilos para el generador de tráfico ITG


def interpreter(json_data, connection):
    
    answer_to_client = None 
    charge_array = {}
    traffic_array = {}
    dict_answer = {} #diccionario que se enviará como respuesta al Cliente
    if 'action' in json_data:

        act = json_data['action']
        if act == "stop":
            print("Terminando Emulacion ...")
            #CLI(net,script= "stop.sh")
            os.system('mn -c')
            #net.stop()
            ans = {}
            ans['emulacion'] = 'terminada'
            f = json.dumps(ans)
            connection.sendall(f.encode())
            ans = {}

        return True

    else:
        print('Creando el Arreglo de la Red ...')
        # Contiene el diccionario de la clave Items
        array_data = json_data['items']

        ipClient = json_data['IpClient']
        aux = ""
        for ip in ipClient:
            ip_sh = ip[0]
            aux = aux+ip
        # Establece en el Bash la direccion del cliente  en el DISPPLAY
        os.environ["DISPLAY"] = aux+':0.0'
        #w.start()
        for x in array_data:
            id = x['id'][0]
            if id == 'h':
                host_group.append(x)
            elif id == 's':
                swithc_group.append(x)
            elif id == 'c':
                controller_group.append(x)
            elif id == 'l':
                link_group.append(x)
            elif id == 'e':
                port_group.append(x)
            else:
                print("None")

        for x in host_group:
            host_container.append(x['id'])
        for y in swithc_group:
            switch_container.append(y['id'])
        for z in controller_group:
            controller_container.append(z['id'])
        for cn in link_group:
            link_container.append(cn['connection'])
            aux = {
                'cn': cn['connection'], 'intfName1': cn['intfName1'], 'intfName2': cn['intfName2']}
            link_array.append(aux)
        

        run_mininet()
        at = {}
        at['red:'] = 'creada'
        f = json.dumps(at)
        connection.sendall(f.encode())
        at = {}
        return True

