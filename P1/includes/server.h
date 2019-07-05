/**
* Descripcion: Fichero cabecera modulo server.
*
* Autores: Pablo Diez del Pozo y Andres Barbero Valentin.
*
* Grupo: 2311
*
*/

#include "sockets.h"
#include <pthread.h>
#include "picohttpparser.h"
#include <assert.h>
#include <string.h>
#include <time.h>
#include "confuse.h"
#include <limits.h>
#include <fcntl.h>
#include "demonizar.h"
#include <sys/types.h>
#include <sys/wait.h>

