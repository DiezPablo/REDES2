# Banderas
CC = gcc
CFLAGS = -pedantic -I .
LINK = -lconfuse

# Macros
SERVER = obj/server.o obj/demonizar.o obj/picohttpparser.o
LIBS = lib/libpico.a lib/libsockets.a
LIBPICO = -Llib/ -lpico
LIBSOCK = -Llib/ -lsockets


all: objetos server

# Ejecutable
server:	$(LIBS) $(SERVER)
	$(CC) $^ -o $@ $(LINK) $(LIBPICO) $(LIBSOCK)


# Directorio objetos
objetos:
	mkdir obj
	mkdir lib


# Objetos
obj/server.o: src/server.c includes/server.h includes/demonizar.h
	$(CC) $(CFLAGS) -c -o $@ $< $(LINK)

obj/demonizar.o: srclib/demonizar.c includes/demonizar.h
	$(CC) $(CFLAGS) -c -o $@ $< $(LINK)

obj/sockets.o: srclib/sockets.c includes/sockets.h
	$(CC) $(CFLAGS) -c -o $@ $<

obj/picohttpparser.o: srclib/picohttpparser.c includes/picohttpparser.h
	$(CC) $(CFLAGS) -c -o $@ $<



# Librerias estaticas
lib/libpico.a: obj/picohttpparser.o
	ar -rv $@ $^

lib/libsockets.a: obj/sockets.o
	ar -rv $@ $^




# Limpiar ficheros generados
clean:
	rm -f server
	rm -f *.o
	rm -R lib
	rm -R obj
	rm -f .gitignore
