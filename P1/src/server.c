#include "../includes/server.h"


/**
* Descripcion: Fichero fuente modulo server.
*
* Autores: Pablo Diez del Pozo y Andres Barbero Valentin.
*
* Grupo: 2311
*
*/


int descriptor;

/*Estructura que guarda la peticion*/
typedef struct {
    char verbo[100];
    char ruta_peticion[100];
    int version;
    int tamanio;
    char args_post[128];

} Peticion;

/**
 * Funcion get_date
 *
 * DESCRIPCION:
 *       Funcion que obtiene la fecha actual.
 *
 * INPUT:
 *       fecha: char* cadena de caracteres donde se almacena la fecha obtenida.
 *
 */
void get_date(char *fecha) {
    time_t tiempo = time(0);
    struct tm *t = gmtime(&tiempo);
    strftime(fecha, 128, "%a, %d %b %Y %H:%M:%S %Z", t);
}


/**
 * Funcion print_peticion
 *
 * DESCRIPCION:
 *       Funcion que imprime por pantalla el contenido de la peticion recibida por argumento.
 *
 * INPUT:
 *       p: Peticion* peticion a imprimir por pantalla.
 *
 */
void print_peticion(Peticion *p) {
    if (p == NULL){
        syslog(LOG_INFO, "Error en print_peticion\n");
        return;
    }


    printf("Version: %d.\n", p->version);
    printf("Tamanio: %d.\n", p->tamanio);
    printf("Verbo: %s.\n", p->verbo);
    printf("Path: %s.\n", p->ruta_peticion);
    printf("Argumentos POST: %s.", p->args_post);

}



/**
 * Funcion respuesta_error404
 *
 * DESCRIPCION:
 *       Funcion que genera la respuesta al cliente cuando la peticion es error 404.
 *
 * INPUT:
 *       descriptor: int descriptor del socket abierto.
 *       nombre_servidor: char* nombre del servidor.
 *       version_http: int version HTTP.
 *
 */
void respuesta_error404(int descriptor, char *nombre_servidor, int version_http) {
    char fecha[128];
    char buffer_response[400];
    get_date(fecha);
    sprintf(buffer_response, "HTTP/1.%d 404 Not Found\r\nDate: %s\r\nServer: %s\r\nContent-Length: 80\r\n"
            "Content-Type: text/html\r\n\r\n<html><b>404 Not Found</b></html>", version_http, fecha, nombre_servidor);
    send(descriptor, buffer_response, strlen(buffer_response), 0);
    memset(buffer_response, 0, strlen(buffer_response));

    exit(EXIT_SUCCESS);

    return;

}

/**
 * Funcion respuesta_error400
 *
 * DESCRIPCION:
 *       Funcion que genera la respuesta al cliente cuando la peticion es error 400.
 *
 * INPUT:
 *       descriptor: int descriptor del socket abierto.
 *       nombre_servidor: char* nombre del servidor.
 *       version_http: int version HTTP.
 *
 */
void respuesta_error400(int descriptor, char* nombre_servidor, int version_http) {
    char date[128];
    char buffer_response[400];
    get_date(date);
    sprintf(buffer_response, "HTTP/1.%d 400 Bad Request\r\nDate: %s\r\nServer: %s\r\nContent-Length: 80\r\n"
            "Content-Type: text/html\r\n\r\n<html><b>400 Bad Request</b></html>", version_http, date, nombre_servidor);
    send(descriptor, buffer_response, strlen(buffer_response), 0);
    memset(buffer_response, 0, strlen(buffer_response));

    exit(EXIT_SUCCESS);

    return;
}


/**
 * Funcion comprobar_verbo
 *
 * DESCRIPCION:
 *       Funcion que comprueba si el verbo de una peticion esta soportado.
 *
 * INPUT:
 *       verbo: char* verbo a comprobar.
 *
 * OUTPUT:
 *      0 si es soportado.
 *     -1 si no es soportado.
 */
int comprobar_verbo(char *verbo) {
    if (verbo == NULL) {
        syslog(LOG_INFO, "Error comprobar_verbo\n");
        return -1;
    }
    if (strstr(verbo, "GET") == 0) {
        return 0;
    } else if (strstr(verbo, "POST") == 0) {
        return 0;
    } else if (strstr(verbo, "OPTIONS") == 0) {
        return 0;
    } else{
        return -1;
    }
}


