#ifndef SOCKET_H
#define SOCKET_H

/**
* Descripcion: Fichero cabecera modulo sockets.
*
* Autores: Pablo Diez del Pozo y Andres Barbero Valentin.
*
* Grupo: 2311
*
*/


#include <unistd.h>
#include <syslog.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>


/**
* Funcion inicializa_server
*
* DESCRIPCION:
*       Apertura de socket del servidor, asociacion del puerto y preparado para escuchar.
*
* INPUT:
*       puerto: int Puerto al que se asocia el socket
*       conexiones_max: int Numero maximo de conexiones al socket
*
* OUTPUT:
*      sockval: int retorno de la funcion socket()
*     -1 si no es correcto
*/
int inicializa_server(int puerto, int conexiones_max);


/**
* Funcion aceptar_conexion
*
* DESCRIPCION:
*       Funcion que establece la conexion con el socket.
*
* INPUT:
*       sockval: int Socket al que queremos aceptar la conexion.
*
* OUTPUT:
*      socket_client: int Descriptor de la conexion establecida.
*     -1 si no es correcto
*/
int aceptar_conexion(int sockval);

#endif /* SOCKET_H */
