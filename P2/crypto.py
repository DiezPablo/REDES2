"""
Modulo crypto.py
Su utilidad es gestionar todo el cifrado y descifrado de ficheros del programa.
Realizado por:
    - Andres Barbero Valentin
    - Pablo Diez del Pozo
    - Grupo 2311
"""

from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad
from Crypto.Util.Padding import unpad
from Crypto.Hash import SHA256
from Crypto.Signature import pkcs1_15
from Crypto.Cipher import PKCS1_OAEP

# Definciones de tamaño de las claves utilizadas para cifrar y firmar los ficheros. Tambien hay longitudes de las claves
# utilizadas para descifrar.
RSA_TAM = 2048
VECTOR_IV_TAM = 16
AES_KEY_TAM = 32
KEY_RSA_TAM = 256
SIGN_TAM = 256



def generate_rsa():
    """
    Esta funcion genera el par de claves publica y privada generado por RSA para el usuario de SecureBox Client.
    Guarda cada una de las claves en un fichero .pem.
    """
    # Geneamos la pareja de claves
    key = RSA.generate(RSA_TAM)

    # Exportamos la clave privada
    private_key = key.exportKey('PEM')

    # Escribimos la clave en un fichero
    with open("private.pem","wb") as f:
        f.write(private_key)

    # Generamos la clave publica
    public_key = key.publickey().exportKey('PEM')

    # Escribimos la clave en un fichero
    with open("public.pem", "wb") as f:
        f.write(public_key)

    f.close()

def get_public_key():
    """
    Getter de la clave publica del usuario. Leemos el fichero y lo exportamos para que pueda ser utilizado por otras funciones.

    :return: clave pública exportada utilizando el formato "OpenSSH".
    """
    f = open('public.pem', 'rb')
    key = RSA.import_key(f.read())
    f.close()
    return key.export_key('OpenSSH')


def sign(file):
    """
    Firma el fichero que recibe como argumento utilizando el algoritmo SHA256.
    :param file: Fichero que se quiere firmar.
    :return: firma y el contenido del fichero concatenado.
    """
    if file == None:
        return

    # Ciframos el hash del mensaje con la clave privada del emisor
    # Obtenemos la clave privada del emisor
    key = RSA.import_key(open('private.pem').read())

    # Leemos el fichero con el mensaje a cifrar
    with open(file, "rb") as f:
        file_content = f.read()

    #Convertimos a
    h = SHA256.new(file_content)
    signature = pkcs1_15.new(key).sign(h)

    # Para ahora firmar con AES necesitamos la firma + el contenido del fichero
    # content_and_sign = "sign+content_" +file
    # with open(content_and_sign,'wb') as f_out:
    #     f_out.write(signature)
    #     f_out.write(file_content)

    # Devolvemos el nombre del fichero firmado para proceder al cifrado AES
    # return str(content_and_sign)
    return signature +file_content

def encrypt(file, public_key_receiver):
    """
    Función que se encarga de cifrar el contenido del fichero que posteriormente se va a transmitir por la red, utilizando
    el algoritmo simétrico de cifrado AES. También se cifrará la clave de sesión con RSA utilizando la clave pública
    del receptor del mensaje, aportando confidencialidad y que solamente el pueda descifrarla.
    :param file: Fichero a cifrar
    :param public_key_receiver: Clave pública del receptor del fichero, se cifrará con RSA para que posteriormente solo
    el pueda descifrar el fichero.
    :return: devuelve el vector de inicializacion concatenado con la clave AES cifrada con RSA y el contenido cifrado con AES.
    """

    # Definimos el vector de inicializacion, de 16 bytes y la clave de 256.
    ini_vector = get_random_bytes(VECTOR_IV_TAM)
    random_key = get_random_bytes(AES_KEY_TAM)

    # Ciframos la clave AES
    cipher = AES.new(random_key,AES.MODE_CBC,ini_vector)

    # Alineamos en bloques de 16
    content_padded = pad(file,16)

    #Ciframos los bloques
    ciphered_content = cipher.encrypt(content_padded)

    # Cifrar clave publica receptor.
    cipher_key_RSA = PKCS1_OAEP.new(RSA.import_key(public_key_receiver))

    # Ciframos utilizando la clave AES
    ciphered_key_receiver = cipher_key_RSA.encrypt(random_key)

    ciphered_file = 'ciphered'
    with open(ciphered_file,'wb') as f_out:
        f_out.write(ini_vector)
        f_out.write(ciphered_key_receiver)
        f_out.write(ciphered_content)

    # Devolvemos un fichero cifrado listo para transmitir.
    return ini_vector +ciphered_key_receiver +ciphered_content