/**
 * Funcion get_content_type
 *
 * DESCRIPCION:
 *       Funcion que obtiene el content-type.
 *
 * INPUT:
 *       path: char* ruta de la peticion.
 *       tipo: char* extension de la respuesta.
 * OUTPUT:
 *      0 si es soportado.
 *     -1 si no es soportado.
 */
int get_content_type(char* path, char* tipo) {

    if (strstr(path, ".txt")) {
        strcpy(tipo, "text/plain");
    } else if (strstr(path, ".html") || strstr(path, ".htm")) {
        strcpy(tipo, "text/html");
    } else if (strstr(path, ".gif")) {
        strcpy(tipo, "image/gif");
    } else if (strstr(path, ".jpeg") || strstr(path, ".jpg")) {
        strcpy(tipo, "image/jpeg");
    } else if (strstr(path, ".mpeg") || strstr(path, ".mpg")) {
        strcpy(tipo, "video/mpeg");
    } else if (strstr(path, ".doc") || strstr(path, ".docx")) {
        strcpy(tipo, "application/msword");
    } else if (strstr(path, ".pdf")) {
        strcpy(tipo, "application/pdf");
    } else {
        /*Caso error 400*/
        return -1;
    }

    return 0;

}


/**
 * Funcion get_content_lenght
 *
 * DESCRIPCION:
 *       Funcion que obtiene el content_length del fichero que queremos mandar.
 *
 * INPUT:
 *       path_to_file: char* ruta del fichero.
 *
 * OUTPUT:
 *      tamanyo del fichero que queremos mandar.
 */
long get_content_lenght(char* path_to_file) {
    struct stat s;
    long size;
    stat(path_to_file, &s);
    size = s.st_size;

    return size;
}


/**
 * Funcion options
 *
 * DESCRIPCION:
 *       Funcion que genera la respuesta a una peticion cuando el verbo es OPTIONS.
 *
 * INPUT:
 *       descriptor: int descriptor del socket abierto.
 *       nombre_servidor: char* nombre del servidor.
 *       version_http: int version HTTP.
 *
 */
void options(int descriptor, char* nombre_servidor, int version_http) {
    char date[128];
    char buffer_response[400];
    get_date(date);
    sprintf(buffer_response, "HTTP/1.%d 200 OK\r\nDate: %s\r\nServer: %s\r\nContent-Length: 0\r\nAllow: GET, POST, OPTIONS\r\n", version_http, date, nombre_servidor);
    send(descriptor, buffer_response, strlen(buffer_response), 0);
    memset(buffer_response, 0, strlen(buffer_response));

    exit(EXIT_SUCCESS);

    return;
}


/**
 * Funcion respuesta
 *
 * DESCRIPCION:
 *       Funcion que genera la respuesta de una peticion.
 *
 * INPUT:
 *       descriptor: int descriptor del socket abierto.
 *       ruta_servidor: char* ruta del servidor.
 *       server_signature: char* firma del servidor.
 *       server_root: char* ruta raiz del servidor.
 *       peticion: Peticion* peticion recibida.
 *
 */
