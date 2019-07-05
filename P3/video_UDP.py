import connection_control
import discover_server
import cv2
import socket
import numpy as np
from PIL import Image, ImageTk
import threading
import sys
import time

class Video_UDP(object):
    """
    Clase que contiene toda la funcionalidad del Streaming
    """
    def __init__(self, gui):
        """
        Funcion de inicializacion del objeto Video_UDP.
        :param gui: gui: objeto de la interfaz videoClient, necesario para completar su funcionalidad.
        """
        # Le pasamos un objeto interfaz grafica para tenerla.
        self.gui = gui.app
        self.gui.startSubWindow("Retransmision")
        self.gui.setGeometry(800,520)

        msg = "Redes2 - P2P - " +discover_server.user_read_file()['nick']
        self.gui.addLabel("subtitle", msg)

        # Imagen en la que se van a mostrar el video de nuestra camara y el del otro usuario
        self.gui.addImage("imagen_stream", "imgs/webcam.gif")

        # Captura de frames
        self.frame = cv2.VideoCapture(0)
        self.gui.setPollTime(20)

        # Variable que guarda el frame enviado en todo momento
        self.frame_sended = None

        # Definimos los fps
        self.fps = 25

        # Botones de la GUI del stream
        self.gui.addButtons(["STOP VIDEOCALL"],self.buttonsCallback)


    def start(self):
        """
        Inicializa la clase Video_UDP. Lanza los hilos de mandar y recibir video e inicializa el parametro que define
        si el streaming esta activo o no a TRUE.
        :return:
        """
        # Paramos la ventana anterior de la GUI y enseñamos la neuva
        self.gui.stopSubWindow()
        self.gui.showSubWindow("Retransmision")

        # Empezar el streaming de video
        connection_control.stream_on = True

        # Creamos los hilos, uno para mandar el video, otro para recibirlo
        self.thread1 = threading.Thread(target=self.send_video, args=(),daemon= False)
        self.thread1.start()
        self.thread2 = threading.Thread(target=self.receive_video, args=(),daemon=False)
        self.thread2.start()

    def buttonsCallback(self, button):
        """
        Callback de los botonos de la clase Video_UDP.
        :param button: boton que se pulsa en la interfaz
        :return:
        """
        # Leemos el fichero del usuario que usa la aplicacion y del usuario con el que establecemos el streaming.
        user = discover_server.user_read_file()
        user_dest = discover_server.user_dest_read()

        if button == "STOP VIDEOCALL":
            msg = "CALL_END " +user['nick']

            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Creamos el par IP puerto para conectarnos.
            server_address = (user_dest['ip'],int(user_dest['port']))
            # Nos conectamos a la otra maquina
            sock.connect(server_address)
            # Mandamos el mensaje a traves del socket.
            sock.send(msg.encode())
            sock.close()


            connection_control.stream_on = False
            print("STOP_VIDEOCALL : stream_on = " +str(connection_control.stream_on))
            self.gui.stopSubWindow()

    def send_video(self):
        """
        Funcion encargada de enviar frames de video al otro usuario. Se capturan estos frames, se empaquetan y se envian.
        Tambien se encarga de utilizar los FPS para mandar paquetes cada cierto tiempo de tal manera que se puede controlar
        la congestion.
        :return: devuelve OK al salir de ella.
        """
        # Leemos los ficheros de usuario y usuario destino
        user_dest = discover_server.user_dest_read()
        user = discover_server.user_read_file()

        # Creamos el socket UDP para mandar video
        sock = socket.socket(socket.AF_INET,  socket.SOCK_DGRAM)

        # Mientras la variable global streaming sea TRUE mandamos video
        while connection_control.stream_on == True:

            # Hacemos un sleep en funcion de los fps para mandar el frame cuando
            # tiene que reproducirse
            wait_time = float(1/self.fps)
            time.sleep(wait_time)

            # lectura del frame a enviar
            ret, img = self.frame.read()

            # Le hacemos un resize para modificar el tamaño
            img = cv2.resize(img,(160,120))
            self.frame_sended = cv2.resize(img, (160, 120))

            # Empaquetamos el frame
            encode_param = [cv2.IMWRITE_JPEG_QUALITY, 50]
            result, encimg = cv2.imencode('.jpg', img, encode_param)
            if result == False: print('Error al codificar imagen')
            encimg = encimg.tobytes()

            # Enviamos al socket udp el frame
            sock.sendto(encimg, (user_dest['ip'], int(user_dest['udp_port_dest'])))

        # Cerramos el socket una vez que sale del streaming
        sock.close()
        return "OK"

    def receive_video(self):
        """
        Funcion que se utiliza para recibir el video que nos manda el usuario al que estamos conectados. Se recibe,
        descomprime y muestra por la interfaz.
        :return: devuelve OK cuando termina.
        """
        # Leemos el fichero de nuestro usuario
        user = discover_server.user_read_file()

        # Recibe los frames del otro usuario
        sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        sock.bind((user['ip'],int(user['udp_port'])))

        while connection_control.stream_on == True:
            # Recibimos el frame
            data, addr = sock.recvfrom(60000)

            # Descomprimimos el frame
            decimg = cv2.imdecode(np.frombuffer(data,np.uint8), 1)

            # Mostrarlo por la gui
            if self.frame_sended is not None:

                # Lo mostramos en la gui, junto con nuestra camara en pequeño
                frame_base = cv2.resize(decimg,(640,480))
                frame_peque = self.frame_sended
                frame_compuesto = frame_base
                frame_compuesto[0:frame_peque.shape[0],0:frame_peque.shape[1]] = frame_peque

                cv2_im = cv2.cvtColor(frame_compuesto, cv2.COLOR_BGR2RGB)
                img_tk = ImageTk.PhotoImage(image=Image.fromarray(cv2_im))

                # Lo mostramos en el gui
                self.gui.setImageData("imagen_stream", img_tk, fmt='PhotoImage')

        # Cerramos el socket cuando termina el streaming
        sock.close()
        return "OK"