# -- enc_sign
def encrypt_and_sign(file, public_key_receiver):
    """
    Función que firma y cifra el fichero utilizando las funciones sign() y encrypt() y genera el fichero que va a ser
    enviado finalmente.
    :param file: Fichero a cifrar y transmitir por la red
    :param public_key_receiver: Clave publica del recepetor del fichero, para que solamente el pueda leerlo
    :return: Fichero cifrado por completo juntando ambas funciones de sign() y encrypt()
    """

    # Obtenemos la extension del fichero que va a ser subido
    filename = file
    ext = filename.split(".")[1]

    # Llamada a firmar
    file_to_encrypt = sign(file)

    # Ciframos el fichero que se quiere transmitir
    file_to_send = encrypt(file_to_encrypt,public_key_receiver)

    # Devolvemos el fichero cifrado y firmado
    f = "file_to_send." +ext
    with open(f,'wb') as f_out:
        f_out.write(file_to_send)

    return f

def decrypt(file,public_key_receiver):
    """
    Esta funcion se encarga del descifrado del fichero que recibe como parametro. Para ello, se separan los campos en los
    que viene divido el fichero, primero el IV, luego la clave de AES(clave de sesion) y por ultimo el contenido con
    la firma. Utilizando la clave privada del receptor se descifra la clave de sesion, se descifra el contenido con
    la clave de sesion y luego se genera el hash del mensaje para comprobar que la firma y el hash del mensaje coinciden.
    :param file: Fichero a descifrar
    :param public_key_receiver: clave publica del receptor.
    :return: Si todo va bien se obtiene el fichero descifrado, en caso contrario una excepcion que informa de que la
    firma no coincide
    """
    if file == None:
        return None

    # Lectura del fichero a descifrar
    with open(file,'rb') as f:
        file_content = f.read()

    # Abrir el sobre para poder leer el mensaje.
    # El mensaje recibido tiene la siguiente composicion: IV -> 16 bits, KEY -> 256 bits, el resto es firmas+mensaje.
    ini_vector = file_content[0:VECTOR_IV_TAM]
    key_receiver = file_content[VECTOR_IV_TAM:KEY_RSA_TAM+VECTOR_IV_TAM]
    sign_and_content = file_content[KEY_RSA_TAM+VECTOR_IV_TAM:]

    # Obtenemos la clave privada del receptor
    private_key = RSA.import_key(open('private.pem', 'r').read())

    # Desciframos la clave de sesion
    cipher_sesion = PKCS1_OAEP.new(private_key)
    key_session = cipher_sesion.decrypt(key_receiver)

    # Descifrar el contenido para posteriormente validar la firma
    aes_decrypt = AES.new(key_session,AES.MODE_CBC,ini_vector)
    content_padded = aes_decrypt.decrypt(sign_and_content)
    content = unpad(content_padded,16)

    # Cogemos la firma del contenido ya descifrado y comprobamos que es correcta.
    sign = content[0:SIGN_TAM]
    content_info_decrypted = content[SIGN_TAM:]

    # Obtenemos el hash
    content_hash = SHA256.new(content_info_decrypted)
    key_signer = RSA.import_key(public_key_receiver)

    try:
        pkcs1_15.new(key_signer).verify(content_hash,sign)

    except (ValueError, TypeError):
        print("Error en la firma. No coinciden")
        return

    # Si todo va bien imprimos el fichero descifrado

    with open("decrypted_"+file, 'wb') as f_out:
        f_out.write(content_info_decrypted)

    return