void respuesta(int descriptor, char *ruta_servidor, char *server_signature, char *server_root, Peticion *peticion) {

    /*Variables necesarias para parsear la respuesta del servidor GET*/
    FILE* fichero;
    char extension_respuesta[30];
    char fecha_respuesta[128];
    char args[128];
    char fecha_ultima_modificacion[128];
    long tam_fichero;
    char buffer_response[8192];
    char ruta_fichero_solicitud[1000];
    char ruta_final[100];
    int ret;
    int file;
    char delim[] = "?";
    char *ptr, *argumentos;
    char script[200];
    FILE *salida_script;
    char resultado_script[512];


    /*Respuesta OPTIONS*/
    if(strstr(peticion->verbo,"OPTIONS")){
        options(descriptor,server_signature,peticion->version);
        exit(EXIT_SUCCESS);
    }
    
    /*Respuesta POST*/
    if (strstr(peticion->verbo, "POST") && !(strstr(peticion->ruta_peticion, "?"))) {
        sprintf(ruta_fichero_solicitud, "%s%s%s", ruta_servidor, server_root, peticion->ruta_peticion);
        if (strstr(ruta_fichero_solicitud, ".py")) {
            sprintf(script, "echo %s | python %s", peticion->args_post, ruta_fichero_solicitud);
        } else {
            sprintf(script, "echo %s | php %s", peticion->args_post, ruta_fichero_solicitud);
        }

        salida_script = popen(script, "r");
        if (salida_script == NULL) {
            syslog(LOG_INFO, "Error en popen en respuesta POST\n");
            respuesta_error404(descriptor, server_signature, peticion->version);
            close(descriptor);
        }

        /*Leemos el fichero en el que se ha escrito el resultado de ejecutar el mandato python*/
        tam_fichero = fread(resultado_script, 1, 512, salida_script);

        /*Rellenamos la respuesta del servidor*/
        /*Fecha de la respuesta*/
        get_date(fecha_respuesta);

        /*Last-modified*/
        struct stat s;
        stat(ruta_fichero_solicitud, &s);

        /*Construimos la respuesta*/
        strftime(fecha_ultima_modificacion, 128, "%a, %d %b %Y %H:%M:%S %Z", gmtime(&s.st_mtime));
        sprintf(buffer_response, "HTTP/1.%d 200 OK\r\nDate: %s\r\nServer: %s\r\nContent-Length: %ld\r\nLast-Modified: %s\r\nContent-Type: text/html\r\n\r\n%s\r\n",
                peticion->version, fecha_respuesta, server_signature, tam_fichero, fecha_ultima_modificacion, resultado_script);

        send(descriptor, buffer_response, strlen(buffer_response), 0);

        pclose(salida_script);

    }

    /*Argumentos POST y argumentos en la URL.*/
    if (strstr(peticion->verbo, "POST") && (strstr(peticion->ruta_peticion, "?"))) {
        ptr = strtok(peticion->ruta_peticion, delim);
        strcpy(ruta_final, ptr);
        argumentos = strtok(NULL, delim);
        strcpy(args, argumentos);
        sprintf(ruta_fichero_solicitud, "%s%s%s", ruta_servidor, server_root, ruta_final);

        if (strstr(ruta_fichero_solicitud, ".py")) {
            sprintf(script, "echo %s | python %s %s", peticion->args_post, ruta_fichero_solicitud, args);
        } else {
            sprintf(script, "echo %s | php %s %s", peticion->args_post, ruta_fichero_solicitud, args);
        }

        salida_script = popen(script, "r");
        if (salida_script == NULL) {
            syslog(LOG_INFO, "Error en popen en respuesta GET/POST\n");
            respuesta_error404(descriptor, server_signature, peticion->version);
            close(descriptor);
        }

        /*Leemos el fichero en el que se ha escrito el resultado de ejecutar el mandato python*/
        tam_fichero = fread(resultado_script, 1, 512, salida_script);

        /*Rellenamos la respuesta*/
        get_date(fecha_respuesta);

        /*Last-modified*/
        struct stat s;
        stat(ruta_fichero_solicitud, &s);
        strftime(fecha_ultima_modificacion, 128, "%a, %d %b %Y %H:%M:%S %Z", gmtime(&s.st_mtime));
        sprintf(buffer_response, "HTTP/1.%d 200 OK\r\nDate: %s\r\nServer: %s\r\nContent-Length: %ld\r\nLast-Modified: %s\r\nContent-Type: text/html\r\n\r\n%s\r\n",
                peticion->version, fecha_respuesta, server_signature, tam_fichero, fecha_ultima_modificacion, resultado_script);
        send(descriptor, buffer_response, strlen(buffer_response), 0);


        pclose(salida_script);

    }

    /*Caso GET con argumentos en la URL.*/
    if (strstr(peticion->ruta_peticion, "?")) {
        /*Captura de la url pedida y los argumentos*/
        ptr = strtok(peticion->ruta_peticion, delim);
        strcpy(ruta_final, ptr);
        argumentos = strtok(NULL, delim);
        strcpy(args, argumentos);
        sprintf(ruta_fichero_solicitud, "%s%s%s", ruta_servidor, server_root, ruta_final);

        /*Ejecucion del script*/
        if (strstr(ruta_fichero_solicitud, ".py")) {
            sprintf(script, "python %s \"%s\"", ruta_fichero_solicitud, args);
        } else if (strstr(ruta_fichero_solicitud, ".php")) {
            sprintf(script, "php %s \"%s\"", ruta_fichero_solicitud, args);
        }
        salida_script = popen(script, "r");
        if (salida_script == NULL) {
            syslog(LOG_INFO, "Error en popen en respuesta GET\n");
            respuesta_error404(descriptor, server_signature, peticion->version);
            close(descriptor);
        }

        /*Leemos el fichero en el que se ha escrito el resultado de ejecutar el mandato python*/
        tam_fichero = fread(resultado_script, 1, 512, salida_script);

        /*Rellenamos la respuesta*/
        get_date(fecha_respuesta);

        /*Last-modified*/
        struct stat s;
        stat(ruta_fichero_solicitud, &s);
        strftime(fecha_ultima_modificacion, 128, "%a, %d %b %Y %H:%M:%S %Z", gmtime(&s.st_mtime));
        sprintf(buffer_response, "HTTP/1.%d 200 OK\r\nDate: %s\r\nServer: %s\r\nContent-Length: %ld\r\nLast-Modified: %s\r\nContent-Type: text/html\r\n\r\n%s\r\n",
                peticion->version, fecha_respuesta, server_signature, tam_fichero, fecha_ultima_modificacion, resultado_script);
        send(descriptor, buffer_response, strlen(buffer_response), 0);


        pclose(salida_script);

        /*Caso GET sin argumentos*/
    } else {
        sprintf(ruta_fichero_solicitud, "%s%s%s", ruta_servidor, server_root, peticion->ruta_peticion);

        /*Comprobamos la version del fichero*/
        /*Comprobacion fichero solicitado se encuentra en el servidor.*/
        fichero = fopen(ruta_fichero_solicitud, "r");
        if (fichero == NULL) {
            syslog(LOG_INFO, "Error en fopen en respuesta GET sin argumentos\n");
            respuesta_error404(descriptor, server_signature, peticion->version);
            close(descriptor);
        }

        /*Comprobamos la extension*/
        if (get_content_type(peticion->ruta_peticion, extension_respuesta) == -1){
            syslog(LOG_INFO, "Error, content-type no soportado\n");
            respuesta_error400(descriptor, server_signature, peticion->version);
            close(descriptor);
        }

        if (extension_respuesta == NULL) {
            syslog(LOG_INFO, "Error, extension no soportada\n");
            respuesta_error400(descriptor, server_signature, peticion->version);
            close(descriptor);
        }

        /*Date*/
        get_date(fecha_respuesta);

        /*Last-modified*/
        struct stat s;
        stat(ruta_fichero_solicitud, &s);
        strftime(fecha_ultima_modificacion, 128, "%a, %d %b %Y %H:%M:%S %Z", gmtime(&s.st_mtime));

        /*Content-Length*/
        tam_fichero = get_content_lenght(ruta_fichero_solicitud);

        /*Mandamos la cabecera de la respuesta*/
        sprintf(buffer_response, "HTTP/1.%d 200 OK\r\nDate: %s\r\nServer: %s\r\nContent-Length: %ld\r\nLast-Modified: %s\r\nContent-Type: %s\r\n\r\n",
                peticion->version, fecha_respuesta, server_signature, tam_fichero, fecha_ultima_modificacion, extension_respuesta);
        send(descriptor, buffer_response, strlen(buffer_response), 0);

        /*Primero se manda la cabecera, despues el contenido*/
        file = open(ruta_fichero_solicitud, O_RDONLY);
        while ((ret = read(file, buffer_response, 8192)) > 0) {

            send(descriptor, buffer_response, ret, 0);
        }
    }

    exit(EXIT_SUCCESS);

}


