import socket
import threading
import sys
import random
from functions import *

#############################################
#              AVAILABLE COMMANDS           # 
# REGISTER <name>                           #
# LIST                                      #
# INVITE <name>                             #
# Y / N                                     #           
# PLACE <p>                                 #
# EXIT                                      #
# HELP                                      #
# ###########################################



# Recebe no porto SERVER PORT os comandos "IAM <nome>", "HELLO",
#    "HELLOTO <nome>" ou "KILLSERVER"
# "IAM <nome>" - regista um cliente como <nome>
# "HELLO" - responde HELLO <nome> se o cliente estiver registado
# "HELLOTO <nome>" - envia HELLO para o cliente <nome>
# "KILLSERVER" - mata o servidor

#constants definition
NULL = ''
#sockets communication parameters
SERVER_PORT = 12100
MSG_SIZE = 1024
NUMBER_OF_POSITIONS = 3
MAX_TURNS = 9

#message info
COMMAND  = 0
ARGUMENT = 1

#return codes
OK          = 'OK: '
NOT_OK      = 'ERROR: '

#return sub-codes
INV_MSG     = 'invalid message type'




def server_function(client_socket):
    # meter aqui variaveis tipo nome, que devem ser locais
    client_name = NULL
    while True:
        client_msg = client_socket.recv(MSG_SIZE)
        msg_request = client_msg.decode().split()
        try:
            command = msg_request[COMMAND]
        except IndexError:
            server_msg = NOT_OK + INV_MSG + '\n'
        else:
            lock.acquire()
            if command == "LIST":
                server_msg = show_status(client_socket)

            elif command == "EXIT": 
                server_msg = exit_session(client_socket)
                fast_send(server_msg, client_socket)
                lock.release()
                break

            elif command == "Y" or command == "N": # mudou para SO com maiusculas
                server_msg = update_user_infos(command, client_socket, client_name)

            elif command in ["INVITE", "PLACE", "IAM"]: # nao gosto muito
                try:
                    arg = msg_request[ARGUMENT]
                except IndexError:
                    server_msg = NOT_OK + USE_ARG

                else:
                    if command == "INVITE":
                        server_msg = invite(arg, client_socket, client_name)

                    elif command == "PLACE":
                        server_msg = play_space(arg, client_socket, client_name)

                    elif command == "IAM":
                        server_msg = register_client(msg_request, client_socket)
                        client_name = find_addr(client_socket)

            else:
                server_msg = invalid_msg(msg_request)

        lock.release()
        fast_send(server_msg, client_socket)
    client_socket.close()
    sys.exit(0)


#main code
threads = []
user_infos = {} #dict: key: user_name; val:user_address info: example:'maria'= ('127.0.0.1',17234)

# programa inicial, nao e thread
server_sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # para depois poder matar com ctrl+c
server_sock.bind(('', SERVER_PORT))
server_sock.listen(5)
lock = threading.Lock()

while True:
    client_sock, client_addr = server_sock.accept()
    cliente = threading.Thread(target=server_function, args=(client_sock,))
    threads.append(cliente)
    cliente.start()


# jogos guardados numa lista, jogo guarda os players e os seus simbolos, 
# podes fazer quit para voltar para o cmd, SHOWGAMES e ENTER NUM pa voltar
