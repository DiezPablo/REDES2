#ifndef DEMONIZAR_H
#define DEMONIZAR_H

/**
* Descripcion: Fichero cabecera modulo demonizar.
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
#include "demonizar.h"
#include <fcntl.h>

/**
 * Funcion demonizar
 *
 * DESCRIPCION:
 *       Funcion que demoniza un proceso siguiendo los pasos del manual de la practica.
 *
 * INPUT:
 *       servicio: char* Identifica por medio de una cadena de caracteres el servicio.
 *
 * OUTPUT:
 *      0 si es correto.
 *     -1 si no es correcto.
 */
int demonizar(char* servicio);

#endif /* DEMONIZAR_H */
