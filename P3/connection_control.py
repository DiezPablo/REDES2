import socket
import discover_server
from video_UDP import Video_UDP

global stream_on
stream_on = False

RECV_SIZE = 1024

def call(gui, user_dest):
    """
    Funcion que se encarga de llamar a otro usuario creando un socket TCP
    conectandose a el. Tambien espera por la respuesta a este comando CALLING.
    :param gui: Objeto de la interfaz grafica
    :param user_dest: usuario destino de la llamada
    :return: OK si todo va correctamente.
    """
    # Obtenemos nuestro usuario
    user = discover_server.user_read_file()

    # Definimos el mensaje que se le va a mandar para establecer la llamada
    msg = "CALLING " +user['nick'] +" " +str(user['udp_port'])

    # Mandamos el mensaje y obtenemos la respuesta
    # Conexion TCP con la otra maquina para mandar mensajes
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Creamos el par IP puerto para conectarnos.
    server_address = (user_dest['ip'],int(user_dest['port']))

    # Nos conectamos a la otra maquina
    sock.connect(server_address)

    # Mandamos el mensaje a traves del socket.
    sock.send(msg.encode())
    response = sock.recv(RECV_SIZE).decode()
    sock.close()

    # Dividimos la respuesta
    response_splitted = response.split(" ")

    # Caso llamada denegada
    if response_splitted[0] == "CALL_DENIED":
        gui.app.infoBox("Llamada","Llamada denegada")
        return None

    #Caso el otro usuario en llamada
    elif response_splitted[0] == "CALL_BUSY":
        gui.app.infoBox("Llamada","Usuario en otra llamada")
        return None
    elif response_splitted[0] == "CALL_ACCEPTED":
        # Se nos mandan los parametros del usuario
        # Lo buscamos y escribimos el fichero que nos va a permitir tenenrlo siempre disponible.
        user_dest = discover_server.query_user(response_splitted[1])
        discover_server.user_dest_write(user_dest,response_splitted[2])

        # Iniciamos la gui del streaming
        video_UDP = Video_UDP(gui)
        video_UDP.start()

        return "OK"

    return "OK"

def listen(gui):
    """
    Funcion que deja un socket abierto escuchando en su IP y puerto TCP para recibir comandos utilies para la
    comunicacion entre nuestro usuario y el usuario de la llamada
    :param gui: Objeto de la interfaz grafica
    :return: OK si todo va correctamente. None en caso contrario
    """
    # Abrimos un socket de escucha TCP para que puedan conectarse a el otros equipos
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    user = discover_server.user_read_file()

    # Creamos la direccion en la que vamos a registrar el servidor
    server_address = ((user['ip'],int(user['port'])))

    sock.bind(server_address)

    # Fijamos el tamanio de la cola de escucha del servidor
    sock.listen(1)

    # Aceptamos conexiones
    conn, address = sock.accept()

    # Aceptamos las peticiones en bucle
    while(1):
        # Recibimos peticiones
        petition = conn.recv(1024)

        # Formateamos la peticion que recibimos
        petition_splitted = petition.decode().split(" ")
        if petition_splitted[0] == "CALLING":

            # Estamos recibiendo una llamada, respndemos con si o no
            call_accepted = gui.app.yesNoBox("Llamada","El usuario " +petition_splitted[1] +" nos esta llamando. ¿Aceptar?")
            if call_accepted == False:
                # Mandamos un call denied si la respuesta es No
                msg = "CALL_DENIED " +user['nick']
                conn.sendall(msg.encode())
            else:
                # Mandamos un CALL_ACCEPTED si queremos conectarnos
                msg = "CALL_ACCEPTED " +user['nick'] +" " +user['udp_port']
                conn.sendall(msg.encode())

                # Buscamos al usuario y guardamos sus datos en un fichero user_dest para poder acceder cuando queramos
                user_dest = discover_server.query_user(petition_splitted[1])
                discover_server.user_dest_write(user_dest,petition_splitted[2])

                # Iniciamos la conexion UDP para el streaming
                video_UDP = Video_UDP(gui)
                video_UDP.start()

                return "OK"

        # Caso en el que el otro usurio se encuentra ocupado en otra llamada
        elif petition_splitted[0] == "CALL_BUSY":
            gui.app.infoBox("Llamada","El usuario se encuentra en llamada.")
            return None
        # Caso en el que el usuario quiere terminar la llamada
        elif petition_splitted[0] == "CALL_END":
            # Se pone la variable que gestiona si el stream esta activo a false
            stream_on = False
            gui.app.infoBox("Llamada","El usuario quiere terminar la llamada.")
            return None
        else:
            # Caso en el que el usuario haga un CALL_DENIED
            gui.app.infoBox("Llamada", "El usuario ha rechazado la llamada.")
            return None

    # Se cierra la conexion
    conn.close()

    return "OK"
