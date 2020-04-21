import socket
import threading


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

#message info
COMMAND = 0
ARGUMENT = 1
SOCKET  = 0
STATUS  = 1
INVITED = 2

#return codes
OK          = 'OK: '
NOT_OK      = 'ERROR: '

#return sub-codes
REG_OK      = 'client successfully registered'
REG_UPDATED = 'client registration updated'
REG_NOT_OK  = 'client unsuccessfully registered'
INV_CLIENT  = 'client is not registered' # invalid client
INV_SESSION = 'client has no user_infos session'  #no user_infos session for the client"
INV_MSG     = 'invalid message type'
REG_USED    = 'client with that name already exists'
HAS_SESSION = 'you already have a session, '
EXIT        = 'you have ended your session'
NOTHING     = 'has done nothing'
NO_USER     = 'No user with that name!'
ACK         = 'Your message has been delivered'
FREE        = 'free'
BUSY        = 'busy'
PLAYING     = 'playing'
ACCEPT      = 'you are in a game now!'
ACCEPTED    = 'you are in a game now!'
DECLINE     = 'you declined the game invite'
DECLINED    = 'the player declined your invite'
#GAME        = 'game has started'

#generic functions

def find_addr (addr): # pede addr
    for key, val in list(user_infos.items()):
        if val[SOCKET] == addr:
            return key
    return NULL

def find_name(name): # pede name
    for key, val in list(user_infos.items()):
        if key == name:
            return user_infos[name][SOCKET]
    return NULL


def register_client(msg_request, client_socket):
    name = msg_request[ARGUMENT]
    msg_reply = NOT_OK + NOTHING + "\n"
    client_name = find_addr(client_socket)

    if (client_name != NULL):
        msg_reply = NOT_OK + HAS_SESSION + client_name + "\n"
    elif name in user_infos: 
        msg_reply = NOT_OK + REG_USED + "\n"
    else:
        user_infos[name] = [client_socket, FREE, NULL]
        msg_reply = OK + REG_OK + "\n"

    return msg_reply


def reply_hello(client_socket):
    msg_reply = NOT_OK + INV_CLIENT + "\n"
    dst_name = find_addr(client_socket)

    if dst_name != NULL:
        msg_reply = 'HELLO' + ' ' + dst_name + "\n"

    return msg_reply


def forward_hello(msg_request, client_socket):
    dst_name = msg_request[ARGUMENT]
    dst_addr = find_name(dst_name)
    msg_reply = NOT_OK + INV_SESSION + "\n"
    src_name =  find_addr(client_socket)

    if src_name == NULL:
        msg_reply = NOT_OK + INV_SESSION
    elif dst_addr == NULL:
        msg_reply = NO_USER + "\n"
    else:
        msg_reply = OK + ACK + "\n"
        server_reply = 'HELLO'   + ' ' + dst_name + ' from ' + src_name + "\n"
        server_reply = server_reply.encode()
        dst_addr.send(server_reply)

    return msg_reply


def show_status(client_socket):
    msg_reply = OK + '\n'
    for key, val in list(user_infos.items()): #fazer funcao
        if user_infos[key][STATUS] == FREE:
            msg_reply += key + ': free\n'
    for key, val in list(user_infos.items()): #fazer funcao
        if user_infos[key][STATUS] == BUSY:
            msg_reply += key + ': busy\n'
    for key, val in list(user_infos.items()): #fazer funcao
        if user_infos[key][STATUS] == PLAYING:
            msg_reply += key + ': playing\n'
    return msg_reply


def invite(msg_request, client_socket):
    dst_name = msg_request[ARGUMENT]
    user_infos[dst_name][STATUS] = BUSY
    invited_socket = find_name(dst_name)
    src_name = find_addr(client_socket)
    user_infos[dst_name][INVITED] = src_name
    user_infos[src_name][STATUS] = BUSY
    server_reply = " You have been invited to a game by: " + src_name + ". (Y/n)"
    server_reply = server_reply.encode() #fazer uma funcao auxiliar que faz estas 2 linhas depois
    invited_socket.send(server_reply)
    msg_reply = OK + ACK + '\n'

    return msg_reply


def update_user_infos(accepted, client_socket):
    src_name = find_addr(client_socket)
    dst_addr = find_name(user_infos[src_name][INVITED])
    dst_name = find_addr(dst_addr)
    print(dst_name)
    print(accepted)
    if accepted == "Y":
        user_infos[src_name][STATUS] = PLAYING # mudar todos if else para este formato?
        user_infos[dst_name][STATUS] = PLAYING
        msg_reply = OK + ACCEPT
        server_reply = OK + ACCEPTED
    else:
        user_infos[src_name][STATUS] = FREE
        user_infos[dst_name][STATUS] = FREE
        msg_reply = OK + DECLINE
        server_reply = OK + DECLINED
    server_reply = server_reply.encode()
    dst_addr.send(server_reply)
    return msg_reply

def invalid_msg(msg_request):
  respond_msg = "INVALID MESSAGE\n"
  msg_reply = NOT_OK + msg_request[COMMAND] + ' ' + INV_MSG + "\n"
  return msg_reply


def exit_session(client_socket):
    name = find_addr(client_socket)
    del user_infos[name]
    return EXIT.encode()


def server_function(client_socket):
    while True:
        client_msg = client_socket.recv(MSG_SIZE)
        print(client_msg.decode())
        msg_request = client_msg.decode().split()
        command = msg_request[COMMAND]
        if(command == "IAM"): # se command 2 for NULL breaka
            server_msg = register_client(msg_request, client_socket)
        elif(command == "HELLO"):
            server_msg = reply_hello(client_socket)
        elif(command == "HELLOTO"):
            server_msg = forward_hello(msg_request, client_socket)
        elif(command == "LIST"):
            server_msg = show_status(client_socket)
        elif(command == "INVITE"):
            server_msg = invite(msg_request, client_socket)
        elif(command.upper() == "Y" or command.upper() == "N"):
            client_name = find_addr(client_socket)
            if user_infos[client_name][STATUS] == BUSY:
                server_msg = update_user_infos(command.upper(), client_socket)
        elif(command == "EXIT"):
            server_msg = exit_session(client_socket)
            server_msg = msg_reply.encode()
            client_socket.send(server_msg)
            break
        else:
            server_msg = invalid_msg(msg_request)
        #server_sock.sendto(server_msg, (client_addr, SERVER_PORT))
        server_msg = server_msg.encode()
        client_socket.send(server_msg)
    client_socket.close()


#main code
threads = []
user_infos = {} #dict: key: user_name; val:user_address info: example:'maria'= ('127.0.0.1',17234)

# programa inicial, nao e thread
server_sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # para depois poder matar com ctrl+c
server_sock.bind(('', SERVER_PORT))
server_sock.listen(5)


while True:
    client_sock, client_addr = server_sock.accept()
    cliente = threading.Thread(target=server_function, args = (client_sock,))
    threads.append(cliente)
    cliente.start()
