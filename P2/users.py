"""
Modulo users.py
Su utilidad es gestionar la creacion, busqueda y borrado de usuarios del sistema.
Realizado por:
    - Andres Barbero Valentin
    - Pablo Diez del Pozo
    - Grupo 2311
"""

import requests
import crypto
import json
import time


URL_API_USERS = "http://vega.ii.uam.es:8080/api/users"

# --create_id
def register_user(name, email, token):

    # Generamos las claves para el nuevo usuario
    crypto.generate_rsa()

    # Obtenemos la clave publica
    public_key = crypto.get_public_key()

    # Completamos todos lo campos necesarios para realizar la solicitud
    url = URL_API_USERS +"/register"
    header = {
        'Authorization': 'Bearer ' +token,
    }
    args = {
        'nombre': name,
        'email': email,
        'publicKey': public_key.decode('utf-8'),
    }

    # Llamada a la API con los datos que hemos completado para crear el usuario.
    response = requests.post(url, headers=header, json=args)

    # No hay caso de fallo. La llamada a la API siempre devuelve HTTP 200
    print("Identidad creada con los siguientes datos:")
    print("\t - Nombre: " + response.json()['nombre'])
    print("\t - Email: " +email)
    print("\t - Fecha creacion: " + time.strftime("%D %H:%M",time.localtime(response.json()['ts'])))

# --search_id
def search_user(data_search,token):

    # Rellenamos los campos necesarios para la solicitud
    url = URL_API_USERS + "/search"
    header = {
        'Authorization': 'Bearer ' + token,
    }
    args = {
        'data_search':data_search,}

    # Llamada a la API. HTTP 401 Caso Error. 200 caso OK. Solo devuelve esos dos codigos
    # Aunque no exista usuario para la busqueda se devuelve 200 siempre.
    response = requests.post(url, headers=header, json=args)
    if response.status_code == 401:
        print(response.json()['description'])

    # Hay que ver la lista de usuarios que coincidan con lo buscado en el sistema
    else:
        if len(response.json()) == 0:
            print ("Usuario no encontrado para el dato: "+data_search)
        else:
            print("Usuarios encontrados: " +str(len(response.json())))
            count = 1
            for item in response.json():
                print("\t[" +str(count) +"] " +str(item['nombre']) +", " +str(item['email']) +", ID: " +str(item['userID']))
                count += 1

def get_public_key(user_id, token):

    # Componemos los campos necesarios para la request
    url = URL_API_USERS + "/getPublicKey"
    header = {
        'Authorization': 'Bearer ' + token,
    }
    args = {
        'userID': user_id, }

    # Llamada a la API.
    response = requests.post(url, headers=header, json=args)
    if response.status_code == 401:
        print(response.json()['description'])
    else:
        return response.json()['publicKey']

# --delete_user
def delete_user(user_id, token):
    url = URL_API_USERS + "/delete"
    header = {
        'Authorization': 'Bearer ' + token,
    }
    args = {
        'userID': user_id, }

    # Llamada a la API.
    response = requests.post(url, headers=header, json=args)
    print("Borrado usuario con id "+str(response.json()['userID']))

