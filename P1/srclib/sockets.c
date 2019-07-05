#include "../includes/sockets.h"


/**
* Descripcion: Fichero fuente modulo sockets.
*
* Autores: Pablo Diez del Pozo y Andres Barbero Valentin.
*
* Grupo: 2311
*
*/



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
int inicializa_server(int puerto, int conexiones_max){
    
    int sockval, opt_val = 1;
    struct sockaddr_in servidor;
    
    /*Abrimos el socket del servidor para poder recibir conexiones*/
    sockval = socket(AF_INET,SOCK_STREAM,0);
    if(sockval < 0){
        syslog(LOG_INFO, "Error creando el socket\n");
        exit(EXIT_FAILURE);
    }

    /*Se inicializa la estructura direccion y puerto*/
    servidor.sin_family = AF_INET;
    servidor.sin_port = htons(puerto);
    servidor.sin_addr.s_addr = htonl(INADDR_ANY);

    
   
    
    if (setsockopt(sockval, SOL_SOCKET, SO_REUSEADDR, &opt_val, sizeof opt_val) <0){
        syslog(LOG_INFO, "Error setsockopt\n");
        exit(EXIT_FAILURE);
    }

    
    /*Asociamos la direccion y el puerto*/
    if((bind(sockval,(struct sockaddr *) &servidor,sizeof(servidor)))< 0){
        syslog(LOG_INFO, "Error en bind\n");
        exit(EXIT_FAILURE);
    }

    /*Preparamos el socket para que escuche conexiones, con el numero de puerto
    * y el numero maximo de conexiones*/
    if ((listen(sockval, conexiones_max)) < 0){
        close(sockval);
        syslog(LOG_INFO, "Error en listen\n");
        exit(EXIT_FAILURE);
    }

    fprintf(stdout,"Escuchando en [%s:%d]...\n", inet_ntoa(servidor.sin_addr), ntohs(servidor.sin_port));

    return sockval;
}

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
int aceptar_conexion(int sockval){

    int socket_client;
    struct sockaddr_in client;

    /*Longitud del cliente, para el acept -> Es un entero*/
    socklen_t length = sizeof(client);

    /*Aceptamos la conexion del cliente*/
    socket_client = accept(sockval, (struct sockaddr *) &client, &length);
    if(socket_client < 0){
        syslog(LOG_INFO, "Error en el accept\n");
        exit(1);
    }

    /*Devolvemos el retorno del accept, necesario para el recv de la info. del cliente*/
    return socket_client; 

}
