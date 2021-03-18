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

#Variables para la generacion de trafico ITG

hots_receiver = None
host_sender = None

# Creacion de la red en Mininet
net = Mininet(build=False)

def traffic_udp_simple():
    file = open("udp.sh", "w")
    file.write("iperfudp"+'\n')
    file.close()


def traffic_tcp_total():
    aux = ""
    for x in host_container:
        for y in host_container:
            if str(x) == str(y):
                pass
            else:
                aux = aux + "iperf "+str(x) + " " + str(y) + "\n"
    file = open("tcp.sh", "w")
    file.write(aux)
    file.close()


def traffic_udp_total():
    aux = ""
    for x in host_container:
        for y in host_container:
            if str(x) == str(y):
                pass
            else:
                aux = aux + "iperfudp "+ "1024 "+str(x) + " " + str(y) + "\n"
    file = open("udp.sh", "w")
    file.write(aux)
    file.close()


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
                        net.addLink(
                            m, j, intfName1=n['intfName1'], intfName2=n['intfName2'])

    print('Links Creados ...')
    net.start()
    print('RED INICIADA!! ...')


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
            net.stop()
            ans = {}
            ans['emulacion'] = 'terminada'
            f = json.dumps(ans)
            connection.sendall(f.encode())
            ans = {}

        return False

    elif 'wireshark' in json_data:
        print("Iniciando Wireshark ...")
        w.start()
        ans = {}
        ans['wireshark'] = 'lanzado'
        f = json.dumps(ans)
        connection.sendall(f.encode())
        ans = {}
        return True

    elif 'TCP' in json_data:
        #Tipos de Distribucion del Tráfico
        if('global' in json_data):

            print('TCP Global ...')
            host_size= (len(host_added))-1
            port_list =[]
            initial_port = 5000

            #Datos del modo de transmision
            #Solo una de estas tres opciones
            time_e = str(5)
            number = '0k'
            block = '0k'

            interval = str(1)
            window = '500k'
            length = '1m'
            bw = '1k'
            

            name_files = []
            dict_data_traffic = {}

            file_traffic= []
            data_traffic={}
            procces_data={}
            data_gen= {}

            #Lista de Puertos
            for pt in range(host_size):
                initial_port = initial_port + 1
                port_list.append(str(initial_port))


            aux_array = []
            #Se colocan los host como servidor en el puerto indicado
            for host_server in host_added:
                for port in port_list:
                    host_server.cmd('iperf3 -s -D -p '+str(port)+' -J>'+str(host_server)+'_'+str(port)+'.json')
                    time.sleep(3)
                    aux = [host_server, port]
                    aux_array.append(aux)

            buffer_server = []
            for server in aux_array:
                for host_client in host_added:
                    if not (str(host_client)+'_'+str(server[0])) in buffer_server:
                        if not str(server) in buffer_server:
                            if str(server[0]) == str(host_client):
                                pass
                            else:
                                #Posibles casos de parametrizacion del Trafico en Iperf3.1
                                #Solo el parámetro de Tiempo 
                                if('t' in json_data and (not 'i' in json_data) and (not 'l' in json_data) and (not 'b' in json_data) and (not 'w' in json_data)):
                                    time_e = str(json_data['t'])
                                    host_client.cmd('iperf3 -c '+str(server[0].IP())+' -p '+str(server[1])+' -t '+time_e+' -J>'+str(host_client)+'_'+str(server[0])+'.json'+' &')
                                    temp = str(host_client)+'_'+str(server[0])
                                    ax = str(server)
                                    buffer_server.append(temp)
                                    buffer_server.append(ax)
                                    name_files.append(str(host_client)+'_'+str(server[0]))
                                #Solo el parámetro de Tiempo con Intervalo 
                                elif('t' in json_data and ('i' in json_data) and (not 'l' in json_data) and (not 'b' in json_data) and (not 'w' in json_data)):
                                    time_e = str(json_data['t'])
                                    interval = str(json_data['i'])
                                    host_client.cmd('iperf3 -c '+str(server[0].IP())+' -p '+str(server[1])+' -t '+time_e+' -i '+interval+' -J>'+str(host_client)+'_'+str(server[0])+'.json'+' &')
                                    temp = str(host_client)+'_'+str(server[0])
                                    ax = str(server)
                                    buffer_server.append(temp)
                                    buffer_server.append(ax)
                                    name_files.append(str(host_client)+'_'+str(server[0]))
                                #Solo el parametro de Tiempo con Longitud 
                                elif('t' in json_data and (not 'i' in json_data) and ('l' in json_data) and (not 'b' in json_data) and (not 'w' in json_data)):
                                    time_e = str(json_data['t'])
                                    length = str(json_data['i'])
                                    host_client.cmd('iperf3 -c '+str(server[0].IP())+' -p '+str(server[1])+' -t '+time_e+' -l '+length+' -J>'+str(host_client)+'_'+str(server[0])+'.json'+' &')
                                    temp = str(host_client)+'_'+str(server[0])
                                    ax = str(server)
                                    buffer_server.append(temp)
                                    buffer_server.append(ax)
                                    name_files.append(str(host_client)+'_'+str(server[0]))
                                #Solo el parametro de Tiempo con Ancho de Banda
                                elif('t' in json_data and (not 'i' in json_data) and (not 'l' in json_data) and ('b' in json_data) and (not 'w' in json_data)):
                                    time_e = str(json_data['t'])
                                    bw = str(json_data['b'])
                                    host_client.cmd('iperf3 -c '+str(server[0].IP())+' -p '+str(server[1])+' -t '+time_e+' -b '+bw+' -J>'+str(host_client)+'_'+str(server[0])+'.json'+' &')
                                    temp = str(host_client)+'_'+str(server[0])
                                    ax = str(server)
                                    buffer_server.append(temp)
                                    buffer_server.append(ax)
                                    name_files.append(str(host_client)+'_'+str(server[0]))
                                    pass
                                #Solo el parametro de Tiempo con Ventana
                                elif('t' in json_data and (not 'i' in json_data) and (not 'l' in json_data) and (not 'b' in json_data) and ('w' in json_data)):
                                    time_e = str(json_data['t'])
                                    window = str(json_data['w'])
                                    host_client.cmd('iperf3 -c '+str(server[0].IP())+' -p '+str(server[1])+' -t '+time_e+' -w '+window+' -J>'+str(host_client)+'_'+str(server[0])+'.json'+' &')
                                    temp = str(host_client)+'_'+str(server[0])
                                    ax = str(server)
                                    buffer_server.append(temp)
                                    buffer_server.append(ax)
                                    name_files.append(str(host_client)+'_'+str(server[0]))
                                #Solo el parametro de Tiempo con Intervalo y Longitud
                                elif('t' in json_data and ('i' in json_data) and ( 'l' in json_data) and (not 'b' in json_data) and (not 'w' in json_data)):
                                    time_e = str(json_data['t'])
                                    interval = str(json_data['i'])
                                    length =  str(json_data['l'])
                                    host_client.cmd('iperf3 -c '+str(server[0].IP())+' -p '+str(server[1])+' -t '+time_e+' -i '+interval+' -l '+length+' -J>'+str(host_client)+'_'+str(server[0])+'.json'+' &')
                                    temp = str(host_client)+'_'+str(server[0])
                                    ax = str(server)
                                    buffer_server.append(temp)
                                    buffer_server.append(ax)
                                    name_files.append(str(host_client)+'_'+str(server[0]))
                                #Solo el parametro de Tiempo con Intervalo y Ancho de Banda
                                elif('t' in json_data and ('i' in json_data) and ( not 'l' in json_data) and ('b' in json_data) and (not 'w' in json_data)):
                                    time_e = str(json_data['t'])
                                    interval = str(json_data['i'])
                                    bw =  str(json_data['b'])
                                    host_client.cmd('iperf3 -c '+str(server[0].IP())+' -p '+str(server[1])+' -t '+time_e+' -i '+interval+' -b '+bw+' -J>'+str(host_client)+'_'+str(server[0])+'.json'+' &')
                                    temp = str(host_client)+'_'+str(server[0])
                                    ax = str(server)
                                    buffer_server.append(temp)
                                    buffer_server.append(ax)
                                    name_files.append(str(host_client)+'_'+str(server[0]))
                                #Solo el parametro de Tiempo con Longitud y Ventana
                                elif('t' in json_data and (not 'i' in json_data) and ('l' in json_data) and (not 'b' in json_data) and ('w' in json_data)):
                                    time_e = str(json_data['t'])
                                    length = str(json_data['l'])
                                    window =  str(json_data['w'])
                                    host_client.cmd('iperf3 -c '+str(server[0].IP())+' -p '+str(server[1])+' -t '+time_e+' -l '+length+' -w '+window+' -J>'+str(host_client)+'_'+str(server[0])+'.json'+' &')
                                    temp = str(host_client)+'_'+str(server[0])
                                    ax = str(server)
                                    buffer_server.append(temp)
                                    buffer_server.append(ax)
                                    name_files.append(str(host_client)+'_'+str(server[0]))
                                #Solo el parametro de Tiempo con  Ancho de Banda y Ventana
                                elif('t' in json_data and (not 'i' in json_data) and (not 'l' in json_data) and ('b' in json_data) and (not 'w' in json_data)):
                                    time_e = str(json_data['t'])
                                    window = str(json_data['w'])
                                    bw =  str(json_data['b'])
                                    host_client.cmd('iperf3 -c '+str(server[0].IP())+' -p '+str(server[1])+' -t '+time_e+' -w '+window+' -b '+bw+' -J>'+str(host_client)+'_'+str(server[0])+'.json'+' &')
                                    temp = str(host_client)+'_'+str(server[0])
                                    ax = str(server)
                                    buffer_server.append(temp)
                                    buffer_server.append(ax)
                                    name_files.append(str(host_client)+'_'+str(server[0]))

                                #Solo el parametro de Tiempo con Intervalo y Ventana 
                                elif('t' in json_data and ('i' in json_data) and ( not 'l' in json_data) and (not 'b' in json_data) and ('w' in json_data)):
                                    time_e = str(json_data['t'])
                                    interval = str(json_data['i'])
                                    window =  str(json_data['w'])
                                    host_client.cmd('iperf3 -c '+str(server[0].IP())+' -p '+str(server[1])+' -t '+time_e+' -i '+interval+' -w '+window+' -J>'+str(host_client)+'_'+str(server[0])+'.json'+' &')
                                    temp = str(host_client)+'_'+str(server[0])
                                    ax = str(server)
                                    buffer_server.append(temp)
                                    buffer_server.append(ax)
                                    name_files.append(str(host_client)+'_'+str(server[0]))

                                #Solo el parametro de Tiempo con Intervalo Longitud  Ancho de Banda
                                elif('t' in json_data and ('i' in json_data) and ( 'l' in json_data) and ('b' in json_data) and (not 'w' in json_data)):
                                    time_e = str(json_data['t'])
                                    interval = str(json_data['i'])
                                    length =  str(json_data['l'])
                                    bw = str(json_data['b'])
                                    host_client.cmd('iperf3 -c '+str(server[0].IP())+' -p '+str(server[1])+' -t '+time_e+' -i '+interval+' -l '+length+' -b '+bw+' -J>'+str(host_client)+'_'+str(server[0])+'.json'+' &')
                                    temp = str(host_client)+'_'+str(server[0])
                                    ax = str(server)
                                    buffer_server.append(temp)
                                    buffer_server.append(ax)
                                    name_files.append(str(host_client)+'_'+str(server[0]))
                                #Solo el parametro de Tiempo con Intervalo Longitud  Ventana
                                elif('t' in json_data and ('i' in json_data) and ( 'l' in json_data) and (not 'b' in json_data) and ('w' in json_data)):
                                    time_e = str(json_data['t'])
                                    interval = str(json_data['i'])
                                    length =  str(json_data['l'])
                                    window = str(json_data['w'])
                                    host_client.cmd('iperf3 -c '+str(server[0].IP())+' -p '+str(server[1])+' -t '+time_e+' -i '+interval+' -l '+length+' -w '+window+' -J>'+str(host_client)+'_'+str(server[0])+'.json'+' &')
                                    temp = str(host_client)+'_'+str(server[0])
                                    ax = str(server)
                                    buffer_server.append(temp)
                                    buffer_server.append(ax)
                                    name_files.append(str(host_client)+'_'+str(server[0]))
                                #Solo el parametro de Tiempo con Ancho de Banda Longitud  Ventana
                                elif('t' in json_data and (not 'i' in json_data) and ( 'l' in json_data) and ('b' in json_data) and ('w' in json_data)):
                                    time_e = str(json_data['t'])
                                    bw = str(json_data['b'])
                                    length =  str(json_data['l'])
                                    window = str(json_data['w'])
                                    host_client.cmd('iperf3 -c '+str(server[0].IP())+' -p '+str(server[1])+' -t '+time_e+' -b '+bw+' -l '+length+' -w '+window+' -J>'+str(host_client)+'_'+str(server[0])+'.json'+' &')
                                    temp = str(host_client)+'_'+str(server[0])
                                    ax = str(server)
                                    buffer_server.append(temp)
                                    buffer_server.append(ax)
                                    name_files.append(str(host_client)+'_'+str(server[0]))
                                #Solo el parametro de Tiempo con Intervalo Longitud  Ancho de Banda Ventana
                                elif('t' in json_data and ('i' in json_data) and ( 'l' in json_data) and ('b' in json_data) and ('w' in json_data)):
                                    time_e = str(json_data['t'])
                                    interval = str(json_data['i'])
                                    length =  str(json_data['l'])
                                    bw = str(json_data['b'])
                                    window = str(json_data['w'])
                                    host_client.cmd('iperf3 -c '+str(server[0].IP())+' -p '+str(server[1])+' -t '+time_e+' -i '+interval+' -l '+length+' -b '+bw+' -w '+window+' -J>'+str(host_client)+'_'+str(server[0])+'.json'+' &')
                                    temp = str(host_client)+'_'+str(server[0])
                                    ax = str(server)
                                    buffer_server.append(temp)
                                    buffer_server.append(ax)
                                    name_files.append(str(host_client)+'_'+str(server[0]))

                                #Solo el parámetro de Intervalo
                                elif(not 't' in json_data and ('i' in json_data) and (not 'l' in json_data) and (not 'b' in json_data) and (not 'w' in json_data)):
                                    interval = str(json_data['i'])
                                    host_client.cmd('iperf3 -c '+str(server[0].IP())+' -p '+str(server[1])+' -i '+interval+' -J>'+str(host_client)+'_'+str(server[0])+'.json'+' &')
                                    temp = str(host_client)+'_'+str(server[0])
                                    ax = str(server)
                                    buffer_server.append(temp)
                                    buffer_server.append(ax)
                                    name_files.append(str(host_client)+'_'+str(server[0]))

                                #Solo el parámetro de Intervalo y Longitud
                                elif(not 't' in json_data and ('i' in json_data) and ('l' in json_data) and (not 'b' in json_data) and (not 'w' in json_data)):
                                    interval = str(json_data['i'])
                                    length = str(json_data['l'])
                                    host_client.cmd('iperf3 -c '+str(server[0].IP())+' -p '+str(server[1])+' -i '+interval+' -l ' +length+' -J>'+str(host_client)+'_'+str(server[0])+'.json'+' &')
                                    temp = str(host_client)+'_'+str(server[0])
                                    ax = str(server)
                                    buffer_server.append(temp)
                                    buffer_server.append(ax)
                                    name_files.append(str(host_client)+'_'+str(server[0]))

                                #Solo el parámetro de Intervalo y Anchode Banda
                                elif(not 't' in json_data and ('i' in json_data) and (not 'l' in json_data) and ('b' in json_data) and (not 'w' in json_data)):
                                    interval = str(json_data['i'])
                                    bw = str(json_data['b'])
                                    host_client.cmd('iperf3 -c '+str(server[0].IP())+' -p '+str(server[1])+' -i '+interval+' -b '+bw+' -J>'+str(host_client)+'_'+str(server[0])+'.json'+' &')
                                    temp = str(host_client)+'_'+str(server[0])
                                    ax = str(server)
                                    buffer_server.append(temp)
                                    buffer_server.append(ax)
                                    name_files.append(str(host_client)+'_'+str(server[0]))

                                #Solo el parámetro de Intervalo y Ventana
                                elif(not 't' in json_data and ('i' in json_data) and (not 'l' in json_data) and (not 'b' in json_data) and ('w' in json_data)):
                                    interval = str(json_data['i'])
                                    window = str(json_data['w'])
                                    host_client.cmd('iperf3 -c '+str(server[0].IP())+' -p '+str(server[1])+' -i '+interval+' -w '+window+' -J>'+str(host_client)+'_'+str(server[0])+'.json'+' &')
                                    temp = str(host_client)+'_'+str(server[0])
                                    ax = str(server)
                                    buffer_server.append(temp)
                                    buffer_server.append(ax)
                                    name_files.append(str(host_client)+'_'+str(server[0]))

                                #Solo el parámetro de Intervalo, Anchode Banda y Longitud
                                elif(not 't' in json_data and ('i' in json_data) and ('l' in json_data) and ('b' in json_data) and (not 'w' in json_data)):
                                    interval = str(json_data['i'])
                                    bw = str(json_data['b'])
                                    length = str(json_data['l'])
                                    host_client.cmd('iperf3 -c '+str(server[0].IP())+' -p '+str(server[1])+' -i '+interval+' -b '+bw+' -l '+length+' -J>'+str(host_client)+'_'+str(server[0])+'.json'+' &')
                                    temp = str(host_client)+'_'+str(server[0])
                                    ax = str(server)
                                    buffer_server.append(temp)
                                    buffer_server.append(ax)
                                    name_files.append(str(host_client)+'_'+str(server[0]))

                                #Solo el parámetro de Intervalo, Anchode Banda y Window
                                elif(not 't' in json_data and ('i' in json_data) and (not 'l' in json_data) and ( 'b' in json_data) and ( 'w' in json_data)):
                                    interval = str(json_data['i'])
                                    bw = str(json_data['b'])
                                    window = str(json_data['w'])
                                    host_client.cmd('iperf3 -c '+str(server[0].IP())+' -p '+str(server[1])+' -i '+interval+' -b '+bw+' -w '+window+' -J>'+str(host_client)+'_'+str(server[0])+'.json'+' &')
                                    temp = str(host_client)+'_'+str(server[0])
                                    ax = str(server)
                                    buffer_server.append(temp)
                                    buffer_server.append(ax)
                                    name_files.append(str(host_client)+'_'+str(server[0]))

                                #Solo el parámetro de Intervalo, Longitud y Window
                                elif(not 't' in json_data and ('i' in json_data) and ('l' in json_data) and (not 'b' in json_data) and ( 'w' in json_data)):
                                    interval = str(json_data['i'])
                                    length = str(json_data['l'])
                                    window = str(json_data['w'])
                                    host_client.cmd('iperf3 -c '+str(server[0].IP())+' -p '+str(server[1])+' -i '+interval+' -l '+length+' -w '+window+' -J>'+str(host_client)+'_'+str(server[0])+'.json'+' &')
                                    temp = str(host_client)+'_'+str(server[0])
                                    ax = str(server)
                                    buffer_server.append(temp)
                                    buffer_server.append(ax)
                                    name_files.append(str(host_client)+'_'+str(server[0]))


                                #Solo el parámetro de Intervalo, Anchode Banda, Longitud y Window
                                elif(not 't' in json_data and ('i' in json_data) and ('l' in json_data) and ('b' in json_data) and ('w' in json_data)):
                                    interval = str(json_data['i'])
                                    bw = str(json_data['b'])
                                    length = str(json_data['l'])
                                    window = str(json_data['w'])
                                    host_client.cmd('iperf3 -c '+str(server[0].IP())+' -p '+str(server[1])+' -i '+interval+' -b '+bw+' -l '+length+' -w '+window+' -J>'+str(host_client)+'_'+str(server[0])+'.json'+' &')
                                    temp = str(host_client)+'_'+str(server[0])
                                    ax = str(server)
                                    buffer_server.append(temp)
                                    buffer_server.append(ax)
                                    name_files.append(str(host_client)+'_'+str(server[0]))

                              #Solo el parámetro de Longitud
                                elif(not 't' in json_data and (not 'i' in json_data) and ('l' in json_data) and (not 'b' in json_data) and (not 'w' in json_data)):
                                    length = str(json_data['l'])
                                    host_client.cmd('iperf3 -c '+str(server[0].IP())+' -p '+str(server[1])+' -l '+length+' -J>'+str(host_client)+'_'+str(server[0])+'.json'+' &')
                                    temp = str(host_client)+'_'+str(server[0])
                                    ax = str(server)
                                    buffer_server.append(temp)
                                    buffer_server.append(ax)
                                    name_files.append(str(host_client)+'_'+str(server[0]))

                              #Solo el parámetro de Longitud y Ancho de Banda
                                elif(not 't' in json_data and (not 'i' in json_data) and ('l' in json_data) and ('b' in json_data) and (not 'w' in json_data)):
                                    length = str(json_data['l'])
                                    bw = str(json_data['b'])
                                    host_client.cmd('iperf3 -c '+str(server[0].IP())+' -p '+str(server[1])+' -l '+length+' -b '+bw+' -J>'+str(host_client)+'_'+str(server[0])+'.json'+' &')
                                    temp = str(host_client)+'_'+str(server[0])
                                    ax = str(server)
                                    buffer_server.append(temp)
                                    buffer_server.append(ax)
                                    name_files.append(str(host_client)+'_'+str(server[0]))

                                #Solo el parámetro de Longitud y Ventana
                                elif(not 't' in json_data and (not 'i' in json_data) and ('l' in json_data) and (not 'b' in json_data) and ('w' in json_data)):
                                    length = str(json_data['l'])
                                    window = str(json_data['w'])
                                    host_client.cmd('iperf3 -c '+str(server[0].IP())+' -p '+str(server[1])+' -l '+length+' -w '+window+' -J>'+str(host_client)+'_'+str(server[0])+'.json'+' &')
                                    temp = str(host_client)+'_'+str(server[0])
                                    ax = str(server)
                                    buffer_server.append(temp)
                                    buffer_server.append(ax)
                                    name_files.append(str(host_client)+'_'+str(server[0]))
                                #Solo el parámetro de Longitud   Ancho de Banda y Ventana
                                elif(not 't' in json_data and (not 'i' in json_data) and ('l' in json_data) and ('b' in json_data) and ('w' in json_data)):
                                    length = str(json_data['l'])
                                    bw = str(json_data['b'])
                                    window = str(json_data['w'])
                                    host_client.cmd('iperf3 -c '+str(server[0].IP())+' -p '+str(server[1])+' -l '+length+' -b '+bw+' -w '+window+' -J>'+str(host_client)+'_'+str(server[0])+'.json'+' &')
                                    temp = str(host_client)+'_'+str(server[0])
                                    ax = str(server)
                                    buffer_server.append(temp)
                                    buffer_server.append(ax)
                                    name_files.append(str(host_client)+'_'+str(server[0]))
                                
                                #Solo el parámetro de Ancho de Banda
                                elif(not 't' in json_data and (not 'i' in json_data) and (not 'l' in json_data) and ('b' in json_data) and (not 'w' in json_data)):
                                    bw = str(json_data['b'])
                                    host_client.cmd('iperf3 -c '+str(server[0].IP())+' -p '+str(server[1])+' -b '+bw+' -J>'+str(host_client)+'_'+str(server[0])+'.json'+' &')
                                    temp = str(host_client)+'_'+str(server[0])
                                    ax = str(server)
                                    buffer_server.append(temp)
                                    buffer_server.append(ax)
                                    name_files.append(str(host_client)+'_'+str(server[0]))

                                #Solo el parámetro de  Ancho de Banda y Ventana
                                elif(not 't' in json_data and (not 'i' in json_data) and (not 'l' in json_data) and ('b' in json_data) and ('w' in json_data)):
                                    
                                    bw = str(json_data['b'])
                                    window = str(json_data['w'])
                                    host_client.cmd('iperf3 -c '+str(server[0].IP())+' -p '+str(server[1])+' -b '+bw+' -w '+window+' -J>'+str(host_client)+'_'+str(server[0])+'.json'+' &')
                                    temp = str(host_client)+'_'+str(server[0])
                                    ax = str(server)
                                    buffer_server.append(temp)
                                    buffer_server.append(ax)
                                    name_files.append(str(host_client)+'_'+str(server[0]))

                                #Solo el parámetro de Longitud   Ancho de Banda y Ventana
                                elif(not 't' in json_data and (not 'i' in json_data) and ('l' in json_data) and ('b' in json_data) and ('w' in json_data)):
                                    length = str(json_data['l'])
                                    bw = str(json_data['b'])
                                    window = str(json_data['w'])
                                    host_client.cmd('iperf3 -c '+str(server[0].IP())+' -p '+str(server[1])+' -l '+length+' -b '+bw+' -w '+window+' -J>'+str(host_client)+'_'+str(server[0])+'.json'+' &')
                                    temp = str(host_client)+'_'+str(server[0])
                                    ax = str(server)
                                    buffer_server.append(temp)
                                    buffer_server.append(ax)
                                    name_files.append(str(host_client)+'_'+str(server[0]))

                                 #Solo el parametro de Tiempo Intervalo  Ancho de Banda Ventana
                                
                                elif('t' in json_data and ('i' in json_data) and (not 'l' in json_data) and ('b' in json_data) and ('w' in json_data)):
                                    time_e = str(json_data['t'])
                                    bw = str(json_data['b'])
                                    interval =  str(json_data['i'])
                                    window = str(json_data['w'])
                                    host_client.cmd('iperf3 -c '+str(server[0].IP())+' -p '+str(server[1])+' -t '+time_e+' -b '+bw+' -i '+interval+' -w '+window+' -J>'+str(host_client)+'_'+str(server[0])+'.json'+' &')
                                    temp = str(host_client)+'_'+str(server[0])
                                    ax = str(server)
                                    buffer_server.append(temp)
                                    buffer_server.append(ax)
                                    name_files.append(str(host_client)+'_'+str(server[0]))

                                 #Solo el parametro de  Ventana
                                
                                elif(not 't' in json_data and (not 'i' in json_data) and (not'l' in json_data) and (not 'b' in json_data) and ('w' in json_data)):
                                    window = str(json_data['w'])
                                    host_client.cmd('iperf3 -c '+str(server[0].IP())+' -p '+str(server[1])+' -w '+window+' -J>'+str(host_client)+'_'+str(server[0])+'.json'+' &')
                                    temp = str(host_client)+'_'+str(server[0])
                                    ax = str(server)
                                    buffer_server.append(temp)
                                    buffer_server.append(ax)
                                    name_files.append(str(host_client)+'_'+str(server[0]))
    
                            #host_client.cmd('iperf3 -c '+str(server[0].IP())+' -p '+str(server[1])+' -t '+time_e+' -i '+interval+' -w '+window+' -J>'+str(host_client)+'_'+str(server[0])+'.json'+' &')
                            
        #Tiempo de espera para q se generen por completo los archivos JSON
            time.sleep(int(time_e) + 5)
            for name in name_files:
                    archive_json = json.loads(open(str(name)+'.json').read())
                    dict_data_traffic[str(name)] = archive_json

            #print(dict_data_traffic)
            #print('Keys Dict: ',dict_data_traffic.keys())
            traffic = {}
            for name in name_files:
                #print(str(name))
                connected = dict_data_traffic[str(name)]['start']['connected'][0]
                #print('tipo: ', type(connected))

                #datos del host que actua como transmisor
                local_host = connected['local_host']
                local_port = connected['local_port']

                #datos del host que actua como servidor
                remote_host = dict_data_traffic[str(name)]['start']['connecting_to']['host']
                remote_port = dict_data_traffic[str(name)]['start']['connecting_to']['port']

                #datos de los parámetros del tráfico en la red
                tcp_mss_default = dict_data_traffic[str(name)]['start']['tcp_mss_default']
                sock_bufsize = dict_data_traffic[str(name)]['start']['sock_bufsize']
                sndbuf_actual = dict_data_traffic[str(name)]['start']['sndbuf_actual']
                rcvbuf_actual = dict_data_traffic[str(name)]['start']['rcvbuf_actual'] 

                #datos del inicio del Test
                protocol = dict_data_traffic[str(name)]['start']['test_start']['protocol']
                blksize =  dict_data_traffic[str(name)]['start']['test_start']['blksize']
                omit =  dict_data_traffic[str(name)]['start']['test_start']['omit']
                duration =  dict_data_traffic[str(name)]['start']['test_start']['duration']
                num_bytes =  dict_data_traffic[str(name)]['start']['test_start']['bytes']
                blocks =  dict_data_traffic[str(name)]['start']['test_start']['blocks']
                    
                #Resultados del Tráfico generado
                rang = int(time_e)/int(interval)
                intervals = dict_data_traffic[str(name)]['intervals']
                times = {}
                data_speciffic= {}

                for t in range(rang):
                    streams = intervals[t]['streams'][0]
                    start = streams['start']
                    end = streams['end']
                    n_bytes = streams['bytes']
                    bits_per_second = streams['bits_per_second']
                    retransmits = streams['retransmits']
                    snd_cwnd = streams['snd_cwnd']
                    rtt = streams['rtt']
                    rttvar = streams['rttvar']
                    pmtu = streams['pmtu']
                    omitted = streams['omitted']
                    sender = streams['sender']

                    data_speciffic['start'] = start
                    data_speciffic['end'] = end
                    data_speciffic['n_bytes'] = n_bytes
                    data_speciffic['bits_per_second'] = bits_per_second
                    data_speciffic['retransmits'] = retransmits
                    data_speciffic['snd_cwnd'] = snd_cwnd
                    data_speciffic['rtt'] = rtt
                    data_speciffic['rttvar'] = rttvar
                    data_speciffic['pmtu'] = pmtu
                    data_speciffic['omitted'] = str(omitted)
                    data_speciffic['sender'] = str(sender)

                    times['t_'+str(t)] = data_speciffic
                    data_speciffic = {}

                data_gen['local_host'] = local_host
                data_gen['local_port'] = local_port
                data_gen['remote_host'] = remote_host
                data_gen['remote_port'] = remote_port
                data_gen['tcp_mss_default'] = tcp_mss_default
                data_gen['sock_bufsize'] = sock_bufsize
                data_gen['sndbuf_actual'] = sndbuf_actual
                data_gen['rcvbuf_actual'] = rcvbuf_actual
                data_gen['protocol'] = protocol
                data_gen['blksize'] = blksize
                data_gen['omit'] = omit
                data_gen['duration'] = duration
                data_gen['num_bytes'] = num_bytes
                data_gen['blocks'] = blocks
                procces_data['speciffic'] = times
                procces_data['general']= data_gen
                
                traffic[str(name)] = procces_data
                
                data_gen= {}
                times = {}
                procces_data = {}
            #print('Trafico!!!: ', traffic)
                    
                    #answer_to_client = net.iperf(hosts=[x, y], l4Type='TCP', udpBw=udpBW, fmt=None, seconds=time_e, port=5001)
                    #traffic_array[str(x)+"-"+str(y)]= answer_to_client
                    #charge_array[c]= traffic_array
                    #dict_answer['TCP'] = charge_array
                    #dict_answer["TCP " + str(x)+" to "+str(y) +" " + str(c)] = answer_to_client

            
            f = json.dumps(traffic)
            connection.sendall(f.encode())
            dict_answer = {}
            traffic = {}
            answer_to_client = None
            return True

        elif('xtreme' in json_data):
            pass
        elif('specific' in json_data):
            pass
        pass


    elif ('UDP' in json_data):
        
    
        #Tipos de Distribucion del Tráfico
        if('global' in json_data):

            print('UDP Global ...')
            host_size= (len(host_added))-1
            port_list =[]
            initial_port = 5000

            #Datos del modo de transmision
            #Solo una de estas tres opciones
            time_e = str(5)
            number = '0k'
            block = '0k'

            interval = str(1)
            window = '500k'
            length = '1m'
            bw = '1k'
            

            name_files = []
            dict_data_traffic = {}

            file_traffic= []
            data_traffic={}
            procces_data={}
            data_gen= {}

            #Lista de Puertos
            for pt in range(host_size):
                initial_port = initial_port + 1
                port_list.append(str(initial_port))


            aux_array = []

            for host_server in host_added:
                for port in port_list:
                    host_server.cmd('iperf3 -s -D -p '+str(port))
                    time.sleep(3)
                    aux = [host_server, port]
                    aux_array.append(aux)

            buffer_server = []
            for server in aux_array:
                for host_client in host_added:
                    if not (str(host_client)+'_'+str(server[0])) in buffer_server:
                        if not str(server) in buffer_server:
                            if str(server[0]) == str(host_client):
                                pass
                            else:
                                #Posibles casos de parametrizacion del Trafico en Iperf3.1
                                #Solo el parámetro de Tiempo 
                                if('t' in json_data and (not 'i' in json_data) and (not 'l' in json_data) and (not 'b' in json_data) and (not 'w' in json_data)):
                                    time_e = str(json_data['t'])
                                    host_client.cmd('iperf3 -c '+str(server[0].IP())+' -p '+str(server[1])+' -u '+' -t '+time_e+' -J>'+str(host_client)+'_'+str(server[0])+'.json'+' &')
                                    temp = str(host_client)+'_'+str(server[0])
                                    ax = str(server)
                                    buffer_server.append(temp)
                                    buffer_server.append(ax)
                                    name_files.append(str(host_client)+'_'+str(server[0]))
                                #Solo el parámetro de Tiempo con Intervalo 
                                elif('t' in json_data and ('i' in json_data) and (not 'l' in json_data) and (not 'b' in json_data) and (not 'w' in json_data)):
                                    time_e = str(json_data['t'])
                                    interval = str(json_data['i'])
                                    host_client.cmd('iperf3 -c '+str(server[0].IP())+' -p '+str(server[1])+' -u '+' -t '+time_e+' -i '+interval+' -J>'+str(host_client)+'_'+str(server[0])+'.json'+' &')
                                    temp = str(host_client)+'_'+str(server[0])
                                    ax = str(server)
                                    buffer_server.append(temp)
                                    buffer_server.append(ax)
                                    name_files.append(str(host_client)+'_'+str(server[0]))
                                #Solo el parametro de Tiempo con Longitud 
                                elif('t' in json_data and (not 'i' in json_data) and ('l' in json_data) and (not 'b' in json_data) and (not 'w' in json_data)):
                                    time_e = str(json_data['t'])
                                    length = str(json_data['i'])
                                    host_client.cmd('iperf3 -c '+str(server[0].IP())+' -p '+str(server[1])+' -u '+' -t '+time_e+' -l '+length+' -J>'+str(host_client)+'_'+str(server[0])+'.json'+' &')
                                    temp = str(host_client)+'_'+str(server[0])
                                    ax = str(server)
                                    buffer_server.append(temp)
                                    buffer_server.append(ax)
                                    name_files.append(str(host_client)+'_'+str(server[0]))
                                #Solo el parametro de Tiempo con Ancho de Banda
                                elif('t' in json_data and (not 'i' in json_data) and (not 'l' in json_data) and ('b' in json_data) and (not 'w' in json_data)):
                                    time_e = str(json_data['t'])
                                    bw = str(json_data['b'])
                                    host_client.cmd('iperf3 -c '+str(server[0].IP())+' -p '+str(server[1])+' -u '+' -t '+time_e+' -b '+bw+' -J>'+str(host_client)+'_'+str(server[0])+'.json'+' &')
                                    temp = str(host_client)+'_'+str(server[0])
                                    ax = str(server)
                                    buffer_server.append(temp)
                                    buffer_server.append(ax)
                                    name_files.append(str(host_client)+'_'+str(server[0]))
                                    pass
                                #Solo el parametro de Tiempo con Ventana
                                elif('t' in json_data and (not 'i' in json_data) and (not 'l' in json_data) and (not 'b' in json_data) and ('w' in json_data)):
                                    time_e = str(json_data['t'])
                                    window = str(json_data['w'])
                                    host_client.cmd('iperf3 -c '+str(server[0].IP())+' -p '+str(server[1])+' -u '+' -t '+time_e+' -w '+window+' -J>'+str(host_client)+'_'+str(server[0])+'.json'+' &')
                                    temp = str(host_client)+'_'+str(server[0])
                                    ax = str(server)
                                    buffer_server.append(temp)
                                    buffer_server.append(ax)
                                    name_files.append(str(host_client)+'_'+str(server[0]))
                                #Solo el parametro de Tiempo con Intervalo y Longitud
                                elif('t' in json_data and ('i' in json_data) and ( 'l' in json_data) and (not 'b' in json_data) and (not 'w' in json_data)):
                                    time_e = str(json_data['t'])
                                    interval = str(json_data['i'])
                                    length =  str(json_data['l'])
                                    host_client.cmd('iperf3 -c '+str(server[0].IP())+' -p '+str(server[1])+' -u '+' -t '+time_e+' -i '+interval+' -l '+length+' -J>'+str(host_client)+'_'+str(server[0])+'.json'+' &')
                                    temp = str(host_client)+'_'+str(server[0])
                                    ax = str(server)
                                    buffer_server.append(temp)
                                    buffer_server.append(ax)
                                    name_files.append(str(host_client)+'_'+str(server[0]))
                                #Solo el parametro de Tiempo con Intervalo y Ancho de Banda
                                elif('t' in json_data and ('i' in json_data) and ( not 'l' in json_data) and ('b' in json_data) and (not 'w' in json_data)):
                                    time_e = str(json_data['t'])
                                    interval = str(json_data['i'])
                                    bw =  str(json_data['b'])
                                    host_client.cmd('iperf3 -c '+str(server[0].IP())+' -p '+str(server[1])+' -u '+' -t '+time_e+' -i '+interval+' -b '+bw+' -J>'+str(host_client)+'_'+str(server[0])+'.json'+' &')
                                    temp = str(host_client)+'_'+str(server[0])
                                    ax = str(server)
                                    buffer_server.append(temp)
                                    buffer_server.append(ax)
                                    name_files.append(str(host_client)+'_'+str(server[0]))
                                #Solo el parametro de Tiempo con Longitud y Ventana
                                elif('t' in json_data and (not 'i' in json_data) and ('l' in json_data) and (not 'b' in json_data) and ('w' in json_data)):
                                    time_e = str(json_data['t'])
                                    length = str(json_data['l'])
                                    window =  str(json_data['w'])
                                    host_client.cmd('iperf3 -c '+str(server[0].IP())+' -p '+str(server[1])+' -u '+' -t '+time_e+' -l '+length+' -w '+window+' -J>'+str(host_client)+'_'+str(server[0])+'.json'+' &')
                                    temp = str(host_client)+'_'+str(server[0])
                                    ax = str(server)
                                    buffer_server.append(temp)
                                    buffer_server.append(ax)
                                    name_files.append(str(host_client)+'_'+str(server[0]))
                                #Solo el parametro de Tiempo con  Ancho de Banda y Ventana
                                elif('t' in json_data and (not 'i' in json_data) and (not 'l' in json_data) and ('b' in json_data) and (not 'w' in json_data)):
                                    time_e = str(json_data['t'])
                                    window = str(json_data['w'])
                                    bw =  str(json_data['b'])
                                    host_client.cmd('iperf3 -c '+str(server[0].IP())+' -p '+str(server[1])+' -u '+' -t '+time_e+' -w '+window+' -b '+bw+' -J>'+str(host_client)+'_'+str(server[0])+'.json'+' &')
                                    temp = str(host_client)+'_'+str(server[0])
                                    ax = str(server)
                                    buffer_server.append(temp)
                                    buffer_server.append(ax)
                                    name_files.append(str(host_client)+'_'+str(server[0]))

                                #Solo el parametro de Tiempo con Intervalo y Ventana 
                                elif('t' in json_data and ('i' in json_data) and ( not 'l' in json_data) and (not 'b' in json_data) and ('w' in json_data)):
                                    time_e = str(json_data['t'])
                                    interval = str(json_data['i'])
                                    window =  str(json_data['w'])
                                    host_client.cmd('iperf3 -c '+str(server[0].IP())+' -p '+str(server[1])+' -u '+' -t '+time_e+' -i '+interval+' -w '+window+' -J>'+str(host_client)+'_'+str(server[0])+'.json'+' &')
                                    temp = str(host_client)+'_'+str(server[0])
                                    ax = str(server)
                                    buffer_server.append(temp)
                                    buffer_server.append(ax)
                                    name_files.append(str(host_client)+'_'+str(server[0]))

                                #Solo el parametro de Tiempo con Intervalo Longitud  Ancho de Banda
                                elif('t' in json_data and ('i' in json_data) and ( 'l' in json_data) and ('b' in json_data) and (not 'w' in json_data)):
                                    time_e = str(json_data['t'])
                                    interval = str(json_data['i'])
                                    length =  str(json_data['l'])
                                    bw = str(json_data['b'])
                                    host_client.cmd('iperf3 -c '+str(server[0].IP())+' -p '+str(server[1])+' -u '+' -t '+time_e+' -i '+interval+' -l '+length+' -b '+bw+' -J>'+str(host_client)+'_'+str(server[0])+'.json'+' &')
                                    temp = str(host_client)+'_'+str(server[0])
                                    ax = str(server)
                                    buffer_server.append(temp)
                                    buffer_server.append(ax)
                                    name_files.append(str(host_client)+'_'+str(server[0]))
                                #Solo el parametro de Tiempo con Intervalo Longitud  Ventana
                                elif('t' in json_data and ('i' in json_data) and ( 'l' in json_data) and (not 'b' in json_data) and ('w' in json_data)):
                                    time_e = str(json_data['t'])
                                    interval = str(json_data['i'])
                                    length =  str(json_data['l'])
                                    window = str(json_data['w'])
                                    host_client.cmd('iperf3 -c '+str(server[0].IP())+' -p '+str(server[1])+' -u '+' -t '+time_e+' -i '+interval+' -l '+length+' -w '+window+' -J>'+str(host_client)+'_'+str(server[0])+'.json'+' &')
                                    temp = str(host_client)+'_'+str(server[0])
                                    ax = str(server)
                                    buffer_server.append(temp)
                                    buffer_server.append(ax)
                                    name_files.append(str(host_client)+'_'+str(server[0]))
                                #Solo el parametro de Tiempo con Ancho de Banda Longitud  Ventana
                                elif('t' in json_data and (not 'i' in json_data) and ( 'l' in json_data) and ('b' in json_data) and ('w' in json_data)):
                                    time_e = str(json_data['t'])
                                    bw = str(json_data['b'])
                                    length =  str(json_data['l'])
                                    window = str(json_data['w'])
                                    host_client.cmd('iperf3 -c '+str(server[0].IP())+' -p '+str(server[1])+' -u '+' -t '+time_e+' -b '+bw+' -l '+length+' -w '+window+' -J>'+str(host_client)+'_'+str(server[0])+'.json'+' &')
                                    temp = str(host_client)+'_'+str(server[0])
                                    ax = str(server)
                                    buffer_server.append(temp)
                                    buffer_server.append(ax)
                                    name_files.append(str(host_client)+'_'+str(server[0]))
                                #Solo el parametro de Tiempo con Intervalo Longitud  Ancho de Banda Ventana
                                elif('t' in json_data and ('i' in json_data) and ( 'l' in json_data) and ('b' in json_data) and ('w' in json_data)):
                                    time_e = str(json_data['t'])
                                    interval = str(json_data['i'])
                                    length =  str(json_data['l'])
                                    bw = str(json_data['b'])
                                    window = str(json_data['w'])
                                    host_client.cmd('iperf3 -c '+str(server[0].IP())+' -p '+str(server[1])+' -u '+' -t '+time_e+' -i '+interval+' -l '+length+' -b '+bw+' -w '+window+' -J>'+str(host_client)+'_'+str(server[0])+'.json'+' &')
                                    temp = str(host_client)+'_'+str(server[0])
                                    ax = str(server)
                                    buffer_server.append(temp)
                                    buffer_server.append(ax)
                                    name_files.append(str(host_client)+'_'+str(server[0]))

                                #Solo el parámetro de Intervalo
                                elif(not 't' in json_data and ('i' in json_data) and (not 'l' in json_data) and (not 'b' in json_data) and (not 'w' in json_data)):
                                    interval = str(json_data['i'])
                                    host_client.cmd('iperf3 -c '+str(server[0].IP())+' -p '+str(server[1])+' -u '+' -i '+interval+' -J>'+str(host_client)+'_'+str(server[0])+'.json'+' &')
                                    temp = str(host_client)+'_'+str(server[0])
                                    ax = str(server)
                                    buffer_server.append(temp)
                                    buffer_server.append(ax)
                                    name_files.append(str(host_client)+'_'+str(server[0]))

                                #Solo el parámetro de Intervalo y Longitud
                                elif(not 't' in json_data and ('i' in json_data) and ('l' in json_data) and (not 'b' in json_data) and (not 'w' in json_data)):
                                    interval = str(json_data['i'])
                                    length = str(json_data['l'])
                                    host_client.cmd('iperf3 -c '+str(server[0].IP())+' -p '+str(server[1])+' -u '+' -i '+interval+' -l ' +length+' -J>'+str(host_client)+'_'+str(server[0])+'.json'+' &')
                                    temp = str(host_client)+'_'+str(server[0])
                                    ax = str(server)
                                    buffer_server.append(temp)
                                    buffer_server.append(ax)
                                    name_files.append(str(host_client)+'_'+str(server[0]))

                                #Solo el parámetro de Intervalo y Anchode Banda
                                elif(not 't' in json_data and ('i' in json_data) and (not 'l' in json_data) and ('b' in json_data) and (not 'w' in json_data)):
                                    interval = str(json_data['i'])
                                    bw = str(json_data['b'])
                                    host_client.cmd('iperf3 -c '+str(server[0].IP())+' -p '+str(server[1])+' -u '+' -i '+interval+' -b '+bw+' -J>'+str(host_client)+'_'+str(server[0])+'.json'+' &')
                                    temp = str(host_client)+'_'+str(server[0])
                                    ax = str(server)
                                    buffer_server.append(temp)
                                    buffer_server.append(ax)
                                    name_files.append(str(host_client)+'_'+str(server[0]))

                                #Solo el parámetro de Intervalo y Ventana
                                elif(not 't' in json_data and ('i' in json_data) and (not 'l' in json_data) and (not 'b' in json_data) and ('w' in json_data)):
                                    interval = str(json_data['i'])
                                    window = str(json_data['w'])
                                    host_client.cmd('iperf3 -c '+str(server[0].IP())+' -p '+str(server[1])+' -u '+' -i '+interval+' -w '+window+' -J>'+str(host_client)+'_'+str(server[0])+'.json'+' &')
                                    temp = str(host_client)+'_'+str(server[0])
                                    ax = str(server)
                                    buffer_server.append(temp)
                                    buffer_server.append(ax)
                                    name_files.append(str(host_client)+'_'+str(server[0]))

                                #Solo el parámetro de Intervalo, Anchode Banda y Longitud
                                elif(not 't' in json_data and ('i' in json_data) and ('l' in json_data) and ('b' in json_data) and (not 'w' in json_data)):
                                    interval = str(json_data['i'])
                                    bw = str(json_data['b'])
                                    length = str(json_data['l'])
                                    host_client.cmd('iperf3 -c '+str(server[0].IP())+' -p '+str(server[1])+' -u '+' -i '+interval+' -b '+bw+' -l '+length+' -J>'+str(host_client)+'_'+str(server[0])+'.json'+' &')
                                    temp = str(host_client)+'_'+str(server[0])
                                    ax = str(server)
                                    buffer_server.append(temp)
                                    buffer_server.append(ax)
                                    name_files.append(str(host_client)+'_'+str(server[0]))

                                #Solo el parámetro de Intervalo, Anchode Banda y Window
                                elif(not 't' in json_data and ('i' in json_data) and (not 'l' in json_data) and ( 'b' in json_data) and ( 'w' in json_data)):
                                    interval = str(json_data['i'])
                                    bw = str(json_data['b'])
                                    window = str(json_data['w'])
                                    host_client.cmd('iperf3 -c '+str(server[0].IP())+' -p '+str(server[1])+' -u '+' -i '+interval+' -b '+bw+' -w '+window+' -J>'+str(host_client)+'_'+str(server[0])+'.json'+' &')
                                    temp = str(host_client)+'_'+str(server[0])
                                    ax = str(server)
                                    buffer_server.append(temp)
                                    buffer_server.append(ax)
                                    name_files.append(str(host_client)+'_'+str(server[0]))

                                #Solo el parámetro de Intervalo, Longitud y Window
                                elif(not 't' in json_data and ('i' in json_data) and ('l' in json_data) and (not 'b' in json_data) and ( 'w' in json_data)):
                                    interval = str(json_data['i'])
                                    length = str(json_data['l'])
                                    window = str(json_data['w'])
                                    host_client.cmd('iperf3 -c '+str(server[0].IP())+' -p '+str(server[1])+' -u '+' -i '+interval+' -l '+length+' -w '+window+' -J>'+str(host_client)+'_'+str(server[0])+'.json'+' &')
                                    temp = str(host_client)+'_'+str(server[0])
                                    ax = str(server)
                                    buffer_server.append(temp)
                                    buffer_server.append(ax)
                                    name_files.append(str(host_client)+'_'+str(server[0]))


                                #Solo el parámetro de Intervalo, Anchode Banda, Longitud y Window
                                elif(not 't' in json_data and ('i' in json_data) and ('l' in json_data) and ('b' in json_data) and ('w' in json_data)):
                                    interval = str(json_data['i'])
                                    bw = str(json_data['b'])
                                    length = str(json_data['l'])
                                    window = str(json_data['w'])
                                    host_client.cmd('iperf3 -c '+str(server[0].IP())+' -p '+str(server[1])+' -u '+' -i '+interval+' -b '+bw+' -l '+length+' -w '+window+' -J>'+str(host_client)+'_'+str(server[0])+'.json'+' &')
                                    temp = str(host_client)+'_'+str(server[0])
                                    ax = str(server)
                                    buffer_server.append(temp)
                                    buffer_server.append(ax)
                                    name_files.append(str(host_client)+'_'+str(server[0]))

                              #Solo el parámetro de Longitud
                                elif(not 't' in json_data and (not 'i' in json_data) and ('l' in json_data) and (not 'b' in json_data) and (not 'w' in json_data)):
                                    length = str(json_data['l'])
                                    host_client.cmd('iperf3 -c '+str(server[0].IP())+' -p '+str(server[1])+' -u '+' -l '+length+' -J>'+str(host_client)+'_'+str(server[0])+'.json'+' &')
                                    temp = str(host_client)+'_'+str(server[0])
                                    ax = str(server)
                                    buffer_server.append(temp)
                                    buffer_server.append(ax)
                                    name_files.append(str(host_client)+'_'+str(server[0]))

                              #Solo el parámetro de Longitud y Ancho de Banda
                                elif(not 't' in json_data and (not 'i' in json_data) and ('l' in json_data) and ('b' in json_data) and (not 'w' in json_data)):
                                    length = str(json_data['l'])
                                    bw = str(json_data['b'])
                                    host_client.cmd('iperf3 -c '+str(server[0].IP())+' -p '+str(server[1])+' -u '+' -l '+length+' -b '+bw+' -J>'+str(host_client)+'_'+str(server[0])+'.json'+' &')
                                    temp = str(host_client)+'_'+str(server[0])
                                    ax = str(server)
                                    buffer_server.append(temp)
                                    buffer_server.append(ax)
                                    name_files.append(str(host_client)+'_'+str(server[0]))

                                #Solo el parámetro de Longitud y Ventana
                                elif(not 't' in json_data and (not 'i' in json_data) and ('l' in json_data) and (not 'b' in json_data) and ('w' in json_data)):
                                    length = str(json_data['l'])
                                    window = str(json_data['w'])
                                    host_client.cmd('iperf3 -c '+str(server[0].IP())+' -p '+str(server[1])+' -u '+' -l '+length+' -w '+window+' -J>'+str(host_client)+'_'+str(server[0])+'.json'+' &')
                                    temp = str(host_client)+'_'+str(server[0])
                                    ax = str(server)
                                    buffer_server.append(temp)
                                    buffer_server.append(ax)
                                    name_files.append(str(host_client)+'_'+str(server[0]))
                                #Solo el parámetro de Longitud   Ancho de Banda y Ventana
                                elif(not 't' in json_data and (not 'i' in json_data) and ('l' in json_data) and ('b' in json_data) and ('w' in json_data)):
                                    length = str(json_data['l'])
                                    bw = str(json_data['b'])
                                    window = str(json_data['w'])
                                    host_client.cmd('iperf3 -c '+str(server[0].IP())+' -p '+str(server[1])+' -u '+' -l '+length+' -b '+bw+' -w '+window+' -J>'+str(host_client)+'_'+str(server[0])+'.json'+' &')
                                    temp = str(host_client)+'_'+str(server[0])
                                    ax = str(server)
                                    buffer_server.append(temp)
                                    buffer_server.append(ax)
                                    name_files.append(str(host_client)+'_'+str(server[0]))
                                
                                #Solo el parámetro de Ancho de Banda
                                elif(not 't' in json_data and (not 'i' in json_data) and (not 'l' in json_data) and ('b' in json_data) and (not 'w' in json_data)):
                                    bw = str(json_data['b'])
                                    host_client.cmd('iperf3 -c '+str(server[0].IP())+' -p '+str(server[1])+' -u '+' -b '+bw+' -J>'+str(host_client)+'_'+str(server[0])+'.json'+' &')
                                    temp = str(host_client)+'_'+str(server[0])
                                    ax = str(server)
                                    buffer_server.append(temp)
                                    buffer_server.append(ax)
                                    name_files.append(str(host_client)+'_'+str(server[0]))

                                #Solo el parámetro de  Ancho de Banda y Ventana
                                elif(not 't' in json_data and (not 'i' in json_data) and (not 'l' in json_data) and ('b' in json_data) and ('w' in json_data)):
                                    
                                    bw = str(json_data['b'])
                                    window = str(json_data['w'])
                                    host_client.cmd('iperf3 -c '+str(server[0].IP())+' -p '+str(server[1])+' -u '+' -b '+bw+' -w '+window+' -J>'+str(host_client)+'_'+str(server[0])+'.json'+' &')
                                    temp = str(host_client)+'_'+str(server[0])
                                    ax = str(server)
                                    buffer_server.append(temp)
                                    buffer_server.append(ax)
                                    name_files.append(str(host_client)+'_'+str(server[0]))

                                #Solo el parámetro de Longitud   Ancho de Banda y Ventana
                                elif(not 't' in json_data and (not 'i' in json_data) and ('l' in json_data) and ('b' in json_data) and ('w' in json_data)):
                                    length = str(json_data['l'])
                                    bw = str(json_data['b'])
                                    window = str(json_data['w'])
                                    host_client.cmd('iperf3 -c '+str(server[0].IP())+' -p '+str(server[1])+' -u '+' -l '+length+' -b '+bw+' -w '+window+' -J>'+str(host_client)+'_'+str(server[0])+'.json'+' &')
                                    temp = str(host_client)+'_'+str(server[0])
                                    ax = str(server)
                                    buffer_server.append(temp)
                                    buffer_server.append(ax)
                                    name_files.append(str(host_client)+'_'+str(server[0]))

                                 #Solo el parametro de Tiempo Intervalo  Ancho de Banda Ventana
                                
                                elif('t' in json_data and ('i' in json_data) and (not 'l' in json_data) and ('b' in json_data) and ('w' in json_data)):
                                    time_e = str(json_data['t'])
                                    bw = str(json_data['b'])
                                    interval =  str(json_data['i'])
                                    window = str(json_data['w'])
                                    host_client.cmd('iperf3 -c '+str(server[0].IP())+' -p '+str(server[1])+' -u '+' -t '+time_e+' -b '+bw+' -i '+interval+' -w '+window+' -J>'+str(host_client)+'_'+str(server[0])+'.json'+' &')
                                    temp = str(host_client)+'_'+str(server[0])
                                    ax = str(server)
                                    buffer_server.append(temp)
                                    buffer_server.append(ax)
                                    name_files.append(str(host_client)+'_'+str(server[0]))

                                 #Solo el parametro de  Ventana
                                
                                elif(not 't' in json_data and (not 'i' in json_data) and (not'l' in json_data) and (not 'b' in json_data) and ('w' in json_data)):
                                    window = str(json_data['w'])
                                    host_client.cmd('iperf3 -c '+str(server[0].IP())+' -p '+str(server[1])+' -u '+' -w '+window+' -J>'+str(host_client)+'_'+str(server[0])+'.json'+' &')
                                    temp = str(host_client)+'_'+str(server[0])
                                    ax = str(server)
                                    buffer_server.append(temp)
                                    buffer_server.append(ax)
                                    name_files.append(str(host_client)+'_'+str(server[0]))
    
                            #host_client.cmd('iperf3 -c '+str(server[0].IP())+' -p '+str(server[1])+' -t '+time_e+' -i '+interval+' -w '+window+' -J>'+str(host_client)+'_'+str(server[0])+'.json'+' &')
                            
        #Tiempo de espera para q se generen por completo los archivos JSON
            time.sleep(int(time_e) + 5)
            for name in name_files:
                    archive_json = json.loads(open(str(name)+'.json').read())
                    dict_data_traffic[str(name)] = archive_json

            #print(dict_data_traffic)
            #print('Keys Dict: ',dict_data_traffic.keys())
            traffic = {}
            for name in name_files:
                #print(str(name))
                connected = dict_data_traffic[str(name)]['start']['connected'][0]
                #print('tipo: ', type(connected))

                #datos del host que actua como transmisor
                local_host = connected['local_host']
                local_port = connected['local_port']

                #datos del host que actua como servidor
                remote_host = dict_data_traffic[str(name)]['start']['connecting_to']['host']
                remote_port = dict_data_traffic[str(name)]['start']['connecting_to']['port']

                #datos de los parámetros del tráfico en la red
                #tcp_mss_default = dict_data_traffic[str(name)]['start']['tcp_mss_default']
                sock_bufsize = dict_data_traffic[str(name)]['start']['sock_bufsize']
                sndbuf_actual = dict_data_traffic[str(name)]['start']['sndbuf_actual']
                rcvbuf_actual = dict_data_traffic[str(name)]['start']['rcvbuf_actual'] 

                #datos del inicio del Test
                protocol = dict_data_traffic[str(name)]['start']['test_start']['protocol']
                blksize =  dict_data_traffic[str(name)]['start']['test_start']['blksize']
                omit =  dict_data_traffic[str(name)]['start']['test_start']['omit']
                duration =  dict_data_traffic[str(name)]['start']['test_start']['duration']
                num_bytes =  dict_data_traffic[str(name)]['start']['test_start']['bytes']
                blocks =  dict_data_traffic[str(name)]['start']['test_start']['blocks']
                
                    
                #Resultados del Tráfico generado
                rang = int(time_e)/int(interval)
                intervals = dict_data_traffic[str(name)]['intervals']
                times = {}
                data_speciffic= {}

                for t in range(rang):
                    streams = intervals[t]['streams'][0]
                    start = streams['start']
                    end = streams['end']
                    n_bytes = streams['bytes']
                    bits_per_second = streams['bits_per_second']
                    packets = streams['packets']
                    omitted = streams['omitted']
                    sender = streams['sender']

                    data_speciffic['start'] = start
                    data_speciffic['end'] = end
                    data_speciffic['n_bytes'] = n_bytes
                    data_speciffic['bits_per_second'] = bits_per_second
                    data_speciffic['packets'] = packets
                    data_speciffic['omitted'] = str(omitted)
                    data_speciffic['sender'] = str(sender)

                    times['t_'+str(t)] = data_speciffic
                    data_speciffic = {}

                data_gen['local_host'] = local_host
                data_gen['local_port'] = local_port
                data_gen['remote_host'] = remote_host
                data_gen['remote_port'] = remote_port
                
                data_gen['sock_bufsize'] = sock_bufsize
                data_gen['sndbuf_actual'] = sndbuf_actual
                data_gen['rcvbuf_actual'] = rcvbuf_actual
                data_gen['protocol'] = protocol
                data_gen['blksize'] = blksize
                data_gen['omit'] = omit
                data_gen['duration'] = duration
                data_gen['num_bytes'] = num_bytes
                data_gen['blocks'] = blocks
                procces_data['speciffic'] = times
                procces_data['general']= data_gen
                
                traffic[str(name)] = procces_data
                
                data_gen= {}
                times = {}
                procces_data = {}

            
            f = json.dumps(traffic)
            connection.sendall(f.encode())
            dict_answer = {}
            traffic = {}
            answer_to_client = None
            return True

        elif('xtreme' in json_data):
            pass
        elif('specific' in json_data):
            pass
        pass




    
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
        w.start()
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