/**
 * Funcion parsea_peticion
 *
 * DESCRIPCION:
 *       Funcion que parsea la peticion recibida y genera la respuesta correspondiente.
 *
 * INPUT:
 *       descriptor: int descriptor del socket abierto.
 *       ruta_servidor: char* ruta del servidor.
 *       server_signature: char* firma del servidor.
 *       server_root: char* ruta raiz del servidor.
 *
 * OUTPUT:
 *       dirección de memoria a la peticion.
 */
Peticion* parsea_peticion(int descriptor, char *ruta_servidor, char *server_signature, char *server_root) {
    char buf[4096], *method, *path;
    char info[8192];


    int pret, minor_version;
    size_t buflen = 0, prevbuflen = 0, method_len, path_len;
    ssize_t rret;
    struct phr_header headers[100];
    size_t num_headers;
    Peticion *p;

    p = (Peticion*) calloc(1, sizeof (Peticion));
    if (p == NULL) {
        return NULL;
    }

    while (1) {
        while ((rret = read(descriptor, buf + buflen, sizeof (buf) - buflen)) == -1 && errno == EINTR)
            ;
        if (rret <= 0)
            return NULL;

        prevbuflen = buflen;
        buflen += rret;

        /* parse the request */
        num_headers = sizeof (headers) / sizeof (headers[0]);

        /*Parseo de la peticion*/
        pret = phr_parse_request(buf, buflen, (const char**) &method, &method_len, (const char**) &path, &path_len,
                &minor_version, headers, &num_headers, prevbuflen);

        if (pret > 0)
            break; /* successfully parsed the request */

        else if (pret == -1)
            return NULL;

        /* request is incomplete, continue the loop */
        assert(pret == -2);

        if (buflen == sizeof (buf))
            return NULL;
    }

    /*Guardamos los datos en la estructura*/
    p->version = minor_version;
    p->tamanio = pret;

    /*Guardamos la ruta*/
    sprintf(info, "%.*s", (int) path_len, path);
    strcpy(p->ruta_peticion, info);

    memset(info, 0, strlen(info));

    /*Guardamos el verbo*/
    sprintf(info, "%.*s", (int) method_len, method);
    strcpy(p->verbo, info);

    /*Argumentos POST*/
    if (strstr(p->verbo, "POST")) {
        sprintf(info, "%s", buf + pret);
        strcpy(p->args_post, info);
        printf("Argumentos POST: %s\n", p->args_post);
    }

    /*Reseteamos el array en que vamos guardando la informacion*/
    memset(info, 0, strlen(info));

    /*Comprobamos la version HTTP*/
    if ((p->version != 0) && (p->version != 1)) {
        syslog(LOG_INFO, "Error version HTTP incompatible\n");
        respuesta_error400(descriptor, server_signature, p->version);
        close(descriptor);
    }

    /*Comprobamos si el verbo es soportado. Si no, respuesta 400*/
    if (comprobar_verbo(p->verbo) == -1) {
        syslog(LOG_INFO, "Error, el verbo no esta soportado\n");
        respuesta_error400(descriptor, server_signature, p->version);
        close(descriptor);
    }

    /*Llamamos a la funcion respuesta que responde a la peticion*/
    respuesta(descriptor, ruta_servidor, server_signature, server_root, p);

    return p;
}

