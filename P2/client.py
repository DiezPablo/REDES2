"""
Modulo client.py
Su utilidad es gestionar el sistema, aglutinando toda la funcionalidad de ficheros, usuarios y cifrado y descifrado de
ficheros.
Realizado por:
    - Andres Barbero Valentin
    - Pablo Diez del Pozo
    - Grupo 2311
"""

import crypto
import files
import users
import sys
import argparse

# Token para el usuario DiezPablo
token = '624fbD71C0FBcd3e'


def main():
    """
    Main que gestiona todo el funcionamiento del sistema.
    :return:
    """
    # Creamos un parser para los argumentos de entrada del programa
    parser = argparse.ArgumentParser(description = "Cliente SecureBox")

    # Ayuda

    # Gestion de usuarios
    parser.add_argument("--create_id", nargs = 2, metavar = ('name','email'))
    parser.add_argument("--search_id",nargs = 1, metavar = ('data'))
    parser.add_argument("--delete_id",nargs = 1, metavar = ('user_id'))

    # Gestion de ficheros
    parser.add_argument("--upload", nargs = 1, metavar = ('file'))
    parser.add_argument("--source_id", nargs = 1, metavar = ('user_id'))
    parser.add_argument("--dest_id", nargs = 1, metavar = ('user_id'))
    parser.add_argument("--list_files", action='store_true')
    parser.add_argument("--download", nargs = 1, metavar = ('file_id'))
    parser.add_argument("--delete_file", nargs = 1, metavar = ('file_id'))

    # Gestion del cifrado y firmado de documentos
    parser.add_argument("--encrypt", nargs = 1, metavar = ('file'))
    parser.add_argument("--sign", nargs = 1, metavar = ('file'))
    parser.add_argument("--enc_sign", nargs = 1, metavar = ('file'))

    # Se parsean los argumentos
    args = parser.parse_args()



    # Si no se encuentan los parametros suficientes
    if len(sys.argv) < 2:
        print("Se necesitan mas argumentos de entrada para ejecutar el programa.")
        print("Si necesita ayuda ejecute el programa con la flag --help")
        return

    # Gestion de usuarios
    if args.create_id:
        users.register_user(name = args.create_id[0], email = args.create_id[1],token = token)
    elif args.search_id:
        users.search_user(data_search = args.search_id[0], token = token)
    elif args.delete_id:
        users.delete_user(user_id = args.delete_id[0],token = token)

    # Gestion de cifrado y firmado
    elif args.encrypt and args.dest_id:
        key = users.get_public_key(user_id = args.dest_id[0],token = token)
        crypto.encrypt(file = args.encrypt[0],public_key_receiver = key)
    elif args.sign:
        crypto.sign(file = args.sign[0])
    elif args.enc_sign and args.dest_id:
        key = users.get_public_key(user_id = args.dest_id[0], token = token)
        crypto.encrypt_and_sign(file = args.enc_sign[0], public_key_receiver = key)

    # Gestion de ficheros
    elif args.upload and args.dest_id:
        key = users.get_public_key(user_id = args.dest_id[0], token = token)
        files.upload_file(file=args.upload[0], public_key_dest=key, token = token)
    elif args.list_files:
        files.list_files(token = token)
    elif args.download and args.source_id:
        key = users.get_public_key(user_id = args.source_id[0],token = token)
        files.download_file(file_id = args.download[0], public_key_receiver = key, token = token)
    elif args.delete_file:
        files.delete_file(file_id = args.delete_file[0], token = token)
    else:
        print("Comando no soportado")
        print("Revise con el comando --help los comandos que puede ejecutar el cliente SecureBox.")

if __name__ == "__main__":
    main()
