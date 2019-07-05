import socket
import sys

# Ip a la que nos conectamos
ip="192.168.1.40"

server_address = ("vega.ii.uam.es",8000) # Url del servidor de descubrimiento
udp_port = 9999

REGISTER_RESPONSE = 2048
USERS_BEGIN_SIZE = 16

def connect_DS():
    """
    Funcion que establece un socket con el servidor de descubrimiento
    :return: Devuelve el socket que se crea al establecer la conexion
    """
    # Creamos un socket para conectarnos a la direccion del servidor
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    sock.connect(server_address)

    # Devolvemos el socket para mandar mensajes una vez establecida la conexion
    return sock

def register_user (nick, port, password, protocol):
    """
    Funcion que se encarga de crear un nuevo usuario en el servidor de descubrimiento.
    :param nick: Nick del usuario a crear.
    :param port: Puerto tcp en el que se encuentra el usuario escuchando.
    :param password: Password para acceder al sistema.
    :param protocol: Protocolo implementado.
    :return: OK si todo funciona correctamente, ERROR en caso contrario.
    """
    # C.d.E
    if ((nick == None) | (port == None) | (password == None) | (protocol == None)):
        return "ERROR"


    # Llamamos a la funcion que se conecta al servidor de descubrimiento
    sock = connect_DS()

    # Componemos el mensaje
    msg = 'REGISTER ' + nick + ' ' +ip + ' ' + str(port) + ' ' + password + ' ' + protocol

    # Mandamos el register
    sock.sendall(msg.encode())

    # Recibimos la respuesta, si da error lo devolvemos y si un OK
    data = sock.recv(REGISTER_RESPONSE)
    if data.decode() == "NOK WRONG_PASS":
        return "ERROR"
    else:
        return "OK"

    return "ERROR"

def query_user(nick):
    """
    Funcion que busca a un usuario en el servidor de descubrimiento utilizando el nick como parametro.
    :param nick: Nick del usuario que queremos buscar
    :return: diccionario con todos los campos del usuario buscado. None en caso de que no se encuentre en el sistema
    """
    # Componemos el mensaje
    msg = 'QUERY ' + nick

    # Conexion al servidor de descubrimiento
    sock = connect_DS()

    # Mandamos el query al servidor
    sock.sendall(msg.encode())

    # Recibimos la respuesta del servidor
    data = sock.recv(REGISTER_RESPONSE)

    # Formateamos la devolucion con los espacios
    data_splitted = data.decode().split(' ')

    # Almacenamos el usuario en un diccionario y lo devolvemos
    if data_splitted[0] == "OK":
        dict ={}
        dict['nick'] = data_splitted[2]
        dict['ip'] = data_splitted[3]
        dict['port'] = data_splitted[4]
        dict['protocol'] = data_splitted[5]

        return dict

    # en caso de error
    return None

def list_users():
    """
    Lista a todos los usuarios del sistema.
    :return: Lista con todos los usuarios que tiene el sistema.
    """
    # Componemos el mensaje
    msg = 'LIST_USERS'

    # Nos conectamos al servidor
    sock = connect_DS()

    # Mandamos el register
    sock.sendall(msg.encode())

    # Recibimos la respuesta
    data = sock.recv(REGISTER_RESPONSE)
    users_data = data[USERS_BEGIN_SIZE:]

    # Formateamos la respuesta
    users = users_data.decode().split("#")

    users_list=""

    #Añadimos todos los usuarios a una lista
    for item in users:
        users_list += item +"\n"

    return users_list


def quit_server():
    """
    Manda un comando QUIT para cerrar la conexion establecida con el servidor de descubrimiento
    :return: no devuelve nada
    """
    # Componemos el mensaje
    msg = "QUIT"

    # Nos conectamos al servidor de descubrimiento
    sock = connect_DS()

    # Llamamos al servidor
    sock.sendall(msg.encode())
    data = sock.recv(REGISTER_RESPONSE)

    print(data.decode())
    # Cerramos la conexion
    sock.close()

def user_write_file(user):
    """
    Escribe en un fichero el usuario que se encuentra utilizando la aplicacion para tenerlo siempre.
    :param user: Usuario que queremos guardar en el fichero
    :return:
    """
    # Buscamos al usuario
    user_queried = query_user(user['nick'])

    if user == None:
        return "ERROR"

    # Escribimos sus datos en un fichero
    file = open("user.txt","w+")
    file.write("Nick: " +user_queried['nick'] +"\n")
    file.write("Ip: " + user_queried['ip'] + "\n")
    file.write("Port: " + user_queried['port'] + "\n")
    file.write("Protocol: " + user_queried['protocol'] +"\n")
    file.write("Port_udp: " +str(udp_port))

    # Cerramso el fichero
    file.close()

def user_read_file():

    """
    Funcion de lectura del fichero del usuario que usa la aplicacion.
    :return: Diccionario con todos los campos del fichero rellenado
    """
    user = {}
    file = open("user.txt", "r")

    # Leemos el fichero de usuario
    readed = file.read()

    # Formateamos la lectura y lo almacenamos en un diccionario
    lines = readed.split("\n")
    user['nick'] = lines[0].split(" ")[1]
    user['ip'] = lines[1].split(" ")[1]
    user['port'] = lines[2].split(" ")[1]
    user['protocol'] = lines[3].split(" ")[1]
    user['udp_port'] = lines[4].split(" ")[1]

    # Cerramos el fichero
    file.close()

    # Deolvemos el usuario
    return user

def user_dest_write(user,udp_dest_port):
    """
    Funcion que escribe un fichero toda la informacion del usuario con el que se establece el streaming. Incluido
    su puerto udp.
    :param user: Usuario destino del streaming
    :param udp_dest_port: Puerto udp al que se mandaran los paquetes.
    :return:
    """
    # C.d.E
    if user == None:
        return "ERROR"

    # Buscamos al usuario destino de la llamada
    user_dest_queried = query_user(user['nick'])

    # Abrimos un fichero y escribimos la devolucion de la query en él
    file = open("user_dest.txt", "w+")
    file.write("Nick: " + user_dest_queried['nick'] + "\n")
    file.write("Ip: " + user_dest_queried['ip'] + "\n")
    file.write("Port: " + user_dest_queried['port'] + "\n")
    file.write("Protocol: " + user_dest_queried['protocol'] + "\n")
    file.write("Port_udp_dest: " + str(udp_dest_port))

    # Cerramos el fichero
    file.close()

def user_dest_read():
    """
    Funcion de lectura del fichero del usuario con el que se establece el streaming.
    :return: Diccionario con todos los campos del fichero rellenados.
    """
    user_dest = {}

    # Leemos el fichero que guarda al usuario destino de la llamada
    file = open("user_dest.txt", "r")

    readed = file.read()

    # Formateamos la salida
    lines = readed.split("\n")

    # Lo almacenamos en un diccionario
    user_dest['nick'] = lines[0].split(" ")[1]
    user_dest['ip'] = lines[1].split(" ")[1]
    user_dest['port'] = lines[2].split(" ")[1]
    user_dest['protocol'] = lines[3].split(" ")[1]
    user_dest['udp_port_dest'] = lines[4].split(" ")[1]


    # Cerramos el fichero
    file.close()

    # Devolvemos el usuario
    return user_dest
