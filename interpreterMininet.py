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

# Creacion de la red en Mininet
net = None

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
    net = Mininet(build=None)
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


def interpreter(json_data, connection):
    answer_to_client = None
    dict_answer = {}
    if 'action' in json_data:

        act = json_data['action']
        if act == "stop":
            print("Terminando Emulacion ...")
            if net != None:
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

    elif ('pingall' in json_data) and (not 'TCP' in json_data) and (not 'UDP' in json_data):
        print('Ping All ...')

        charge = int(json_data['pingall'])
        for c in range(charge):
            if net != None:
                answer_to_client = net.pingAll()
                dict_answer["pingall" + str(c)] = answer_to_client

        f = json.dumps(dict_answer)
        connection.sendall(f.encode())
        dict_answer = {}
        answer_to_client = None

        return True

    elif not 'pingall' in json_data and 'TCP' in json_data and not 'UDP' in json_data:
        print('TCP ...')
        charge = int(json_data['TCP'])
        for c in range(charge):
            if net != None:
                answer_to_client = net.iperf()
                dict_answer["TCP" + str(c)] = answer_to_client

        f = json.dumps(dict_answer)
        connection.sendall(f.encode())
        dict_answer = {}
        answer_to_client = None
        return True

    elif not 'pingall' in json_data and not 'TCP' in json_data and 'UDP' in json_data:
        print('UDP ...')
        charge = int(json_data['UDP'])
        for c in range(charge):
            if net != None:
                answer_to_client = net.iperf(hosts = None,l4Type = 'UDP',udpBw = '10M',fmt = None, seconds = 5, port = 5001 )
                dict_answer["UDP" + str(c)] = answer_to_client

        f = json.dumps(dict_answer)
        connection.sendall(f.encode())
        dict_answer = {}
        answer_to_client = None
        return True

    elif 'pingall' in json_data and 'TCP' in json_data and not 'UDP' in json_data:
        print('Ping All - TCP ...')
        charge = int(json_data['pingall'])
        for c in range(charge):
            if net != None:
                answer_to_client = net.pingAll()
                dict_answer["pingall" + str(c)] = answer_to_client
                answer_to_client = net.iperf()
                dict_answer["TCP" + str(c)] = answer_to_client

        f = json.dumps(dict_answer)
        connection.sendall(f.encode())
        dict_answer = {}
        answer_to_client = None
        return True

    elif not 'pingall' in json_data and 'TCP' in json_data and 'UDP' in json_data:
        print('TCP - UDP ...')
        charge = int(json_data['TCP'])
        
        for c in range(charge):
            if net != None:
                answer_to_client = net.iperf()
                dict_answer["TCP" + str(c)] = answer_to_client
                answer_to_client = net.iperf(hosts = None,l4Type = 'UDP',udpBw = '10M',fmt = None, seconds = 5, port = 5001 )
                dict_answer["UDP" + str(c)] = answer_to_client

        f = json.dumps(dict_answer)
        connection.sendall(f.encode())
        dict_answer = {}
        answer_to_client = None
        return True

    elif 'pingall' in json_data and not 'TCP' in json_data and 'UDP' in json_data:
        print('Ping All - UDP ...')
        
        charge = int(json_data['pingall'])
        for c in range(charge):
            if net != None:
                answer_to_client = net.pingAll()
                dict_answer["pingall" + str(c)] = answer_to_client
                answer_to_client = net.iperf(hosts = None,l4Type = 'UDP',udpBw = '10M',fmt = None, seconds = 5, port = 5001 )
                dict_answer["UDP" + str(c)] = answer_to_client

        f = json.dumps(dict_answer)
        connection.sendall(f.encode())
        dict_answer = {}
        answer_to_client = None
        return True

    elif 'pingall' in json_data and 'TCP' in json_data and 'UDP' in json_data:
        print('Ping All - TCP - UDP ...')
        
        charge = int(json_data['pingall'])
        for c in range(charge):
            if net != None:
                answer_to_client = net.pingAll()
                dict_answer["pingall" + str(c)] = answer_to_client
                answer_to_client = net.iperf()
                dict_answer["TCP" + str(c)] = answer_to_client
                answer_to_client = net.iperf(hosts = None,l4Type = 'UDP',udpBw = '10M',fmt = None, seconds = 5, port = 5001 )
                dict_answer["UDP" + str(c)] = answer_to_client

        f = json.dumps(dict_answer)
        connection.sendall(f.encode())
        dict_answer = {}
        answer_to_client = None
        return True

    elif ('pingallG' in json_data) and (not 'TCPG' in json_data) and (not 'UDPG' in json_data):
        print('Ping All Global ...')
        charge = int(json_data['pingallG'])
        for c in range(charge):
            if net != None:
                answer_to_client = net.pingAll()
                dict_answer["pingall " + str(c)] = answer_to_client

        f = json.dumps(dict_answer)
        connection.sendall(f.encode())
        dict_answer = {}
        answer_to_client = None
        return True

    elif not 'pingallG' in json_data and 'TCPG' in json_data and  not 'UDPG' in json_data :
        print('TCP Global ...')
        charge = int(json_data['TCPG'])
        
        for c in range(charge):
            for x in host_added:
                for y in host_added:
                    if str(x) == str(y):
                        pass
                    else:
                        if net != None:
                            answer_to_client = net.iperf(hosts = [x,y],l4Type = 'TCP',udpBw = '10M',fmt = None, seconds = 5, port = 5001 )            
                            dict_answer["TCP " + str(x)+" to "+str(y) + " " + str(c) ] = answer_to_client
            
            #answer_to_client = CLI(net,script= "tcp.sh")
            #dict_answer["TCP" + str(c)] = answer_to_client

        f = json.dumps(dict_answer)
        connection.sendall(f.encode())
        dict_answer = {}
        answer_to_client = None
        return True

    elif not 'pingallG' in json_data  and not 'TCPG' in json_data and 'UDPG' in json_data:
        print('UDP Global ...')
        charge = int(json_data['UDPG'])
        
        for c in range(charge):
            for x in host_added:
                for y in host_added:
                    if str(x) == str(y):
                        pass
                    else:
                        if net != None:
                            answer_to_client = net.iperf(hosts = [x,y],l4Type = 'UDP',udpBw = '1024M',fmt = None, seconds = 5, port = 5001 )            
                            dict_answer["UDP " + str(x)+" to "+ str(y)+ " " +str(c)] = answer_to_client
        
        f = json.dumps(dict_answer)
        connection.sendall(f.encode())
        dict_answer = {}
        answer_to_client = None
        return True

    elif 'pingallG' in json_data  and 'TCPG' in json_data  and not 'UDPG' in json_data:
        print('Ping All - TCP Global ...')
        charge = int(json_data['pingallG'])
        
        for c in range(charge):
            answer_to_client = net.pingAll()
            dict_answer["pingall " + str(c)] = answer_to_client
            for x in host_added:
                for y in host_added:
                    if str(x) == str(y):
                        pass
                    else:
                        if net != None:
                            answer_to_client = net.iperf(hosts = [x,y],l4Type = 'TCP',udpBw = '10M',fmt = None, seconds = 5, port = 5001 )            
                            dict_answer["TCP " + str(x)+" to "+str(y) + " " + str(c) ] = answer_to_client

        f = json.dumps(dict_answer)
        connection.sendall(f.encode())
        dict_answer = {}
        answer_to_client = None
        return True

    elif not 'pingallG' in json_data  and 'TCPG' in json_data and 'UDPG' in json_data:
        print('TCP - UDP Global ...')
        charge = int(json_data['TCPG'])
        for c in range(charge):
            for c in range(charge):
                for x in host_added:
                    for y in host_added:
                        if str(x) == str(y):
                            pass
                        else:
                            if net != None:
                                answer_to_client = net.iperf(hosts = [x,y],l4Type = 'TCP',udpBw = '10M',fmt = None, seconds = 5, port = 5001 )
                                dict_answer["TCP " + str(x)+" to "+ str(y)+ " " +str(c)] = answer_to_client
                                answer_to_client = net.iperf(hosts = [x,y],l4Type = 'UDP',udpBw = '1024M',fmt = None, seconds = 5, port = 5001 )
                                dict_answer["UDP " + str(x)+" to "+ str(y)+ " " +str(c)] = answer_to_client


        f = json.dumps(dict_answer)
        connection.sendall(f.encode())
        dict_answer = {}
        answer_to_client = None
        return True

    elif 'pingallG' in json_data and not 'TCPG' in json_data and 'UDPG' in json_data:
        print('Ping All - UDP Global ...')
        
        charge = int(json_data['pingallG'])
        for c in range(charge):
            answer_to_client = net.pingAll()
            dict_answer["pingall " + str(c)] = answer_to_client
            for x in host_added:
                for y in host_added:
                    if str(x) == str(y):
                        pass
                    else:
                        if net != None:
                            answer_to_client = net.iperf(hosts = [x,y],l4Type = 'UDP',udpBw = '1024M',fmt = None, seconds = 5, port = 5001 )            
                            dict_answer["UDP " + str(x)+" to "+ str(y)+ " " +str(c)] = answer_to_client

        f = json.dumps(dict_answer)
        connection.sendall(f.encode())
        dict_answer = {}
        answer_to_client = None
        return True

    elif 'pingallG' in json_data and 'TCPG' in json_data and 'UDPG' in json_data:
        print('Ping All - TCP - UDP')
        charge = int(json_data['pingallG'])
        for c in range(charge):
            answer_to_client = net.pingAll()
            dict_answer["pingall " + str(c)] = answer_to_client
            for c in range(charge):
                for x in host_added:
                    for y in host_added:
                        if str(x) == str(y):
                            pass
                        else:
                            if net != None:
                                answer_to_client = net.iperf(hosts = [x,y],l4Type = 'TCP',udpBw = '10M',fmt = None, seconds = 5, port = 5001 )
                                dict_answer["TCP " + str(x)+" to "+ str(y)+ " " +str(c)] = answer_to_client
                                answer_to_client = net.iperf(hosts = [x,y],l4Type = 'UDP',udpBw = '1024M',fmt = None, seconds = 5, port = 5001 )
                                dict_answer["UDP " + str(x)+" to "+ str(y)+ " " +str(c)] = answer_to_client

        f = json.dumps(dict_answer)
        connection.sendall(f.encode())
        dict_answer = {}
        answer_to_client = None
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

