#include "../includes/demonizar.h"


/**
* Descripcion: Fichero fuente modulo demonizar.
*
* Autores: Pablo Diez del Pozo y Andres Barbero Valentin.
*
* Grupo: 2311
*
*/



/**
 * Funcion demonizar
 *
 * DESCRIPCION:
 *       Funciono que demoniza un proceso siguiendo los pasos del manual de la practica.
 *
 * INPUT:
 *       servicio: char* Identifica por medio de una cadena de caracteres el servicio.
 *
 * OUTPUT:
 *      0 si es correto.
 *     -1 si no es correcto.
 */
int demonizar(char* servicio) {
    /*C.d.E*/
    if (servicio == NULL) {
        return -1;
    }

    pid_t pid = 0, sid = 0;

    pid = fork();
    if (pid > 0) {
        exit(EXIT_SUCCESS);
    }
    if (pid < 0) {
        exit(EXIT_FAILURE);
    }



    /*Creamos una nueva sesion y el proceso hijo lidera esta sesion*/
    sid = setsid();
    if (sid < 0) {
        /* Log the failure */
        exit(EXIT_FAILURE);
    }

    /*Cambiar la mascara de modo de ficheros para que sean accesibles
     * a cualquiera*/
    umask((mode_t) 0);

    /*Establezco el directorio raiz como directorio de trabajo*/
    if (chdir("/") < 0) {
        exit(EXIT_FAILURE);
    }

    close(STDIN_FILENO);
    close(STDOUT_FILENO);
    close(STDERR_FILENO);

    /*Abrir log del sistema,
     * 1 param: mensaje
     * 2 param: PID del proceso que lo abre
     * 3 param: tipo de programa que loggea el mensaje
     */

    int fd0 = open("/dev/null",O_RDONLY);


    openlog(servicio, LOG_PID, LOG_DAEMON);
    syslog(LOG_INFO, "Funcion demonizar correcta\n");
    return 0;


}
