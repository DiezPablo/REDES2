# import the library
import connection_control
from appJar import gui
from PIL import Image, ImageTk
import numpy as np
import cv2
import discover_server
import copy
import threading

class VideoClient(object):
	"""
	Clas VideoClient, que implementa gran parte de la funcionalidad de la interfaz grafica de la aplicacion.
	"""
	def __init__(self, window_size):
		"""
		Funcion de inicializacion de la clase VideoClient, en ella se inicializa la pantalla de registro del usuario.
		:param window_size: tamaño de la ventana de la interfaz que se crea.
		"""
		# Creamos una variable que contenga el GUI principal
		self.app = gui("Redes2 - P2P", window_size)
		self.app.setGuiPadding(10,10)

		# Añadios etiquetas para que se introduzcan los datos de registro
		self.app.addLabelEntry("Nick")
		self.app.addLabelEntry("Password")
		self.app.addLabelEntry("Puerto")
		self.app.addLabelEntry("Protocolo")

		# Boton que recoge la informacion anterior
		self.app.addButton("Iniciar sesion",self.buttonsCallback)

	def start(self):
		"""
		Funcion de inicio de la clase VideoClient
		:return:
		"""
		# Inicio de la aplicacion
		self.app.go()

	def application(self):
		"""
		Funcion aplicacion, que esconde los botones de registro y permite listar, buscar y conectarse a otros usuarios.
		:return:
		"""
		# Preparación del interfaz, escondemos los botones anteriores
		self.app.hideButton("Iniciar sesion")
		self.app.hideLabel("Nick")
		self.app.hideLabel("Protocolo")
		self.app.hideLabel("Password")
		self.app.hideLabel("Puerto")

		msg = "Redes2 - P2P - " +discover_server.user_read_file()['nick']
		self.app.addLabel("title", msg)

		# Añadimos una imagen
		self.app.addImage("video", "imgs/webcam.gif")

		# Añadir los botones
		self.app.addButtons(["Conectar", "Listar usuarios", "Buscar usuario", "Salir"], self.buttonsCallback)

	# Establece la resolución de la imagen capturada
	def setImageResolution(self, resolution):
		# Se establece la resolución de captura de la webcam
		# Puede añadirse algún valor superior si la cámara lo permite
		# pero no modificar estos
		if resolution == "LOW":
			self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 160)
			self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 120)
		elif resolution == "MEDIUM":
			self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
			self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
		elif resolution == "HIGH":
			self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
			self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

	# Función que gestiona los callbacks de los botones
	def buttonsCallback(self, button):
		"""
		Funcion que define los callbacks de los botones de la clase VideoClient.
		:param button: boton seleccionado por el usuario en la interfaz grafica
		"""
		if button == "Salir":
			# Salimos de la aplicación
			self.app.stop()
		elif button == "Conectar":
			# Entrada del nick del usuario a conectar
			nick = self.app.textBox("Conexión", "Introduce el nick del usuario a buscar")

			# Con el nick anterior se busca al usuario
			user_dest = discover_server.query_user(nick)

			# Si no se encuentra sale un mensaje
			if user_dest == None:
				self.app.errorBox("Fallo usuario","No existe el usuario buscado")
			else:
				# Si se encuentra lo llamamos
				connection_control.call(self, user_dest)

		# Listamos los usuarios de la aplicacion
		elif button == "Listar usuarios":
			users = discover_server.list_users()
			self.app.infoBox("Usuarios en el sistema", users)

		# Busqueda de un usuario en la aplicacion
		elif button == "Buscar usuario":
			# Introducimos el nick del usuario que queremos buscar
			nick = self.app.textBox("Busqueda","Introduzca el usuario a buscar")

			# Lo buscamos
			user = discover_server.query_user(nick)

			# Si no se encuentra sale un mensaje de error
			if user == None:
				self.app.errorBox("Usuario no encontrado", "No existe el usuario con nick: " +nick)
			else:
				# Si se encuentra, lo mostramos con toda su informacion en el servidor de descubrimiento
				msg = " - Nick: " +user['nick'] +"\n - Ip: " +user['ip'] +"\n - Port: " +user['port'] +"\n - Protocol: " +user['protocol']
				self.app.infoBox("Usuario encontrado",msg)

		# Caso de inicio de sesion en la aplicacion
		elif button == "Iniciar sesion":

			# Rellenamos todos los campos necesarios
			nick = self.app.getEntry("Nick")
			password = self.app.getEntry("Password")
			port = self.app.getEntry("Puerto")
			protocol = self.app.getEntry("Protocolo")

			# Llamada a la funcion del servidor de descubrimiento que gestiona los registros
			user = discover_server.register_user(nick,port,password,protocol)

			if 	user == "ERROR":
				self.app.errorBox("Inicio de sesion","No ha sido posible iniciar sesion")
			else:
				# Buscamos el usuario para obtener todos sus datos.
				user = discover_server.query_user(nick)

				# Escribimos en un fichero el usuario con el que nos hemos registrado para tenerlo siempre.
				discover_server.user_write_file(user)

				# Iniciamos el thread de escucha de conexiones TCP al que se haran las peticiones
				listen_thread = threading.Thread(target=connection_control.listen, args=(self,),
												 daemon=False)

				# Comenzamos el thread de escucha
				listen_thread.start()

				# Llamamos a la funcion aplicacion que permite usar el sistema
				self.application()



if __name__ == '__main__':

	vc = VideoClient("640x520")

	# Crear aquí los threads de lectura, de recepción y,
	# en general, todo el código de inicialización que sea necesario
	# ...


	# Lanza el bucle principal del GUI
	# El control ya NO vuelve de esta función, por lo que todas las
	# acciones deberán ser gestionadas desde callbacks y threads
	vc.start()
