Autores:
    - Pablo Díez del Pozo
    - Andrés Barbero Valentín
Grupo: 2311

Para ejecutar basta con hacer make y se ejecutará en modo demonio por defecto.

Si se quiere modificar algún parámetro se puede cambiar el puerto, la raíz del 
servidor o el número máximo de clientes en el fichero server.conf.

Al hacer make se crea el directorio lib y el obj incluyendo en ellos sus 
correspondientes *.a y *.o, una vez que se ha compilado es necesario hacer 
make clean antes de volver a compilar.