"""
Modulo files.py
Su utilidad es gestionar la subida, bajada, borrado y listado de ficheros que hay en el sistema.
Realizado por:
    - Andres Barbero Valentin
    - Pablo Diez del Pozo
    - Grupo 2311
"""

import users
import requests
import crypto

URL_API_FILES = "http://vega.ii.uam.es:8080/api/files"

def upload_file(file, public_key_dest,token):
    """
    Funcion que permite subir un fichero a la API del sistema. También se encarga de cifrar el fichero utilizando el
    modulo crypto.py y utilizando la clave publica del destinatario lo cifra solo para el.
    :param file: Fichero que deseamos subir, sin cifrar.
    :param public_key_dest: Clave publica del destinatario del fichero.
    :param token: Token que permite autenticarnos en la API donde se suben los ficheros.
    :return: Informacion sobre la subida del fichero, si ha sido correcta o no.
    """
    if file == None:
        return None

    # Ciframos el contenido del ficheor que queremos subir al servidor
    file_encrypted = crypto.encrypt_and_sign(file, public_key_dest)

    # Construimos la ruta y los argumentos para la llamada a la API. En este caso no hay JSON
    url = URL_API_FILES +'/upload'
    header = {
        'Authorization': 'Bearer ' +token,
    }

    f = open(file_encrypted,'rb')

    # Llamamos a la API con el fichero que se quiere subir
    response = requests.post(url,headers=header, files={'ufile' : f})
    if response.status_code == 403:
        print(response.json()['description'])
    else:
        print("Subida correcta del fichero. ID: "+response.json()['file_id'])

def list_files(token):
    """
    Lista los fichero que hay dirigidos a nosotros en el sistema.
    :param token: Token de autenticacion en la API.
    :return: Lista los ficheros que hay dirigidos a nosotros en la pantalla.
    """
    # Construimos los argumentos para la llamada a la API
    url = URL_API_FILES +'/list'
    header = {
        'Authorization': 'Bearer ' + token,
    }

    # Llamada a la API y recogemos la respuesta
    response = requests.post(url, headers=header)

    # Imprimimos la respuesta
    print("Numero de ficheros del usuario: " +str(response.json()['num_files']))
    for fichero in response.json()['files_list']:
        print("\t - Nombre del fichero: "+fichero['fileName'] +" con ID: "+fichero['fileID'])

def delete_file(file_id, token):
    """
    Elimina un fichero utilizando su id del sistema.
    :param file_id: Id del fichero a eliminar.
    :param token: Token de autenticacion en la API.
    :return: Informacion sobre si el borrado ha sido correcto o no.
    """
    # Contruimos los argumentos para la peticion
    url = URL_API_FILES +'/delete'
    header = {
        'Authorization': 'Bearer ' + token,
    }
    args = {
        'file_id': file_id, }

    # Llamada a la API
    response = requests.post(url, headers = header, json = args)

    # Tratamos la respuesta
    if response.status_code == 401:
        print(response.json()['description'])
    else:
        print("Se ha borrado el fichero con ID: "+response.json()['file_id'])

def download_file(file_id, public_key_receiver, token):
    """
    Funcion que gestiona la descarga de un fichero y lo descifra utilizando la función de decrypt() y la clave publica
    del receptor.
    :param file_id: Id del fichero a descargar.
    :param public_key_receiver: Clave publica del receptor del fichero
    :param token: Token de autenticacion en la API.
    :return: Informacion sobre el proceso de descarga y descifrado del fichero, si ha sido correcto o no.
    """
    url = URL_API_FILES + '/download'
    header = {
        'Authorization': 'Bearer ' + token,
    }
    args = {
        'file_id': file_id, }

    # Llamada a la API
    response = requests.post(url, headers=header, json=args)

    # Tratamos la respuesta
    if response.status_code == 401:
        print(response.json()['description'])
    else:
        print("Se ha descargado el fichero con ID: " +file_id)

        # Cogemos la extension
        content_disposition = response.headers['Content-Disposition']
        ext = content_disposition.split(".")[1]
        # Creamos un fichero para pasarselo a la funcion decrypt
        file = "file_downloaded_" +file_id +"." +ext[:-1]
        with open(file,"wb") as f:
            f.write(response.content)

        crypto.decrypt(file, public_key_receiver)

        print("Se ha descifrado su contenido correctamente.")