int main() {

    int sockval;
    int i, count = 0;

    /*Variables de confuse*/
    char* server_root = NULL, *server_signature = NULL, *server = NULL;
    long int max_clients = 1, listen_port = 1;

    /*Variables para el parseo*/
    Peticion *peticion;
    char ruta_servidor[200];
    FILE *fichero;

    int pid;
    /*Configuracion del servidor*/
    cfg_opt_t opts[] = {
        CFG_SIMPLE_STR("server_root", &server_root),
        CFG_SIMPLE_INT("max_clients", &max_clients),
        CFG_SIMPLE_INT("listen_port", &listen_port),
        CFG_SIMPLE_STR("server_signature", &server_signature),
        CFG_END()
    };
    cfg_t* cfg;

    cfg = cfg_init(opts, 0);
    cfg_parse(cfg, "servidor.conf");



    /*Ruta servidor absoluta*/
    getcwd(ruta_servidor, sizeof (ruta_servidor));

    /*Ponemos al servidor a la espera de peticiones*/
    sockval = inicializa_server(listen_port, max_clients);
    if (sockval == -1) {
        syslog(LOG_INFO, "Error al inicializar servidor\n");
        exit(EXIT_FAILURE);
    }

    /*Demonizar*/
    if(demonizar("Redes2 - Servidor Web") == -1){
        syslog(LOG_INFO, "Error al demonizar\n");
        exit(EXIT_FAILURE);
    }

    /*Procesado de las peticiones*/
    while (1) {
        /*Aceptamos conexiones al servidor*/
        descriptor = aceptar_conexion(sockval);
        if (descriptor == -1) {
            syslog(LOG_INFO, "Error al aceptar conexion\n");
            exit(EXIT_FAILURE);
        }

        count++;

        if ((pid = fork()) == 0) {
            peticion = parsea_peticion(descriptor, ruta_servidor, server_signature, server_root);
            if (peticion == NULL) {
                syslog(LOG_INFO, "Error al parsear la peticion\n");
                exit(EXIT_FAILURE);
            }
            close(descriptor);
            //free(peticion);
        } else if (pid < 0) {
            exit(EXIT_FAILURE);
        }else{
            close(descriptor);
            free(peticion);

            /*Para evitar procesos zombies*/
            for (i = 0; i < count; i++){
                wait(&pid);
            }
        }
    }


    fclose(fichero);
    exit(EXIT_SUCCESS);
    return 0;
}
